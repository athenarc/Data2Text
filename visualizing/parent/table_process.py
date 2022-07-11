import re
import string
from typing import List, Tuple


def parse_source(source: str) -> List[Tuple[str, str]]:
    source = source + "<" # Trick for the regex to work
    # Get the title
    title = re.search(r"<table> (.*?) <col", source).group(1)

    # Get the cell columns names, values
    col_values = re.findall(r"\d> .*? \| .*? \| (.*?) <", source)
    col_names = re.findall(r"\d> (.*?) \| .*? \| .*? <", source)

    if len(col_names) != len(col_values):
        raise ValueError(f"Could not parse source: {source}")

    ret_list = list(zip(col_names, col_values))
    ret_list.append(("title", title))

    return ret_list


def tokenize_table(table):
    tokenized_table = []
    for col_name, col_value in table:
        tokenized_table.append((
            col_name.lower().translate(str.maketrans('', '', string.punctuation)).split(),
            col_value.lower().translate(str.maketrans('', '', string.punctuation)).split()
        ))

    return tokenized_table


def tables_to_parent_format(sources):
    ret_tables = []
    for source in sources:
        ret_tables.append(
            tokenize_table(parse_source(source))
        )

    return ret_tables
