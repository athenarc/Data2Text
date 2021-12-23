import glob
import json
import math
import random
from typing import List, Tuple

from tqdm import tqdm

from data.pretraining.wdc.utils import pick_row_and_section
from data.pretraining.wdc.wdc_to_totto import create_totto_table


def find_number_of_maskings(total_cols, mixing_rate) -> int:
    # Tables with less than 4 columns should not be allowed
    return math.ceil(total_cols * mixing_rate) if total_cols > 1 else 0


def find_indexes_of_mixed_columns(total_cols, mixing_rate) -> List[int]:
    return sorted(random.sample(range(total_cols), find_number_of_maskings(total_cols, mixing_rate)))


def create_target(cols, mask_inds) -> str:
    cols_with_masks = []
    mask_counter = 0
    for ind in mask_inds:
        cols_with_masks.append(f"<extra_id_{mask_counter}>{cols[ind]}")
        mask_counter += 1

    return f"{''.join(cols_with_masks)}<extra_id_{mask_counter}>"


def create_cols_with_masks(cols, mixing_rate) -> Tuple[List[str], str]:
    masked_col_inds = find_indexes_of_mixed_columns(len(cols), mixing_rate)

    cols_with_masks = []
    mask_counter = 0
    for ind, col in enumerate(cols):
        if ind in masked_col_inds:
            cols_with_masks.append(f'<extra_id_{mask_counter}>')
            mask_counter += 1
        else:
            cols_with_masks.append(col)

    target = create_target(cols, masked_col_inds)

    return cols_with_masks, target


def mask_col_on_table(table, mixing_rate):
    row, section = pick_row_and_section(table)

    masked_columns, target = create_cols_with_masks(table['relation'][0], mixing_rate)

    totto_original = create_totto_table({
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'section': section,
        'columns': table['relation'][0],
        'row': row
    })

    totto_masked = create_totto_table({
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'section': section,
        'columns': masked_columns,
        'row': row
    })

    return {
        "totto_original": totto_original,
        "totto_masked": totto_masked,
        "target": target
    }


def check_numb_of_cols(table, minimum):
    return len(table['relation'][0]) >= minimum


def column_masking_task(disable_tqdm=True):
    WDC_FILTERED_DIR = "storage/datasets/wdc/filtered/"
    WDC_COLUMN_MASKING_DIR = "storage/datasets/wdc/column_masking/"
    MASKING_RATE = 0.15

    table_files = glob.glob(f"{WDC_FILTERED_DIR}*")

    for ind, table_file in enumerate(table_files):
        print(f"WDC | Column masking | File: {ind + 1} / {len(table_files)}")

        # Read
        with open(table_file, 'r') as inp:
            filtered_tables = json.load(inp)

        # Column masking
        column_masking_datapoints = []
        for table in tqdm(filtered_tables, disable=disable_tqdm):
            if check_numb_of_cols(table, minimum=4):
                column_masking_datapoints.append(mask_col_on_table(table, MASKING_RATE))

        # Storing
        with open(WDC_COLUMN_MASKING_DIR + table_file.split('/')[-1], 'w') as outfile:
            json.dump(column_masking_datapoints, outfile)

    print(f"DONE!")


if __name__ == '__main__':
    column_masking_task(disable_tqdm=False)
