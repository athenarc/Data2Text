import random
from typing import Iterator, Set, Tuple

from nltk.tokenize import word_tokenize


def find_overlapping_tokens(text, row) -> Set[str]:
    text_tokens = word_tokenize(text)

    # We want the text to be at least 8 tokens so as it resembles real text
    if len(row) == 0 or len(text_tokens) < 8:
        return set()

    token_set = set(text_tokens)
    row_set = set(row)

    return token_set.intersection(row_set)


def pick_row_and_section(table, threshold=1) -> Iterator[Tuple[str, str]]:
    joined_texts = table['textBeforeTable'] + table['textAfterTable']
    for row in table['relation'][1:]:
        for sent in joined_texts:
            if len(find_overlapping_tokens(sent, row)) >= threshold:
                yield row, sent

    # No overlapping row-sentence pair found
    yield random.choice(table['relation'][1:]), ""


# def find_rows_with_high_overlap(table, text_position="textBeforeTable", threshold=1):
#     return [(row, table[text_position]) for row in table['relation'][1:]  # Skip the header
#             if len(find_overlapping_tokens(table[text_position], row)) > threshold]


# def pick_row_and_section(table) -> Tuple[str, str]:
#     # Prefer a row with high overlap with textBefore or textAfter if it exists
#     rows_before = find_rows_with_high_overlap(table, text_position="textBeforeTable", threshold=1)
#     rows_after = find_rows_with_high_overlap(table, text_position="textAfterTable", threshold=1)
#
#     if len(rows_after) != 0:
#         row = rows_after[0][0]
#         section = rows_after[0][1]
#     elif len(rows_before) != 0:
#         row = rows_before[0][0]
#         section = rows_before[0][1]
#     else:
#         row = random.choice(table['relation'][1:])
#         section = ""
#
#     return row, section
