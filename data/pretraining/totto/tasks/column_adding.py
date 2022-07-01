import json
import random

from tqdm import tqdm

from data.pretraining.totto.utlis import (extract_concise_table_attributes,
                                          serialize_table)


def get_sample_column(tables):
    def get_parsed_table():
        while True:
            try:
                return extract_concise_table_attributes(random.choice(tables)['subtable_and_metadata'])
            except IndexError:
                continue

    sample_table = get_parsed_table()

    return random.choice(sample_table['cells'])


def get_inds_of_added_cols(original_cols_numb, added_cols_numb):
    return set(random.sample(range(original_cols_numb), added_cols_numb))


def add_columns_on_table(table, max_added_columns, tables):
    table_attributes = extract_concise_table_attributes(table)
    numb_added_cols = random.choice(range(1, max_added_columns))

    added_cols = [get_sample_column(tables) for _ in range(numb_added_cols)]
    inds_of_added_cols = get_inds_of_added_cols(len(table_attributes['cells']), numb_added_cols)

    new_cells = []
    added_col_ind = 0

    for ind, cell in enumerate(table_attributes['cells']):
        if ind in inds_of_added_cols:
            new_cells.append({
                'type': added_cols[added_col_ind]['type'],
                'value': added_cols[added_col_ind]['value'],
                'col': added_cols[added_col_ind]['col']
            })
            added_col_ind += 1

        new_cells.append({
            'type': cell['type'],
            'value': cell['value'],
            'col': cell['col']
        })

    new_table_attributes = {
        "table": table_attributes['table'],
        "query": table_attributes['query'],
        "cells": new_cells
    }

    def create_target():
        extract_cols = [cell['col'] for cell in table_attributes['cells']]
        return f"<S> {' <S> '.join(extract_cols)} <S>"

    return {
        "original": table,
        "task": serialize_table(new_table_attributes),
        "target": create_target()
    }


def totto_column_adding_task(disable_tqdm=True):
    TOTTO_FILTERED_FILE = "storage/datasets/compact_input/totto/train.json"
    TOTTO_ADDED_COLUMNS_FILE = "storage/datasets/compact_input/pretrain_totto/tasks/added_columns.json"
    MAX_ADDED_COLS = 2

    print("ToTTo | Column adding")

    with open(TOTTO_FILTERED_FILE) as f:
        datapoints = json.load(f)

    added_cols_datapoints = []

    for datapoint in tqdm(datapoints, disable=disable_tqdm):
        try:
            modified_datapoint = add_columns_on_table(datapoint['subtable_and_metadata'], MAX_ADDED_COLS, datapoints)
        except IndexError:
            continue

        added_cols_datapoints.append(modified_datapoint)

    with open(TOTTO_ADDED_COLUMNS_FILE, 'w') as outfile:
        json.dump(added_cols_datapoints, outfile)

    print(f"DONE: Percentage of datapoints included {int(len(added_cols_datapoints) / len(datapoints) * 100)}%")


if __name__ == '__main__':
    totto_column_adding_task(disable_tqdm=False)
