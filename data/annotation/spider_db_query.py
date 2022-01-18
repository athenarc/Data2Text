import json
import sqlite3

import numpy as np
import pandas as pd

from app.backend.processing.process_query.query_pipeline import transform_query


def connect_and_query(db_path, query):
    con = sqlite3.connect(db_path)

    cur = con.cursor()
    cur.execute(query)
    res = cur.fetchall()
    desc = [d[0] for d in cur.description]

    con.close()

    return res, desc


def filter_out_queries(queries):
    """
    We filter out nested queries and queries containing the keyword 'time'
    """
    return [q for q in queries if len(q['query'].split('SELECT')) == 2 and ('time' not in q['query'].lower())]


def create_db_path(db_dir, db_id):
    return f"{db_dir}{db_id}/{db_id}.sqlite"


def sample_row_from_res(res, cols):
    df_res = pd.DataFrame(res, columns=cols)

    df_res.replace('', np.nan, inplace=True)
    df_res.dropna(inplace=True)

    if len(df_res) == 0:
        return None

    single_row = df_res.sample(n=1)
    return single_row


def spider_table_transform(table_df):
    return {col: val for col, val in zip(table_df.columns, table_df.iloc[0])}


def query_beautifier(query: str) -> str:
    keywords = ["FROM", "WHERE", "HAVING", "GROUP BY"]
    query = query.replace(' LIMIT 1', '')
    for keyword in keywords:
        index = query.find(keyword)
        if index != -1:
            query = query[:index] + '\n ' + query[index:]

    return query


def gather_annotation_info(spider_datapoint, db_dir):
    transformed_query, _ = transform_query(spider_datapoint['query'])
    res, cols = connect_and_query(
        create_db_path(db_dir, spider_datapoint['db_id']),
        transformed_query
    )

    return {
        "db": spider_datapoint['db_id'],
        "res": spider_table_transform(sample_row_from_res(res, cols)),
        "original_query": query_beautifier(spider_datapoint['query']),
        "transformed_query": query_beautifier(transformed_query),
        "nl_query": spider_datapoint['question']
    }


def main():
    SPIDER_TRAIN_PATH = "storage/datasets/spider/original/train_spider.json"
    DB_DIR = "storage/datasets/spider/original/database/"
    OUTPUT_PATH = "storage/datasets/spider/annotations/label_studio/annotations.json"

    with open(SPIDER_TRAIN_PATH, 'r') as file:
        train_datapoints = json.load(file)

    annotations = []
    for datapoint in train_datapoints[:10]:
        annotation_point = gather_annotation_info(datapoint, DB_DIR)
        if annotation_point is not None:
            annotations.append(annotation_point)

    with open(OUTPUT_PATH, 'w') as outfile:
        json.dump(annotations, outfile)


if __name__ == '__main__':
    main()
