from typing import Dict, List, Set


def find_sel_cols(sel_clause: List) -> Set[str]:
    ret_cols = set()
    for clause in sel_clause:
        if is_aggregate(clause):
            continue  # Currently we do not consider an aggregated column as selected
            # ret_cols.add(list(clause['value'].values())[0])
        elif is_named_value(clause):
            ret_cols.add(clause['value'])
        elif is_star_select(clause):
            ret_cols.add("*")
        else:
            raise ValueError(f"Cannot parse select clause {clause}")

    return ret_cols


def find_from_tables(from_clause) -> List[str]:
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


def is_aggregate(clause) -> bool:
    """ Clause is of type: {'value': {'count': 'col1'}} """
    if isinstance(clause, Dict):
        if isinstance(clause['value'], Dict):
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
