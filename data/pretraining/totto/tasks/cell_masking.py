import json
import random

from tqdm import tqdm

from data.pretraining.totto.utlis import (extract_concise_table_attributes,
                                          serialize_table)
from data.pretraining.wdc.tasks.column_masking import \
    find_indexes_of_masked_columns


def mask_table_values(table, masking_rate):
    table_attributes = extract_concise_table_attributes(table)
    masked_values_inds = set(find_indexes_of_masked_columns(len(table_attributes['cells']), masking_rate))

    new_cells = []
    masked_cell_ind = 0

    for ind, cell in enumerate(table_attributes['cells']):
        new_cells.append({
            'type': cell['type'],
            'value': f'<extra_id_{masked_cell_ind}>' if ind in masked_values_inds else cell['value'],
            'col': cell['col']
        })
        if ind in masked_values_inds:
            masked_cell_ind += 1

    new_table_attributes = {
        "table": table_attributes['table'],
        "query": table_attributes['query'],
        "cells": new_cells
    }

    def create_target():
        target_str = ""
        for ind, masked_ind in enumerate(masked_values_inds):
            target_str += f"<extra_id_{ind}> {table_attributes['cells'][masked_ind]['value']} "
        target_str += f"<extra_id_{len(masked_values_inds)}>"

        return target_str

    return {
        "original": table,
        "task": serialize_table(new_table_attributes),
        "target": create_target()
    }


def totto_value_masking_task(disable_tqdm=True):
    TOTTO_FILTERED_FILE = "storage/datasets/compact_input/totto/train.json"
    TOTTO_MASKED_CELL_VALUES_FILE = "storage/datasets/compact_input/pretrain_totto/tasks/value_masking.json"
    MASKING_RATE = 0.3

    print("ToTTo | Value masking")

    with open(TOTTO_FILTERED_FILE) as f:
        datapoints = json.load(f)

    masked_value_datapoints = []

    for datapoint in tqdm(datapoints, disable=disable_tqdm):
        try:
            modified_datapoint = mask_table_values(datapoint['subtable_and_metadata'], MASKING_RATE)
        except IndexError:
            continue

        masked_value_datapoints.append(modified_datapoint)

    with open(TOTTO_MASKED_CELL_VALUES_FILE, 'w') as outfile:
        json.dump(masked_value_datapoints, outfile)

    print(f"DONE: Percentage of datapoints included {int(len(masked_value_datapoints) / len(datapoints) * 100)}%")


if __name__ == '__main__':
    totto_value_masking_task(disable_tqdm=False)
