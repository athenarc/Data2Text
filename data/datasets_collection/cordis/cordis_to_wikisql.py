import glob
import json
import re
from typing import List

import pandas as pd

from app.backend.processing.process_query.query_pipeline import transform_query


def load_query_res_paths(dir_path: str) -> List[str]:
    if dir_path[-1] != '/':
        dir_path += "/"

    query_res_paths = sorted([path for path in glob.glob(f"{dir_path}*")],
                             key=lambda x: int(re.sub("[^0-9]", "", x)))

    return query_res_paths


def query_res_to_str(res_paths):
    str_res = []
    for path in res_paths:
        str_res.append(pd
                       .read_csv(path, header=0)
                       .to_csv()
                       )

    return str_res


def raw_to_dict(query_data, result):
    query_data = query_data[1]  # omit the index of the row
    return {
        "table_id": f"cordis.{query_data.table}",
        "query": query_data.query,
        "table_name": query_data.table,
        "query_description": query_data.nl_query,
        "results_description": query_data.nl_results,
        "result": result,
        "difficulty": 1
    }


def difficulty_checker(tables: str, query: str) -> str:
    aggr_funcs = ["avg(", "sum(", "max(", "min(", "count("]
    diff = ""

    # Check JOIN difficulty
    if tables.count(',') > 0:
        diff += "JOIN,"

    # Check AGGREGATION difficulty
    for aggr in aggr_funcs:
        if aggr in query.lower():
            diff += "AGGREGATION,"
            break

    # Check no difficulty
    if diff == "":
        diff += "NONE,"

    return diff[:-1]


def curated_to_dict(query_data, result):
    # query_data = query_data[1]  # omit the index of the row
    return {
        "table_id": query_data.id,
        "query": query_data.processed_query,
        "table_name": transform_query(query_data.sql_query)[1],
        "query_description": query_data.question,
        "results_description": query_data.verbalisation,
        "result": result,
        "difficulty": "NONE"
    }


def load_query_result(query_results_dir: str, query_ind: int) -> str:
    if query_results_dir[-1] != '/':
        query_results_dir += "/"

    results_df = pd.read_csv(f"{query_results_dir}q{query_ind}.csv", header=0)

    return results_df.to_csv()


def cordis_to_json(query_metadata_path, query_results_dir):
    query_metadata = pd.read_csv(query_metadata_path, header=0)
    query_results = query_res_to_str(load_query_res_paths(query_results_dir))

    cordis_json = []
    for query_data, result in zip(query_metadata.iterrows(), query_results):
        cordis_json.append(raw_to_dict(query_data, result))

    return cordis_json


def curated_cordis_to_json(query_metadata_path, query_results_dir):
    query_metadata = pd.read_csv(query_metadata_path, header=0)

    cordis_json = []
    for _, query_data in query_metadata.iterrows():
        if not pd.isnull(query_data.verbalisation):
            query_results = load_query_result(query_results_dir, query_data.id)
            cordis_json.append(curated_to_dict(query_data, query_results))

    return cordis_json


if __name__ == '__main__':
    # Original CORDIS
    # jsoned_cordis = cordis_to_json('storage/datasets/cordis/raw/CORDIS_Evaluation.csv',
    #                                'storage/datasets/cordis/raw/queries')
    #
    # with open('storage/datasets/cordis/cordis_to_wikisql.json', 'w') as outfile:
    #     json.dump(jsoned_cordis, outfile)

    # Curated CORDIS
    jsoned_cordis = curated_cordis_to_json('storage/datasets/cordis_inode/original/cordis_new_train.csv',
                                           'storage/datasets/cordis_inode/original/verbalisations')

    with open('storage/datasets/cordis_inode/to_wiki_sql/train.json', 'w') as outfile:
        json.dump(jsoned_cordis, outfile)
