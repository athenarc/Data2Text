import random
from typing import Tuple

from nltk.tokenize import word_tokenize


def calculate_token_overlap(text, row):
    text_tokens = word_tokenize(text)

    # We want the text to be at least 8 tokens so as it resembles real text
    if len(row) == 0 or len(text_tokens) < 8:
        return 0

    token_set = set(text_tokens)
    row_set = set(row)

    return len(token_set.intersection(row_set)) / min(len(text_tokens), len(row_set))


def find_rows_with_high_overlap(table, text_position="textBeforeTable", threshold=0.4):
    return [(row, table[text_position]) for row in table['relation'][1:]  # Skip the header
            if calculate_token_overlap(table[text_position], row) > threshold]


def pick_row_and_section(table) -> Tuple[str, str]:
    # Prefer a row with high overlap with textBefore or textAfter if it exists
    rows_before = find_rows_with_high_overlap(table, text_position="textBeforeTable", threshold=0.4)
    rows_after = find_rows_with_high_overlap(table, text_position="textAfterTable", threshold=0.4)

    if len(rows_after) != 0:
        row = rows_after[0][0]
        section = rows_after[0][1]
    elif len(rows_before) != 0:
        row = rows_before[0][0]
        section = rows_before[0][1]
    else:
        row = random.choice(table['relation'][1:])
        section = ""

    return row, section
