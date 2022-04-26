import glob
import json
import random

import mo_parsing.exceptions
import mo_sql_parsing
import pandas as pd

from app.backend.processing.process_query.clause_extractors import \
    find_from_tables


def clean_empty_annotations(datapoints):
    def is_empty_annot(annot):
        if len(annot['result']) == 0:
            return True
        else:
            return False

    for datapoint in datapoints:
        datapoint['annotations'] = [annot for annot in datapoint['annotations'] if not is_empty_annot(annot)]

    ret_datapoints = [datapoint for datapoint in datapoints if len(datapoint['annotations']) > 0]

    return ret_datapoints


def read_all_annotations(annotations_dir):
    annotations = []
    for annotation_file in glob.glob(annotations_dir + "*"):
        with open(annotation_file) as json_file:
            annotations.extend(json.load(json_file))
    annotations = clean_empty_annotations(annotations)

    annotation_dict = {}
    for annotation in annotations:
        annot_id = annotation['data']['id']
        if annot_id in annotation_dict:
            annotation_dict[annot_id]['annotations'].append(annotation['annotations'][-1])
        else:
            annotation_dict[annot_id] = annotation
            annotation_dict[annot_id]['annotations'] = [annotation_dict[annot_id]['annotations'][-1]]

    joined_annotations = list(annotation_dict.values())
    return joined_annotations


def create_splits(annotations, train_percentage=0.8):
    # Order the annotations by number of annotations for each datapoint
    # This way we can make sure that our evaluation dataset will have multiple annotations per datapoint
    ordered_annotations = sorted(annotations, key=lambda annot: len(annot['annotations']))

    train_split = ordered_annotations[:int(len(ordered_annotations) * train_percentage)]
    eval_split = ordered_annotations[int(len(ordered_annotations) * train_percentage):]

    for train_point in train_split:
        train_point['annotations'] = [train_point['annotations'][-1]]
    random.shuffle(train_split)
    random.shuffle(eval_split)

    return train_split, eval_split


def query_result_to_str(query_res):
    query_res = {col_name: [val] for col_name, val in query_res.items()}
    res_df = pd.DataFrame.from_dict(query_res)
    return res_df.to_csv()


def get_table_names(original_query):
    try:
        original_query = original_query.replace('DESC0', '')
        query = mo_sql_parsing.parse(original_query)
    except mo_parsing.exceptions.ParseException:
        print(original_query)
        raise mo_parsing.exceptions.ParseException
    return ', '.join(find_from_tables(query['from']))


def create_wiki_sql_datapoint(qr2t_datapoint):
    table_names = get_table_names(qr2t_datapoint['data']['original_query'])
    # print(qr2t_datapoint['annotations'])
    return {
        "table_id": table_names,
        "query": qr2t_datapoint['data']['transformed_query'],
        "table_name": table_names,
        "query_description": qr2t_datapoint['data']['nl_query'],
        "results_description": [annot['result'][-1]['value']['text'][-1] for annot in qr2t_datapoint['annotations']],
        "result": query_result_to_str(qr2t_datapoint['data']['res']),
        "difficulty": qr2t_datapoint['data']['category']
    }


def flatten_target_text(datapoints):
    for datapoint in datapoints:
        datapoint['results_description'] = datapoint['results_description'][0]


def qr2t_to_wikisql(datapoints, store_path, flatten_target=False):
    final_datapoints = [create_wiki_sql_datapoint(datapoint) for datapoint in datapoints]

    if flatten_target:
        flatten_target_text(final_datapoints)

    with open(store_path, 'w') as outfile:
        json.dump(final_datapoints, outfile)


if __name__ == '__main__':
    ANNOTATIONS_DIR = 'storage/datasets/spider/annotations/label_studio/exports/04_18_2022__15_07_53/'
    TARGET_DIR = 'storage/datasets/qr2t_benchmark/'

    annots = read_all_annotations(ANNOTATIONS_DIR)

    train_split, eval_split = create_splits(annots)

    qr2t_to_wikisql(train_split, TARGET_DIR + 'train.json', flatten_target=True)
    qr2t_to_wikisql(eval_split, TARGET_DIR + 'dev.json', flatten_target=True)
    qr2t_to_wikisql(eval_split, TARGET_DIR + 'eval.json', flatten_target=False)
