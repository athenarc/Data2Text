from typing import Dict, List


def apply_join_aliases(query, tables):
    if len(tables) == 1:
        return query

    table_mappings = get_from_mappings(query['from'])
    for sel_clause in query['select']:
        table_col = sel_clause['value'].split('.')
        if len(table_col) == 1:
            # We have SELECTED only the column without the table name eg. SELECT col1
            continue

        if table_col[0] in table_mappings:
            sel_clause['name'] = f"{table_mappings[table_col[0]]} {table_col[1]}"

    return query


def get_from_mappings(from_clause):
    if isinstance(from_clause, str):
        return {}
    elif isinstance(from_clause, Dict):
        return {from_clause['name']: from_clause['value']}
    elif isinstance(from_clause, List):
        mappings = {}
        for table in from_clause:
            try:
                mappings[table['name']] = table['value']
            except TypeError:
                # Case that the table does not have an alias in the query.
                continue

        return mappings
    else:
        raise TypeError("Unexpected type.")
