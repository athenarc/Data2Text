import json
import random

import numpy as np
from mo_parsing.exceptions import ParseException
from tqdm import tqdm

from data.annotation import query_categorization
from data.annotation.annotator_split import assign_annotators
from data.annotation.filter_queries import filter_benchmark
from data.annotation.spider_db_query import create_transformed_benchmark
from utils.query_pattern_recognition import ExtractException, QueryInfo


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


def sample_queries(category_populations, categorized_spider):
    random.shuffle(categorized_spider)

    total_gathered = {cat: 0 for cat, _ in category_populations.items()}
    final_queries = []
    for datapoint in tqdm(categorized_spider):
        if total_gathered[datapoint['category']] >= category_populations[datapoint['category']]:
            continue
        final_queries.append(datapoint)
        total_gathered[datapoint['category']] += 1

    return final_queries, total_gathered


def create_benchmark_annotations():
    SPIDER_TRAIN_PATH = "storage/datasets/spider/original/train_spider.json"
    DB_DIR = "storage/datasets/spider/original/database/"
    OUTPUT_DIR = "storage/datasets/spider/annotations/label_studio/"

    populations = {
        "small_select": 500,
        "large_select": 150,
        "aggregate": 400,
        "aggregate_group_by": 250,
        "join": 350,
        "join_aggregate": 350
    }

    # populations = {
    #     "small_select": 3000,
    #     "large_select": 3000,
    #     "aggregate": 3000,
    #     "aggregate_group_by": 3000,
    #     "join": 3000,
    #     "join_aggregate": 3000
    # }

    annotators = [
        "Stavroula",
        "Giorgos",
        "Chris",
        "Katerina",
        "Antonis",
        "Anna",
        "Apostolis"
    ]
    overlap_ratio = 0.7

    with open(SPIDER_TRAIN_PATH, 'r') as file:
        train_datapoints = json.load(file)

    categorized_datapoints = categorize_spider(train_datapoints)
    filtered_datapoints = filter_benchmark(categorized_datapoints)
    benchmark_datapoints, final_populations = sample_queries(populations, filtered_datapoints)
    transformed_benchmark = create_transformed_benchmark(benchmark_datapoints, DB_DIR)
    benchmark_per_annotator = assign_annotators(transformed_benchmark, annotators, overlap_ratio)

    print("Benchmark creation finished:")
    for cat, pop in final_populations.items():
        print(f"{cat}: {pop}")

    class NpEncoder(json.JSONEncoder):
        """ Needed to encode dictionary fields with numpy types """
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)

    for annotator, benchmark in benchmark_per_annotator.items():
        with open(OUTPUT_DIR + annotator + '.json', 'w') as outfile:
            json.dump(benchmark, outfile, cls=NpEncoder)


if __name__ == '__main__':
    create_benchmark_annotations()
