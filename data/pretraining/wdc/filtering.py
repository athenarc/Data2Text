import glob
import gzip
import json

from tqdm import tqdm


def get_tables(table_paths, with_tqdm):
    for table_path in tqdm(table_paths, disable=with_tqdm):
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


def is_horizontal(table) -> bool:
    return table['tableOrientation'] == 'HORIZONTAL'


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


def get_filtered_tables(table_paths, disable_tqdm):
    filtered_tables = [remove_extra_info(table)
                       for table in get_tables(table_paths, disable_tqdm)
                       if has_header(table) and
                       is_horizontal(table) and
                       has_rows(table) and
                       columns_non_empty(table) and
                       is_english(table) and
                       is_not_huge(table) and
                       has_title_or_page_title(table) and
                       title_is_not_huge(table) and
                       has_non_numeric_col_names(table, allowed_num_rate=0) and
                       does_not_belong_to_specific_case(table)]

    return filtered_tables


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
