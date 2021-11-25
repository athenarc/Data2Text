import logging
from typing import Dict, List, Optional, Set


def find_sel_cols(sel_clause: List) -> Set[str]:
    ret_cols = set()
    for clause in sel_clause:
        if is_aggregate(clause):
            continue  # We deal with aggregate select cols only when verbalising them
        elif is_distinct(clause):
            ret_cols = ret_cols.union(return_distinct_cols(clause))
        elif is_named_value(clause):
            ret_cols.add(clause['value'])
        elif is_star_select(clause):
            ret_cols.add("*")
        else:
            logging.warning(f"Cannot parse select clause {clause}")
            continue

    return ret_cols


def find_from_tables(from_clause) -> List[str]:
    if not isinstance(from_clause, List):
        from_clause = [from_clause]
    ret_tables = []
    for table in from_clause:
        if isinstance(table, Dict):
            if 'value' in table:
                # Table alias case
                ret_tables.append(table['value'])
            elif (join_type := find_join_type_in_from(table)) is not None:
                if isinstance(table[join_type], Dict):
                    # Join with alias
                    ret_tables.append(table[join_type]['value'])
                else:
                    # Simple join without alias
                    ret_tables.append(table[join_type])
            else:
                raise ValueError(f"Unexpected dict in FROM: {from_clause}.")
        elif isinstance(table, str):
            ret_tables.append(table)
        else:
            raise ValueError(f"Unexpected type in FROM: {from_clause}.")
    return ret_tables


def find_where_cols(where_clause: Dict) -> Set[str]:
    where_cols = set()

    def rec_find_cols(clause):
        if isinstance(clause, List):
            if isinstance(clause[0], str):
                if not is_join_column(clause[1]):
                    # We do not include columns that are used to join two tables
                    # They usually are ids that do not offer interpretable information.
                    where_cols.add(clause[0])
            else:
                for inner_clause in clause:
                    rec_find_cols(inner_clause)
        if isinstance(clause, dict):
            in_and_not_in_values_to_list(clause)
            for inner_clause in clause.values():
                rec_find_cols(inner_clause)

    rec_find_cols(where_clause)
    return where_cols


def find_group_by_cols(group_by_clause) -> Set[str]:
    group_by_cols = set()
    if isinstance(group_by_clause, Dict):
        group_by_clause = [group_by_clause]

    for col in group_by_clause:
        group_by_cols.add(col['value'])

    return group_by_cols


def is_aggregate(clause) -> bool:
    """ Clause is of type: {'value': {'count': 'col1'}} """
    aggregates = ["avg", "max", "min", "sum", "count"]
    if isinstance(clause, Dict):
        if isinstance(clause['value'], Dict):
            if any(aggr in clause['value'] for aggr in aggregates):
                return True
    return False


def is_named_value(clause) -> bool:
    """ Clause is of type: {'value': 'col1'} """
    if isinstance(clause, Dict):
        if not isinstance(clause['value'], Dict):
            return True
    return False


def is_star_select(clause) -> bool:
    """ Clause is of type: '*' """
    if isinstance(clause, str) and clause == "*":
        return True
    return False


def is_join_column(value) -> bool:
    """
    Weakly checks if this is a JOIN clause, eg. t1.id = t2.f_id.
    Issue: It does not consult the FROM clause and is based on trivial pattern matching.
    As a result the clause: "t1.c1 = This is. a value" will be considered as a JOIN clause.
    """
    try:
        if len(value.split('.')) == 2:
            return True
        else:
            return False
    except AttributeError:
        return False


def is_distinct(clause) -> bool:
    if isinstance(clause, Dict):
        return 'distinct' in clause['value']


def return_distinct_cols(clause) -> Set[str]:
    if isinstance(clause['value']['distinct'], Dict):
        return {clause['value']['distinct']['value']}
    else:
        return {col['value'] for col in clause['value']['distinct']}


def find_join_type_in_from(clause) -> Optional[str]:
    if 'join' in clause:
        return 'join'
    elif 'inner join' in clause:
        return 'inner join'
    elif 'left join' in clause:
        return 'left join'
    elif 'left outer join' in clause:
        return 'left outer join'
    elif 'right join' in clause:
        return 'right join'
    elif 'right outer join' in clause:
        return 'right outer join'
    elif 'full join' in clause:
        return 'full join'
    elif 'full outer join' in clause:
        return 'full outer join'
    else:
        return None


def in_and_not_in_values_to_list(clause) -> None:
    """
    In the case of the IN, NOT IN operators if the value has only one element then the final
    query contains: "col1 IN 'value1'" which is not valid SQL. We transform it to a list so as
    to be "col1 IN ('value1')".

    The clause is transformed inplace.
    """
    if 'in' in clause:
        operator = 'in'
    elif 'nin' in clause:
        operator = 'nin'
    else:
        return
    clause_dict = clause[operator][1].copy()
    clause[operator][1] = {
        k: [v] if not isinstance(v, list) else v
        for k, v in clause_dict.items()
    }
