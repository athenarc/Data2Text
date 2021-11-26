from typing import Dict, List

from app.backend.processing.process_query.clause_extractors import (
    find_join_type_in_from, find_select_math_operation, is_aggregate,
    is_distinct, is_star_select)


def apply_join_aliases(query, tables):
    if len(tables) == 1:
        return query

    table_mappings = get_from_mappings(query['from'])
    for sel_clause in query['select']:
        if is_aggregate(sel_clause) \
                or is_star_select(sel_clause) \
                or is_distinct(sel_clause) \
                or (find_select_math_operation(sel_clause) is not None):
            # We do not alias the aggregates. Their information is added through the aggregate injector.
            continue
        table_col = sel_clause['value'].split('.')
        if len(table_col) == 1:
            # We have SELECTED only the column without the table name eg. SELECT col1
            continue

        if table_col[0] in table_mappings:
            # Case SELECT table1.c1 FROM table1, table2
            sel_clause['name'] = f"{table_mappings[table_col[0]]} {table_col[1]}"
        else:
            # Case SELECT t1.c1 FROM table1 t1, table2 t2
            sel_clause['name'] = f"{table_col[0]} {table_col[1]}"

    return query


def get_from_mappings(from_clause):
    if not isinstance(from_clause, List):
        from_clause = [from_clause]

    mappings = {}
    for table in from_clause:
        if not isinstance(table, Dict):
            continue

        if 'name' in table:
            # Simple alias case
            mappings[table['name']] = table['value']
        elif (join_type := find_join_type_in_from(table)) is not None:
            if isinstance(table[join_type], Dict):
                # Alias on joined table
                mappings[table[join_type]['name']] = table[join_type]['value']

    return mappings
