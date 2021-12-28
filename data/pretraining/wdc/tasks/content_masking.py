import glob
import json
from typing import Set

from tqdm import tqdm

from data.pretraining.wdc.utils import (find_overlapping_tokens,
                                        pick_row_and_section)
from data.pretraining.wdc.wdc_to_totto import create_totto_table


def apply_mask_to_sent(sent: str, overlap_tokens: Set[str]) -> str:
    """
    Notice that if a cell value appears multiple times it will be replaced by the same special token.
    """
    for ind, token in enumerate(overlap_tokens):
        sent = sent.replace(token, f"<extra_id_{ind}>")

    return sent


def create_target(overlap_tokens: Set[str]) -> str:
    target_str = ""
    for ind, token in enumerate(overlap_tokens):
        target_str += f"<extra_id_{ind}>{token}"
    target_str += f"<extra_id_{len(overlap_tokens)}>"

    return target_str


def create_content_masking_task_from_table(table, threshold=1):
    row, section = next(pick_row_and_section(table, threshold))
    if section == "":
        return None

    overlap_tokens = sorted(find_overlapping_tokens(section, row))

    masked_section = apply_mask_to_sent(section, overlap_tokens)
    target = create_target(overlap_tokens)

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
        'section': masked_section,
        'columns': table['relation'][0],
        'row': row
    })

    return {
        "totto_original": totto_original,
        "totto_mixed": totto_mixed,
        "target": target
    }


def content_table_masking_task(disable_tqdm=True):
    WDC_FILTERED_DIR = "storage/datasets/wdc/filtered/"
    WDC_CONTENT_MASKING_DIR = "storage/datasets/wdc/content_masking/"

    table_files = glob.glob(f"{WDC_FILTERED_DIR}*")

    for ind, table_file in enumerate(table_files):
        print(f"WDC | Content masking | File: {ind + 1} / {len(table_files)}")

        # Read
        with open(table_file, 'r') as inp:
            filtered_tables = json.load(inp)

        # Column mixing
        content_masking_datapoints = []
        for table in tqdm(filtered_tables, disable=disable_tqdm):
            datapoint = create_content_masking_task_from_table(table, threshold=1)
            if datapoint is not None:
                content_masking_datapoints.append(datapoint)

        # Storing
        with open(WDC_CONTENT_MASKING_DIR + table_file.split('/')[-1], 'w') as outfile:
            json.dump(content_masking_datapoints, outfile)

    print(f"DONE!")


if __name__ == '__main__':
    content_table_masking_task(disable_tqdm=False)
