import json
from io import StringIO
from typing import Dict, List

import pandas as pd

from data.datasets_collection.wiki_sql.Annotation.annotator import Annotation


def create_metadata(annotation: Annotation, use_query: bool) -> str:
    page_title = f"<page_title> {annotation.table_name} </page_title>"
    section_title = f"<section_title> {annotation.query_description if use_query else annotation.table_name} " \
                    f"</section_title>"

    return page_title + " " + section_title


def create_cell(col_name: str, col_value: str) -> str:
    return f"<cell> {col_value} <col_header> {col_name} </col_header> </cell>"


def extract_cells_from_df(table_df: pd.DataFrame) -> List[Dict[str, str]]:
    cell_list = []
    for _, row in table_df.iterrows():
        for name, val in row.items():
            try:
                added_value = int(val) if int(val) == val else val
            except ValueError:
                added_value = val
            cell_list.append({"col_header": name, "col_val": str(added_value)})

    return cell_list


def parse_str_csv(str_df: str) -> pd.DataFrame:
    data = StringIO(str_df)
    return pd.read_csv(data, sep=',', index_col=0)


def wikisql_datapoint_diff1_to_totto(annotation: Annotation, use_query: bool) -> Dict[str, str]:
    totto_datapoint = {}

    metadata = create_metadata(annotation, use_query)
    table_cells = extract_cells_from_df(parse_str_csv(annotation.result))
    table_cells_str = ""
    for cell_dict in table_cells:
        table_cells_str += create_cell(cell_dict['col_header'], cell_dict['col_val']) + " "

    totto_datapoint['subtable_and_metadata'] = f"{metadata} <table> {table_cells_str}</table>"
    totto_datapoint['final_sentence'] = annotation.results_description

    return totto_datapoint


def transform_wikisql_to_totto(annotations_path: str, save_path: str, use_query: bool) -> None:
    with open(annotations_path) as f:
        annotations = json.load(f)

    totto_datapoints = [wikisql_datapoint_diff1_to_totto(Annotation(**annotation_dict), use_query)
                        for annotation_dict in annotations]

    with open(save_path, 'w') as fp:
        json.dump(totto_datapoints, fp)


if __name__ == '__main__':
    # The paths below expect the sys.path to be the project root
    ANNOTATIONS_PATH = "storage/datasets/cordis_inode/to_wiki_sql/train.json"
    TOTTO_SAVE_PATH = "storage/datasets/cordis_inode/to_totto/train.json"
    USE_QUERY = True

    transform_wikisql_to_totto(ANNOTATIONS_PATH, TOTTO_SAVE_PATH, USE_QUERY)
