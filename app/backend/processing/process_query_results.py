from typing import Dict

from dateutil.parser import parse

from app.backend.processing.process_query.difficulty_check import \
    DifficultyNotImplemented


def create_metadata(table_name, nl_query="") -> str:
    return f"<query> {nl_query} <table> {table_name} "


def create_cell(col_name: str, col_value: str, ind: int) -> str:
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
        except (ValueError, OverflowError):
            return False

    def extract_type(cell_value):
        if is_numeric(cell_value):
            return 'NUMERIC'
        elif is_date(cell_value):
            return 'DATE'
        else:
            return 'STRING'

    return f"<col{ind}> {col_name} | {extract_type(str(col_value))} | {col_value} "


def query_results_to_totto(query_results: Dict[str, str], nl_query):
    metadata = create_metadata(query_results['tables_name'], nl_query)
    table_cells_str = ""

    if len(query_results['rows']) > 1:
        raise DifficultyNotImplemented("Query results with multiple rows cannot be explained yet.")

    for ind, row in enumerate(query_results['rows']):
        for header, val in zip(query_results['col_names'], row):
            table_cells_str += create_cell(header, val, ind)

    return metadata + table_cells_str
