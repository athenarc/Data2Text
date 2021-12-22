import glob
import json
import math
import random
from typing import Dict, List, Tuple

from tqdm import tqdm

from data.pretraining.wdc.utils import (find_rows_with_high_overlap,
                                        pick_row_and_section)
from data.pretraining.wdc.wdc_to_totto import create_totto_table


def find_number_of_mixins(total_cols, mixing_rate) -> int:
    return math.ceil(total_cols * mixing_rate) if total_cols > 1 else 0


def find_indexes_of_mixed_columns(total_cols, mixing_rate) -> List[int]:
    return random.sample(range(total_cols), find_number_of_mixins(total_cols, mixing_rate))


def create_mixin_pairs(total_cols, mixing_rate) -> Dict[int, int]:
    mixed_inds = find_indexes_of_mixed_columns(total_cols, mixing_rate)
    remaining_inds = mixed_inds.copy()

    pairs = {}
    for original_ind in mixed_inds:
        pairs[original_ind] = random.choice(remaining_inds)
        remaining_inds.remove(pairs[original_ind])

    return pairs


def mix_columns(cols, mixing_rate) -> List[str]:
    mixed_cols = []

    mixed_pairs = create_mixin_pairs(len(cols), mixing_rate)
    for ind in range(len(cols)):
        if ind in mixed_pairs:
            mixed_cols.append(cols[mixed_pairs[ind]])
        else:
            mixed_cols.append(cols[ind])

    return mixed_cols


def create_target_cols(cols) -> str:
    return f"<S>{'<S>'.join(cols)}<S>"


def create_mixing_task_from_table(table, mixing_rate):
    row, section = pick_row_and_section(table)

    mixed_columns = mix_columns(table['relation'][0], mixing_rate)

    totto_original = create_totto_table({
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'section': section,
        'columns': table['relation'][0],
        'row': row
    })

    totto_mixed = create_totto_table({
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'section': section,
        'columns': mixed_columns,
        'row': row
    })

    target = create_target_cols(table['relation'][0])

    return {
        "totto_original": totto_original,
        "totto_mixed": totto_mixed,
        "target": target
    }


def column_mixing_task(disable_tqdm=True):
    WDC_FILTERED_DIR = "storage/datasets/wdc/filtered/"
    WDC_COLUMN_MIXING_DIR = "storage/datasets/wdc/column_mixing/"
    MIXING_RATE = 0.35

    table_files = glob.glob(f"{WDC_FILTERED_DIR}*")

    for ind, table_file in enumerate(table_files):
        print(f"WDC | Column mixing | File: {ind + 1} / {len(table_files)}")

        # Read
        with open(table_file, 'r') as inp:
            filtered_tables = json.load(inp)

        # Column mixing
        column_mixing_datapoints = []
        for table in tqdm(filtered_tables, disable=disable_tqdm):
            column_mixing_datapoints.append(create_mixing_task_from_table(table, MIXING_RATE))

        # Storing
        with open(WDC_COLUMN_MIXING_DIR + table_file.split('/')[-1], 'w') as outfile:
            json.dump(column_mixing_datapoints, outfile)

    print(f"DONE!")


if __name__ == '__main__':
    column_mixing_task(disable_tqdm=False)
