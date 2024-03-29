import logging

from app.backend.processing.process_query.clause_extractors import (
    find_select_math_operation, is_aggregate)
from app.backend.processing.process_query.query_injectors.inject_column_aliases import \
    get_from_mappings


def verbalise_aggregates(query, tables):
    """
    Verbalises aggregators so as to help the model that is trained on ToTTo
    better understand the meaning of the aggregates.

    AVG(col1) -> average col1
    COUNT(col1) FROM table -> count of table
    MAX(col1) -> maximum col1
    MIN(col1) -> minimum col1
    SUM(col1) -> sum of col1

    This method changes the dict parameter "query" inplace.
    """
    aggregate_clauses = [clause for clause in query['select'] if is_aggregate(clause)]
    for sel_clause in aggregate_clauses:
        aggr_func, aggr_col = list(sel_clause['value'].items())[0]
        if isinstance(aggr_col, dict):
            if (arithmetic_op := find_select_math_operation({'value': aggr_col})) is not None:
                # CASE: SELECT AVG(c1 - c2) FROM t1
                aggr_col = f" {MATH_OPS_SYMBOL[arithmetic_op]} ".join(aggr_col[arithmetic_op])
            else:
                # Case: SELECT COUNT(DISTINCT c1) FROM t1
                try:
                    aggr_col = aggr_col['distinct']['value']
                except KeyError:
                    raise KeyError(f"Unexpected aggregate clause {sel_clause}")

        if aggr_func == "avg":
            aggr_col = aggr_col.split('.')[-1]
            sel_clause['name'] = verbalise_avg(aggr_col)
        elif aggr_func == "max":
            aggr_col = aggr_col.split('.')[-1]
            sel_clause['name'] = verbalise_max(aggr_col)
        elif aggr_func == "min":
            aggr_col = aggr_col.split('.')[-1]
            sel_clause['name'] = verbalise_min(aggr_col)
        elif aggr_func == "sum":
            aggr_col = aggr_col.split('.')[-1]
            sel_clause['name'] = verbalise_sum(aggr_col)
        elif aggr_func == "count":
            if len(tables) == 1:
                # Single table query
                sel_clause['name'] = verbalise_count(tables[0])
            else:
                # JOIN query
                sel_clause['name'] = verbalise_count(
                    map_column_alias_to_table(aggr_col, query, tables))
        else:
            logging.warning(f"Cannot verbalise aggregate {aggr_func}.")

    return query


def verbalise_avg(column_name: str) -> str:
    return f"average {column_name}"


def verbalise_count(table_name: str) -> str:
    return f"count of {table_name}"


def verbalise_max(column_name: str) -> str:
    return f"maximum {column_name}"


def verbalise_min(column_name: str) -> str:
    return f"minimum {column_name}"


def verbalise_sum(column_name: str) -> str:
    return f"sum of {column_name}"


def map_column_alias_to_table(col_name, query, tables):
    table_mappings = get_from_mappings(query['from'])

    try:
        table_alias, col_name = col_name.split('.')
        return table_mappings.get(table_alias, table_alias)
    except ValueError:
        # Case that we have COUNT(*) and multiple tables
        # The verbalization ends up being: "count of t1 and t2 and t3..."
        return " and ".join(tables)


MATH_OPS_SYMBOL = {
    'add': '+',
    'sub': '-',
    'mul': '*',
    'div': '/',
    'mod': '%',
}
