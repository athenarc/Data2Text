import logging
import sqlite3

import mo_parsing
import numpy as np
import pandas as pd
from asyncpg import exceptions

from app.backend.processing.process_query.query_pipeline import transform_query


def sample_row_from_res(res, cols):
    if cols is not None and len(cols) > 8:
        return None

    df_res = pd.DataFrame(res, columns=cols)

    df_res.replace('', np.nan, inplace=True)
    df_res.dropna(inplace=True)

    if len(df_res) == 0:
        return None

    single_row = df_res.sample(n=1)
    return single_row


def cordis_table_transform(table_df):
    return {col: val for col, val in zip(table_df.columns, table_df.iloc[0])}


def query_beautifier(query: str) -> str:
    keywords = ["FROM", "WHERE", "HAVING", "GROUP BY"]
    query = query.replace(' LIMIT 1', '')
    for keyword in keywords:
        index = query.find(keyword)
        if index != -1:
            query = query[:index] + '\n ' + query[index:]

    return query


async def gather_annotation_info(cordis_query, db_controller):
    # We do not allow nested queries
    if cordis_query.count('SELECT') >= 2:
        return None

    try:
        transformed_query, _ = transform_query(cordis_query)
    except mo_parsing.exceptions.ParseException:
        return None

    try:
        res, cols = await db_controller.query_with_res_cols(
            "postgresql+asyncpg://postgres:vdS83DJSQz2xQ@testbed.inode.igd.fraunhofer.de:18001/cordis_2021_09",
            transformed_query
        )
    except (exceptions.InvalidTextRepresentationError, exceptions.UndefinedTableError):
        return None

    sampled_row = sample_row_from_res(res, cols)
    if sampled_row is None:
        return None

    cordis_transformed_res = cordis_table_transform(sampled_row)

    return cordis_transformed_res
