import json
import random
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from mo_parsing.exceptions import ParseException
from tqdm import tqdm

from data.annotation_qr2t import query_categorization
from data.annotation_qr2t.annotator_split import (assign_annotators,
                                                  confirm_overlap)
from data.annotation_qr2t.filter_queries import filter_benchmark
from data.annotation_qr2t.spider_db_query import create_transformed_benchmark
from utils.query_pattern_recognition import ExtractException, QueryInfo
from dare_datasets import QR2TBenchmark


def categorize_spider(spider_datapoints):
    categories = [
        ["small_select", query_categorization.is_small_select],
        ["large_select", query_categorization.is_large_select],
        ["aggregate", query_categorization.is_aggregates],
        ["aggregate_group_by", query_categorization.is_aggregates_and_group_by],
        ["join", query_categorization.is_join],
        ["join_aggregate", query_categorization.is_join_and_aggregate]
    ]

    def find_category(query_info):
        for category, cond in categories:
            if cond(query_info):
                return category
        return None

    datapoints_with_category = []
    for datapoint in tqdm(spider_datapoints):
        try:
            cat = find_category(QueryInfo(datapoint['query']))
        except (ExtractException, ParseException):
            continue
        if cat is not None:
            datapoint['category'] = cat
            datapoints_with_category.append(datapoint)

    return datapoints_with_category


def create_benchmark_annotations():
    metric = 'PARENT'
    qr2t_benchmark = QR2TBenchmark().get_raw()
    inferences = pd.read_csv('/home/mikexydas/Downloads/pre_totto_qr2t.csv')

    query_datapoints = {
        datapoint['query_description']: datapoint
        for split in ['train', 'dev', 'eval']
        for datapoint in qr2t_benchmark[split]
    }
    score_per_difficulty = defaultdict(list)

    for _, inf in inferences.iterrows():
        nl_query = inf['Source'].split(' <table')[0].replace('<query> ', '')
        diff = query_datapoints[nl_query]['difficulty']
        score_per_difficulty[diff].append(inf[metric])

    avg_metrics = {
        diff: sum(scores) / len(scores)
        for diff, scores in score_per_difficulty.items()
    }
    print(avg_metrics)
    # difficulties = [
    #     datapoint['difficulty']
    #     for split in ['train', 'dev', 'eval']
    #     for datapoint in qr2t_benchmark[split]
    # ]
    # print(Counter(difficulties))

    # return categorize_spider(train_datapoints)
    # filtered_datapoints = filter_benchmark(categorized_datapoints)
    # benchmark_datapoints, final_populations = sample_queries(populations, filtered_datapoints)
    # transformed_benchmark = create_transformed_benchmark(benchmark_datapoints, DB_DIR)
    # benchmark_per_annotator = assign_annotators(transformed_benchmark, annotators, overlap_ratio)
    #
    # print("Benchmark creation finished:")
    # for cat, pop in final_populations.items():
    #     print(f"{cat}: {pop}")
    #
    # class NpEncoder(json.JSONEncoder):
    #     """ Needed to encode dictionary fields with numpy types """
    #     def default(self, obj):
    #         if isinstance(obj, np.integer):
    #             return int(obj)
    #         if isinstance(obj, np.floating):
    #             return float(obj)
    #         if isinstance(obj, np.ndarray):
    #             return obj.tolist()
    #         return super(NpEncoder, self).default(obj)
    #
    # for annotator, benchmark in benchmark_per_annotator.items():
    #     with open(OUTPUT_DIR + annotator + '.json', 'w') as outfile:
    #         json.dump(benchmark, outfile, cls=NpEncoder)
    # # with open(OUTPUT_DIR + 'annotations_sel_aggregate.json', 'w') as outfile:
    # #     json.dump(transformed_benchmark, outfile, cls=NpEncoder)
    # print(">>> Overlaps:")
    # print(confirm_overlap(benchmark_per_annotator))


if __name__ == '__main__':
    create_benchmark_annotations()
