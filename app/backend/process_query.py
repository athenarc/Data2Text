import re
from typing import List, Tuple


def find_cols(clause: str, all_cols: List[str]) -> List[str]:
    return [col for col in all_cols if re.search(f"{col.lower()}(?!\\w)", clause)]


def cols_added_to_sel(sel_cols: List[str], where_cols:  List[str]) -> List[str]:
    sel_cols = set(sel_cols)
    where_cols = set(where_cols)

    return list(where_cols.difference(sel_cols))


def find_query_clauses(query: str) -> Tuple[str, str, str]:
    lowered_query = query.lower()
    sel_clause_start = lowered_query.find("select") + len("select") + 1
    sel_clause_end = lowered_query.find("from") - 1

    from_clause_start = lowered_query.find("from") + len("from") + 1
    from_clause_end = lowered_query.find("where") - 1

    if from_clause_end == -2:
        return query[sel_clause_start:sel_clause_end], query[from_clause_start:], ""

    where_clause_start = lowered_query.find("where") + len("where") + 1
    # where_clause_end = -1

    return query[sel_clause_start:sel_clause_end], query[from_clause_start:from_clause_end], \
           query[where_clause_start:]
