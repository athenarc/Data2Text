import json

from tqdm import tqdm

from data.pretraining.totto.utlis import (extract_concise_table_attributes,
                                          serialize_table)
from data.pretraining.wdc.tasks.column_mixing import create_mixin_pairs


def mix_columns_of_table(table, mixing_rate):
    table_attributes = extract_concise_table_attributes(table)

    mixin_pairs = create_mixin_pairs(len(table_attributes['cells']), mixing_rate)
    # print(mixin_pairs)

    new_cells = []
    for ind, cell in enumerate(table_attributes['cells']):
        new_cells.append({
            'type': cell['type'],
            'value': cell['value'],
            'col': table_attributes['cells'][mixin_pairs[ind]]['col'] if ind in mixin_pairs else cell['col']
        })

    new_table_attributes = {
        "table": table_attributes['table'],
        "query": table_attributes['query'],
        "cells": new_cells
    }
    # print(new_table_attributes)

    def create_target():
        extract_cols = [cell['col'] for cell in table_attributes['cells']]
        return f"<S> {' <S> '.join(extract_cols)} <S>"

    return {
        "original": table,
        "task": serialize_table(new_table_attributes),
        "target": create_target()
    }


def totto_column_mixing_task(disable_tqdm=True):
    TOTTO_FILTERED_FILE = "storage/datasets/compact_input/totto/train.json"
    TOTTO_COLUMN_MIXING_FILE = "storage/datasets/compact_input/pretrain_totto/tasks/column_mixing.json"
    MIXING_RATE = 0.55

    print("ToTTo | Column mixing")

    with open(TOTTO_FILTERED_FILE) as f:
        datapoints = json.load(f)

    mixed_datapoints = []

    for datapoint in tqdm(datapoints, disable=disable_tqdm):
        try:
            mixed_datapoint = mix_columns_of_table(datapoint['subtable_and_metadata'], MIXING_RATE)
        except IndexError:
            continue

        mixed_datapoints.append(mixed_datapoint)

    with open(TOTTO_COLUMN_MIXING_FILE, 'w') as outfile:
        json.dump(mixed_datapoints, outfile)

    print(f"DONE: Percentage of datapoints included {int(len(mixed_datapoints) / len(datapoints) * 100)}%")


if __name__ == '__main__':
    totto_column_mixing_task(disable_tqdm=False)
