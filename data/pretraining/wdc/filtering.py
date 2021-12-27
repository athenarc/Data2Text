import glob
import gzip
import json
import re

from spacy.lang.en import English
from tqdm import tqdm


def get_tables(table_paths):
    for table_path in table_paths:
        with gzip.open(table_path, 'r') as f:
            for line in f:
                try:
                    yield json.loads(line)
                except UnicodeDecodeError:
                    continue


## Filters ##
def is_english(table):
    """ To make computation faster we do not perform an explicit language check. Instead, we check the url domain. """
    return any(domain in table['url'] for domain in ['.com', '.eu', '.uk', '.net', '.org'])


def has_header(table) -> bool:
    return table['hasHeader'] and table['headerPosition'] == 'FIRST_ROW'


def has_rows(table) -> bool:
    return len(table['relation']) >= 2


def columns_non_empty(table) -> bool:
    return not any(col == '' for col in table['relation'][0])


def is_vertical(table) -> bool:
    return table['tableOrientation'] == 'VERTICAL'


def is_not_huge(table) -> bool:
    return len(table['relation']) < 50 and len(table['relation'][0]) < 8


def has_title_or_page_title(table) -> bool:
    return table['title'] != '' or table['pageTitle'] != ''


def title_is_not_huge(table) -> bool:
    if table['title'] != '' and len(table['title'].split()) < 5:
        return True
    elif table['pageTitle'] != '' and len(table['pageTitle'].split()) < 5:
        return True
    else:
        return False


def has_non_numeric_col_names(table, allowed_num_rate=0.1) -> bool:
    columns = table['relation'][0]

    def is_numeric(col_name: str) -> bool:
        try:
            _ = float(col_name)
            return True
        except ValueError:
            return False

    numb_of_num_cols = sum([is_numeric(col_name) for col_name in columns])
    return True if numb_of_num_cols / len(columns) <= allowed_num_rate else False


def has_invalid_tokens(text):
    INVALID_CONTEXT_TOKENS = ['[', ']', '!', '{', '}', ';', '()', ');', '>', '<', '›']
    return any(
        token in text
        for token
        in INVALID_CONTEXT_TOKENS
    )


def does_not_belong_to_specific_case(table) -> bool:
    words = ['Player', 'Cart Icon', 'Username']

    return not any(table['relation'][0][0] == word for word in words)


def remove_extra_info(table):
    return {
        'relation': table['relation'],
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'textBeforeTable': table['textBeforeTable'],
        'textAfterTable': table['textAfterTable'],
    }


class ContextProcessor(object):
    """
    The preprocessing used for textBefore and textAfter by TaBERT
    https://github.com/facebookresearch/TaBERT/blob/74aa4a88783825e71b71d1d0fdbc6b338047eea9/preprocess/common_crawl.py
    """
    def __init__(self):
        nlp = English()  # just the language with no table_bert
        nlp.add_pipe("sentencizer")
        # nlp.add_pipe(sentencizer)

        self.nlp = nlp
        self.RE_HTML_TAG = re.compile('<.*?>.*?</.*?>')
        self.ALLOWED_SPECIAL_SYMBOLS = {'£', '°', '§', '€'}

    def clean_context(self, text):
        text = self.RE_HTML_TAG.sub('', text)
        text = text.replace('“', '\"').replace("”", '\"').replace('’', "'").replace('—', '-').replace('•', '')
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            return []

        if len(text.split()) == 1:
            return [text]

        text = self.nlp(text)
        valid_sents = []
        for sent in text.sents:
            if has_invalid_tokens(sent.text):
                continue

            non_ascii_char_count = sum(ord(c) >= 128 and c not in self.ALLOWED_SPECIAL_SYMBOLS for c in sent.text)
            if non_ascii_char_count >= 2:
                continue

            num_alpha = sum(w.is_ascii and w.is_alpha for w in sent)
            if num_alpha == 0:
                continue

            num_non_alpha = len(sent) - num_alpha  # sum(not w.is_alpha for w in sent)
            if num_non_alpha >= num_alpha:
                continue

            valid_sents.append(sent.text.strip())

        return valid_sents


def process_context(tables):
    context_processor = ContextProcessor()
    for table in tables:
        table['textBeforeTable'] = context_processor.clean_context(table['textBeforeTable'])
        table['textAfterTable'] = context_processor.clean_context(table['textAfterTable'])

    return tables


def transpose_table(table):
    # First drop the columns without a name
    table['relation'] = [col for col in table['relation'] if col[0] != '']

    table['relation'] = list(map(list, zip(*table['relation'])))
    return table


def get_filtered_tables(table_paths, disable_tqdm):
    transposed_tables = [transpose_table(table) for table in get_tables(table_paths)
                         if table['tableOrientation'] == 'HORIZONTAL']

    filtered_tables = [remove_extra_info(table)
                       for table in tqdm(transposed_tables, disable=disable_tqdm)
                       if has_header(table) and
                       has_rows(table) and
                       # columns_non_empty(table) and
                       is_english(table) and
                       is_not_huge(table) and
                       has_title_or_page_title(table) and
                       title_is_not_huge(table) and
                       has_non_numeric_col_names(table, allowed_num_rate=0) and
                       does_not_belong_to_specific_case(table)]

    # Currently, we only process the textBefore and textAfter
    processed_tables = process_context(filtered_tables)

    return processed_tables


def wdc_filtering(disable_tqdm=True):
    WDC_ORIGINAL_DIR = "storage/datasets/wdc/original/"
    WDC_FILTERED_DIR = "storage/datasets/wdc/filtered/"

    table_dirs = glob.glob(f"{WDC_ORIGINAL_DIR}*")
    total_tables = 0

    for ind, table_dir in enumerate(table_dirs):
        print(f"WDC | Filtering | Directory: {ind + 1} / {len(table_dirs)}")
        table_paths = glob.glob(f"{table_dir}/warc/*")

        filter_tables = get_filtered_tables(table_paths, disable_tqdm)

        # Store
        with open(WDC_FILTERED_DIR + table_dir.split('/')[-1] + '.json', 'w') as outfile:
            json.dump(filter_tables, outfile)

        total_tables += len(filter_tables)

    print(f"DONE! Final tables: {total_tables}.")


if __name__ == '__main__':
    wdc_filtering(disable_tqdm=False)
