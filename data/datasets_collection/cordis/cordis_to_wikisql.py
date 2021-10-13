import glob
import json
import re
from typing import List

import pandas as pd


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


def to_dict(query_data, result):
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


def cordis_to_json(query_metadata_path, results_dir):
    query_metadata = pd.read_csv(query_metadata_path, header=0)
    query_results = query_res_to_str(load_query_res_paths(results_dir))

    cordis_json = []
    for query_data, result in zip(query_metadata.iterrows(), query_results):
        cordis_json.append(to_dict(query_data, result))

    return cordis_json


if __name__ == '__main__':
    jsoned_cordis = cordis_to_json('storage/datasets/cordis/raw/CORDIS_Evaluation.csv',
                                   'storage/datasets/cordis/raw/queries')

    with open('storage/datasets/cordis/cordis_to_wikisql.json', 'w') as outfile:
        json.dump(jsoned_cordis, outfile)
