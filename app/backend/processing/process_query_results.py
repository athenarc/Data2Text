from typing import Dict

from app.backend.processing.process_query.difficulty_check import \
    DifficultyNotImplemented


def create_metadata(table_name, nl_query="") -> str:
    page_title = f"<page_title> {table_name} </page_title>"
    section_title = f"<section_title> {nl_query if nl_query != '' else table_name} </section_title>"

    return page_title + " " + section_title


def create_cell(col_name: str, col_value: str) -> str:
    return f"<cell> {col_value} <col_header> {col_name} </col_header> </cell>"


def query_results_to_totto(query_results: Dict[str, str]):
    metadata = create_metadata(query_results['tables_name'])
    table_cells_str = ""

    if len(query_results['rows']) > 1:
        raise DifficultyNotImplemented("Query results with multiple rows cannot be explained yet.")

    for row in query_results['rows']:
        for header, val in zip(query_results['col_names'], row):
            table_cells_str += create_cell(header, val) + " "

    return f"{metadata} <table> {table_cells_str}</table>"
