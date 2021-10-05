import re
from typing import List, Tuple


def parse_source(source: str) -> List[Tuple[str, str]]:
    # Get the title
    title = re.search(r"<page_title> (.*?) </page_title>", source).group(1)

    # Get the cell columns names, values
    col_values = re.findall(r"<cell> (.*?) <col_header>", source)
    col_names = re.findall(r"<col_header> (.*?) </col_header>", source)

    print(col_values)
    print(col_names)
    if len(col_names) != len(col_values):
        raise ValueError(f"Could not parse source: {source}")

    ret_list = list(zip(col_names, col_values))
    ret_list.append(("title", title))

    return ret_list


def tokenize_table(table):
    tokenized_table = []
    for col_name, col_value in table:
        tokenized_table.append((
            col_name.lower().split(),
            col_value.lower().split()
        ))

    return tokenized_table


def tables_to_parent_format(sources):
    ret_tables = []
    for source in sources:
        ret_tables.append(
            tokenize_table(parse_source(source))
        )

    return ret_tables
