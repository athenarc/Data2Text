import json

from tqdm import tqdm

from data.pretraining.totto.utlis import (extract_concise_table_attributes,
                                          serialize_table)
from data.pretraining.wdc.tasks.column_masking import \
    find_indexes_of_masked_columns


def mask_columns_of_table(table, mixing_rate):
    table_attributes = extract_concise_table_attributes(table)

    masked_cols = set(find_indexes_of_masked_columns(len(table_attributes['cells']), mixing_rate))

    new_cells = []
    for ind, cell in enumerate(table_attributes['cells']):
        new_cells.append({
            'type': cell['type'],
            'value': cell['value'],
            'col': '[MASK]' if ind in masked_cols else cell['col']
        })

    new_table_attributes = {
        "table": table_attributes['table'],
        "query": table_attributes['query'],
        "cells": new_cells
    }

    def create_target():
        extract_cols = [cell['col'] for cell in table_attributes['cells']]
        return f"<S>{'<S>'.join(extract_cols)}<S>"

    return {
        "original": table,
        "task": serialize_table(new_table_attributes),
        "target": create_target()
    }


def totto_column_mixing_task(disable_tqdm=True):
    TOTTO_FILTERED_FILE = "storage/datasets/compact_input/totto/train.json"
    TOTTO_COLUMN_MASKING_FILE = "storage/datasets/compact_input/pretrain_totto/tasks/column_masking.json"
    MASKING_RATE = 0.35

    print("ToTTo | Column masking")

    with open(TOTTO_FILTERED_FILE) as f:
        datapoints = json.load(f)

    masked_datapoints = []

    for datapoint in tqdm(datapoints, disable=disable_tqdm):
        try:
            masked_datapoint = mask_columns_of_table(datapoint['subtable_and_metadata'], MASKING_RATE)
        except IndexError:
            continue

        masked_datapoints.append(masked_datapoint)

    with open(TOTTO_COLUMN_MASKING_FILE, 'w') as outfile:
        json.dump(masked_datapoints, outfile)

    print(f"DONE: Percentage of datapoints included {int(len(masked_datapoints) / len(datapoints) * 100)}%")


if __name__ == '__main__':
    totto_column_mixing_task(disable_tqdm=False)
