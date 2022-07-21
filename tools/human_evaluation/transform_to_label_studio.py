import glob
import json
import random
from collections import defaultdict

from visualizing.totto_table_parse import parse_totto_format


def parse_evaluation_point(datapoint):
    extracted_info = parse_totto_format(datapoint)
    results_table = {col: value for col, value in zip(extracted_info['columns'], extracted_info['cell_values'])}

    return {
        'table_title': extracted_info['title'],
        'nl_query': extracted_info['query'],
        'results_table': results_table
    }


def create_evaluation_points_from_file(file_path):
    with open(file_path) as f:
        datapoints = json.load(f)['data']
    model_name = file_path.split('/')[-1][:-5]

    evaluation_points = []
    for datapoint in datapoints:
        evaluation_point = parse_evaluation_point(datapoint[6])
        evaluation_point['model'] = model_name
        evaluation_point['inference'] = datapoint[0]
        evaluation_points.append(evaluation_point)

    return evaluation_points


def appoint_annotators(evaluation_points, annotators):
    evaluations_per_annotator = defaultdict(list)

    for evaluation in evaluation_points:
        chosen_annotator = random.choice(annotators)
        evaluations_per_annotator[chosen_annotator].append(evaluation)

    return evaluations_per_annotator


def from_inference_to_evaluation_points(inferences_dir, evaluations_dir, annotators):
    all_evaluation_points = []
    for file in glob.glob(inferences_dir + "*"):
        all_evaluation_points.extend(create_evaluation_points_from_file(file))

    evaluations_per_annotator = appoint_annotators(all_evaluation_points, annotators)

    for key, evaluations in evaluations_per_annotator.items():
        random.shuffle(evaluations)
        with open(f"{evaluations_dir}{key}.json", 'w') as f:
            json.dump(evaluations, f)


if __name__ == '__main__':
    INFERENCES_DIR = 'storage/results/human_evaluation/qr2t/all_inferences/'
    EVALUATIONS_DIR = 'storage/results/human_evaluation/qr2t/per_annotator/'
    ANNOTATORS = ['Mike', 'Katerina', 'Anna', 'Dimitris', 'Stavroula', 'George', 'Chris', 'Antonis']

    from_inference_to_evaluation_points(INFERENCES_DIR, EVALUATIONS_DIR, ANNOTATORS)
