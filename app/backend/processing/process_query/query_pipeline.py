import logging
from typing import List, Tuple

import mo_sql_parsing

from app.backend.db.DbInterface import DbInterface
from app.backend.db.SqliteController import SqliteController
from app.backend.processing.process_query import query_injectors
from app.backend.processing.process_query.clause_extractors import (
    find_from_tables, find_sel_cols, find_where_cols)
from app.backend.processing.process_query.difficulty_check import \
    difficulty_check_query


def execute_transformed_query(db_controller: DbInterface, raw_query: str):
    # We check if the original query has any errors
    logging.debug("Executing original query.")
    _ = db_controller.query_with_res_cols(raw_query)

    new_query_str, tables = transform_query(raw_query)
    query_res = db_controller.query_with_res_cols(new_query_str)

    return {"tables_name": tables, "col_names": query_res[1], "rows": query_res[0]}


def transform_query(raw_query: str) -> Tuple[str, str]:
    logging.debug(f"Original query: {raw_query}")
    raw_query = raw_query.replace('"', '\'')

    query = mo_sql_parsing.parse(raw_query)
    if not isinstance(query['select'], List):
        query['select'] = [query['select']]

    # This call will raise a DifficultyNotImplemented error if we do not pass the check
    # Currently we do not allow GROUP BY and nested queries
    difficulty_check_query(query)

    # Extract SELECT, FROM, WHERE clauses
    sel_cols = find_sel_cols(query['select'])
    tables = find_from_tables(query['from'])
    try:
        where_cols = find_where_cols(query['where'])
    except KeyError:
        where_cols = set()
    logging.debug(f"Select cols: {sel_cols}")
    logging.debug(f"Table: {tables}")
    logging.debug(f"Where cols: {where_cols}")

    # Inject in SELECT, WHERE clauses that do not appear in SELECT already
    # eg SELECT c1 FROM t1 WHERE c2=1 -> SELECT c1, c2 FROM t2 WHERE c2=1
    new_query = query_injectors.add_where_cols_to_sel(query, sel_cols, where_cols)

    # We currently inject LIMIT 1 to all queries since we cannot verbalise multiple rows
    new_query = query_injectors.add_limit_1(new_query)

    # Add aliases on column names in case of JOIN.
    # Eg. SELECT t1.c1, t2.c1 FROM table1 t1, table t2 ->
    # SELECT t1.c1 AS "table1 c1", t2.c1 AS "table2 c1" FROM table1 t1, table t2
    new_query = query_injectors.apply_join_aliases(new_query, tables)

    # Verbalise aggregates to a representation that is meaningful for a model trained on ToTTo
    # Eg. SELECT SUM(col1) FROM table1 -> SELECT SUM(col1) AS "sum of col1" FROM table1
    new_query = query_injectors.verbalise_aggregates(new_query, tables)

    # We transform back the Dict query representation to a string query
    new_query_str = mo_sql_parsing.format(new_query)
    logging.debug(f"Transformed query: {new_query_str}")

    return new_query_str, ", ".join(tables)


if __name__ == '__main__':
    sqlite_con = SqliteController("../../../../storage/app_data/tables.db")
    query_res2 = execute_transformed_query(sqlite_con, 'SELECT Name FROM Titanic WHERE PassengerId=1')
    print(query_res2)
