from typing import Dict, Set


def add_where_cols_to_sel(query: Dict, added_cols: Set[str]) -> Dict:
    # We assume that we are in the easy case of having just one table
    query_copy = query.copy()
    for col in added_cols:
        query_copy['select'].append({'value': col})

    return query_copy
