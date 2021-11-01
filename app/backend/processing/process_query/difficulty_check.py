import json
from typing import Dict, List


class DifficultyNotImplemented(NotImplementedError):
    pass


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
