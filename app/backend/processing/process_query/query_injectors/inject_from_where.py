from typing import Dict, Set

from app.backend.processing.process_query.clause_extractors import \
    is_star_select


def add_where_cols_to_sel(query: Dict, sel_cols: Set[str], where_cols: Set[str]) -> Dict:
    if is_star_select(query['select'][0]):
        # The user explicitly selected all the columns. No need to add anything.
        return query
    added_cols = where_cols.difference(sel_cols)

    for col in added_cols:
        query['select'].append({'value': col})

    return query
