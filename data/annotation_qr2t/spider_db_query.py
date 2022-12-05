import json
import logging
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
    # We do not allow nested queries
    if spider_datapoint['query'].count('SELECT') >= 2:
        return None

    transformed_query, _ = transform_query(spider_datapoint['query'])

    res, cols = connect_and_query(
        create_db_path(db_dir, spider_datapoint['db_id']),
        transformed_query
    )

    sampled_row = sample_row_from_res(res, cols)
    if sampled_row is None:
        return None

    spider_transformed_res = spider_table_transform(sampled_row)

    return {
        "db": spider_datapoint['db_id'],
        "res": spider_transformed_res,
        "original_query": query_beautifier(spider_datapoint['query']),
        "transformed_query": query_beautifier(transformed_query),
        "nl_query": spider_datapoint['question'],
        "category": spider_datapoint['category']
    }


def create_transformed_benchmark(train_datapoints, db_dir):
    annotations = []
    for datapoint in train_datapoints:
        try:
            annotation_point = gather_annotation_info(datapoint, db_dir)
        except sqlite3.OperationalError:
            logging.warning(f"Query not executed: {datapoint['query']}")
            continue

        if annotation_point is not None:
            annotations.append(annotation_point)

    return annotations
