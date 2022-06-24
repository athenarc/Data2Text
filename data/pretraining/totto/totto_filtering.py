import re


def table_has_empty_column(table):
    if re.search(r"<col\d>\s\s\|", table) is None:
        return True
    return False
