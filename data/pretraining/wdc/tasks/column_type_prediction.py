import glob
import json
from typing import List, Optional

from dateutil.parser import parse
from tqdm import tqdm

from data.pretraining.wdc.wdc_to_totto import create_totto_table


def is_numeric(cell: str) -> bool:
    try:
        _ = float(cell.replace(',', ''))
        return True
    except ValueError:
        pass

    try:
        _ = float(cell.replace(' ', '').replace('-', ''))
        return True
    except ValueError:
        pass

    return False


def is_date(cell: str) -> bool:
    try:
        _ = parse(cell, fuzzy=False)
        return True
    except ValueError:
        return False


def find_nonempty_row(table) -> Optional[List[str]]:
    for row in table['relation'][1:]:
        if not any(cell == '' for cell in row):
            return row

    return None


def find_column_types(row) -> List[str]:
    column_types = []
    for cell in row:
        if is_numeric(cell):
            column_types.append('NUMERIC')
        elif is_date(cell):
            column_types.append('DATE')
        else:
            column_types.append('STRING')

    return column_types


def create_target(col_types: List[str]) -> str:
    return f"<S>{'<S>'.join(col_types)}<S>"


def create_column_type_prediction_task(table):
    row = find_nonempty_row(table)
    if row is None:
        return None

    col_types = find_column_types(row)
    target = create_target(col_types)

    totto_original = create_totto_table({
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'section': table['textAfterTable'],
        'columns': table['relation'][0],
        'row': row
    })

    totto_col_types = create_totto_table({
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'section': table['textAfterTable'],
        'columns': table['relation'][0],
        'row': [''] * len(row)
    })

    return {
        "totto_original": totto_original,
        "totto_mixed": totto_col_types,
        "target": target
    }


def column_type_task(disable_tqdm=True):
    WDC_FILTERED_DIR = "storage/datasets/wdc/filtered/"
    WDC_COLUMN_TYPE_DIR = "storage/datasets/wdc/column_type/"

    table_files = glob.glob(f"{WDC_FILTERED_DIR}*")

    for ind, table_file in enumerate(table_files):
        print(f"WDC | Column type | File: {ind + 1} / {len(table_files)}")

        # Read
        with open(table_file, 'r') as inp:
            filtered_tables = json.load(inp)

        # Column mixing
        column_type_datapoints = []
        for table in tqdm(filtered_tables, disable=disable_tqdm):
            added_datapoint = create_column_type_prediction_task(table)
            if added_datapoint is not None:
                column_type_datapoints.append(added_datapoint)

        # Storing
        with open(WDC_COLUMN_TYPE_DIR + table_file.split('/')[-1], 'w') as outfile:
            json.dump(column_type_datapoints, outfile)

    print(f"DONE!")


if __name__ == '__main__':
    column_type_task(disable_tqdm=False)
