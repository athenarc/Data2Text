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
