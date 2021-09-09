import re
from typing import Dict, List, Tuple

from app.backend.sqlite_interface import SqliteController


class DifficultyNotImplemented(NotImplementedError):
    pass


def find_cols(clause: str, all_cols: List[str]) -> List[str]:
    return [col for col in all_cols if re.search(f"{col}(?!\\w)", clause)]


def cols_added_to_sel(sel_cols: List[str], where_cols: List[str]) -> List[str]:
    sel_cols = set(sel_cols)
    where_cols = set(where_cols)

    return list(where_cols.difference(sel_cols))


def find_query_clauses(query: str) -> Tuple[str, str, str]:
    lowered_query = query.lower()
    sel_clause_start = lowered_query.index("select") + len("select") + 1
    sel_clause_end = lowered_query.index("from") - 1

    from_clause_start = lowered_query.index("from") + len("from") + 1
    try:
        # The query might not have a where clause
        from_clause_end = lowered_query.index("where") - 1
    except ValueError:
        return query[sel_clause_start:sel_clause_end], query[from_clause_start:], ""

    where_clause_start = lowered_query.index("where") + len("where") + 1

    return query[sel_clause_start:sel_clause_end], query[from_clause_start:from_clause_end], \
           query[where_clause_start:]


def add_where_cols_to_sel(sel_clause, where_clause, all_cols) -> str:
    # We assume that we are in the easy case of having just one table
    if len(all_cols) > 1:
        raise DifficultyNotImplemented("JOIN difficulty not yet implemented.")
    first_table_cols: List[str] = all_cols[0]

    added_cols = cols_added_to_sel(find_cols(sel_clause, first_table_cols),
                                   find_cols(where_clause, first_table_cols))

    for added_col in added_cols:
        sel_clause += f", {added_col}"

    return sel_clause


def execute_query_with_added_sel_cols(sqlite_controller: SqliteController, query):
    # This call will raise a DifficultyNotImplemented error if we do not pass the check
    difficulty_check_query(query)

    sel_clause, from_clause, where_clause = find_query_clauses(query)
    tables = from_clause.replace(' ', '').split(',')

    if "*" not in sel_clause:  # Case where we SELECT * FROM ... (does not take into account aggregating, COUNT(*))
        all_table_cols = [sqlite_controller.get_table_cols(table_name) for table_name in tables]
        new_sel_clause = add_where_cols_to_sel(sel_clause, where_clause, all_table_cols)
        new_query = f"SELECT {new_sel_clause} FROM {from_clause} "
        new_query += f"WHERE {where_clause}" if where_clause != "" else ""
        print(new_query)
    else:
        new_query = query

    query_res = sqlite_controller.connect_and_query_with_desc(new_query)

    return {"tables_name": tables, "col_names": query_res[1], "rows": query_res[0]}


def create_metadata(table_name, nl_query="") -> str:
    page_title = f"<page_title> {table_name} </page_title>"
    section_title = f"<section_title> {nl_query if nl_query != '' else table_name} </section_title>"

    return page_title + " " + section_title


def create_cell(col_name: str, col_value: str) -> str:
    return f"<cell> {col_value} <col_header> {col_name} </col_header> </cell>"


def query_results_to_totto(query_results: Dict[str, str]):
    metadata = create_metadata(query_results['tables_name'][0])
    table_cells_str = ""

    if len(query_results['rows']) > 1:
        raise DifficultyNotImplemented("Query results with multiple rows cannot be explained yet.")

    for row in query_results['rows']:
        for header, val in zip(query_results['col_names'], row):
            table_cells_str += create_cell(header, val) + " "

    return f"{metadata} <table> {table_cells_str}</table>"


def difficulty_check_query(query: str) -> bool:
    lowered_query = query.lower()
    """ Currently we do not allow aggregating, group, nested queries """
    if "group by" in lowered_query:
        raise DifficultyNotImplemented("GROUP BY difficulty not implemented yet.")
    elif "count" in lowered_query or "avg" in lowered_query \
            or "max" in lowered_query or "min" in lowered_query:
        raise DifficultyNotImplemented("Aggregators difficulty not implemented yet.")
    elif len(lowered_query.split("select")) > 2:
        raise DifficultyNotImplemented("Nested queries difficulty not implemented yet.")
    return True


if __name__ == '__main__':
    sqlite_con = SqliteController("../../storage/datasets/wiki_sql/raw/train.db")
    query_res2 = execute_query_with_added_sel_cols(sqlite_con, 'SELECT Name FROM Titanic WHERE PassengerId=1')
    print(query_results_to_totto(query_res2))
