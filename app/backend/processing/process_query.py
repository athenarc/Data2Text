import json
import logging
from typing import Dict, List, Set

import mo_sql_parsing

from app.backend.model.sqlite_interface import SqliteController


class DifficultyNotImplemented(NotImplementedError):
    pass


def add_where_cols_to_sel(query: Dict, added_cols: Set[str]) -> Dict:
    # We assume that we are in the easy case of having just one table
    query_copy = query.copy()
    for col in added_cols:
        query_copy['select'].append({'value': col})

    return query_copy


def execute_query_with_added_sel_cols(sqlite_controller: SqliteController, raw_query):
    new_query_str, tables = transform_query(raw_query)
    query_res = sqlite_controller.connect_and_query_with_desc(new_query_str)

    return {"tables_name": tables, "col_names": query_res[1], "rows": query_res[0]}


def transform_query(raw_query):
    logging.debug(f"Original query: {raw_query}")
    query = mo_sql_parsing.parse(raw_query)
    if not isinstance(query['select'], List):
        query['select'] = [query['select']]

    # This call will raise a DifficultyNotImplemented error if we do not pass the check
    difficulty_check_query(query)

    sel_cols = find_sel_cols(query['select'])
    tables = query['from']
    try:
        where_cols = find_where_cols(query['where'])
    except KeyError:
        where_cols = set()

    if "*" not in sel_cols:
        added_cols = where_cols.difference(sel_cols)
        new_query = add_where_cols_to_sel(query, added_cols)
    else:
        new_query = query
    new_query_str = mo_sql_parsing.format(new_query)
    logging.debug(f"Transformed query: {new_query_str}")

    return new_query_str, tables


def difficulty_check_query(query: Dict) -> bool:
    jsoned_query = json.dumps(query)
    """ Currently we do not allow aggregating, group, nested queries """
    if "groupby" in query:
        raise DifficultyNotImplemented("GROUP BY difficulty not implemented yet.")
    elif check_aggr_exists(query['select']):
        raise DifficultyNotImplemented("Aggregators difficulty not implemented yet.")
    elif len(jsoned_query.split("select")) > 2:
        raise DifficultyNotImplemented("Nested queries difficulty not implemented yet.")
    return True


def check_aggr_exists(sel_clause: List) -> bool:
    aggr_funcs = {"avg", "sum", "max", "min", "count"}
    aggr_exists = False
    for inner_sel in sel_clause:
        try:
            aggr_exists = list(inner_sel['value'].keys())[0] in aggr_funcs
        except (AttributeError, TypeError):
            continue

    return aggr_exists


def find_where_cols(where_clause: Dict) -> Set[str]:
    where_cols = set()

    def rec_find_cols(clause):
        if isinstance(clause, List):
            if isinstance(clause[0], str):
                where_cols.add(clause[0])
            else:
                for inner_clause in clause:
                    rec_find_cols(inner_clause)
        if isinstance(clause, dict):
            for inner_clause in clause.values():
                rec_find_cols(inner_clause)

    rec_find_cols(where_clause)
    return where_cols


def find_sel_cols(sel_clause: List) -> Set[str]:
    ret_cols = set()
    for clause in sel_clause:
        try:
            ret_cols.add(clause['value'])
        except TypeError:
            ret_cols.add(clause)

    return ret_cols


if __name__ == '__main__':
    sqlite_con = SqliteController("../../storage/datasets/wiki_sql/raw/train.db")
    query_res2 = execute_query_with_added_sel_cols(sqlite_con, 'SELECT Name FROM Titanic WHERE PassengerId=1')
    print(query_res2)
