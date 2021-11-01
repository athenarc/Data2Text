import json
import logging
from typing import Dict, List, Set

import mo_sql_parsing

from app.backend.db.DbInterface import DbInterface


class DifficultyNotImplemented(NotImplementedError):
    pass


def add_where_cols_to_sel(query: Dict, added_cols: Set[str]) -> Dict:
    # We assume that we are in the easy case of having just one table
    query_copy = query.copy()
    for col in added_cols:
        query_copy['select'].append({'value': col})

    return query_copy


def execute_query_with_added_sel_cols(sqlite_controller: DbInterface, raw_query):
    new_query_str, tables = transform_query(raw_query)
    query_res = sqlite_controller.query_with_res_cols(new_query_str)

    return {"tables_name": tables, "col_names": query_res[1], "rows": query_res[0]}


def transform_query(raw_query):
    logging.debug(f"Original query: {raw_query}")
    query = mo_sql_parsing.parse(raw_query)
    if not isinstance(query['select'], List):
        query['select'] = [query['select']]

    # This call will raise a DifficultyNotImplemented error if we do not pass the check
    # difficulty_check_query(query)

    sel_cols = find_sel_cols(query['select'])
    tables = find_from_tables(query['from'])
    try:
        where_cols = find_where_cols(query['where'])
    except KeyError:
        where_cols = set()

    if "*" not in sel_cols:
        added_cols = where_cols.difference(sel_cols)
        new_query = add_where_cols_to_sel(query, added_cols)
    else:
        new_query = query

    # We currently add LIMIT 1 to all queries since we cannot verbalise multiple rows
    new_query = add_limit_1(new_query)

    # Add aliases on column names in case of JOIN.
    # Eg. SELECT t1.c1, t2.c1 FROM table1 t1, table t2 ->
    # SELECT t1.c1 AS "table1 c1", t2.c1 AS "table2 c1" FROM table1 t1, table t2
    new_query = apply_join_aliases(new_query, tables)

    # We transform back the Dict query representation to a string query
    new_query_str = mo_sql_parsing.format(new_query)
    logging.debug(f"Transformed query: {new_query_str}")

    return new_query_str, ", ".join(tables)


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


def find_from_tables(from_clause) -> List[str]:
    print(from_clause)
    if isinstance(from_clause, str):
        return [from_clause]
    elif isinstance(from_clause, List):
        ret_tables = []
        for table in from_clause:
            if isinstance(table, Dict):
                ret_tables.append(table['value'])
            else:
                ret_tables.append(table)
        return ret_tables
    elif isinstance(from_clause, Dict):
        return [from_clause['value']]
    else:
        raise TypeError("Unexpected type when extracting FROM tables.")


def find_sel_cols(sel_clause: List) -> Set[str]:
    ret_cols = set()
    for clause in sel_clause:
        try:
            ret_cols.add(clause['value'])
        except TypeError:
            ret_cols.add(clause)

    return ret_cols


def add_limit_1(parsed_query):
    parsed_query["limit"] = 1
    return parsed_query


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


if __name__ == '__main__':
    sqlite_con = SqliteController("../../../storage/app_data/tables.db")
    query_res2 = execute_query_with_added_sel_cols(sqlite_con, 'SELECT Name FROM Titanic WHERE PassengerId=1')
    print(query_res2)
