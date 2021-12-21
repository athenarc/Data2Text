import glob
import gzip
import json


def get_tables(table_paths):
    for table_path in table_paths:
        with gzip.open(table_path, 'r') as f:
            for line in f:
                try:
                    yield json.loads(line)
                except UnicodeDecodeError:
                    continue


def is_english(table):
    return any(domain in table['url'] for domain in ['.com', '.eu', '.uk', '.net', '.org'])


## Filters ##
def has_header(table):
    return table['hasHeader']


def is_not_empty(table):
    return len(table['relation']) >= 2


def is_horizontal(table):
    return table['tableOrientation'] == 'HORIZONTAL'


def is_not_huge(table):
    return len(table['relation']) < 50 and len(table['relation'][0]) < 15


def has_title_or_page_title(table):
    return table['title'] != '' or table['pageTitle'] != ''


def title_is_not_huge(table):
    if table['title'] != '' and len(table['title'].split()) < 5:
        return True
    elif table['pageTitle'] != '' and len(table['pageTitle'].split()) < 5:
        return True
    else:
        return False


def remove_extra_info(table):
    return {
        'relation': table['relation'],
        'title': table['title'],
        'pageTitle': table['pageTitle'],
        'textBeforeTable': table['textBeforeTable'],
        'textAfterTable': table['textAfterTable'],
    }


def get_filtered_tables(table_paths):
    filtered_tables = [table for table in get_tables(table_paths)
                       if has_header(table) and
                       is_not_empty(table) and
                       is_english(table) and
                       is_not_huge(table) and
                       has_title_or_page_title(table) and
                       title_is_not_huge(table)]

    return filtered_tables


if __name__ == '__main__':
    WDC_ORIGINAL_DIR = "storage/datasets/wdc/original/"
    WDC_FILTERED_DIR = "storage/datasets/wdc/filtered/"

    table_dirs = glob.glob(f"{WDC_ORIGINAL_DIR}*")

    for ind, table_dir in enumerate(table_dirs):
        print(f"Directory: {ind} / {len(table_dirs)}")
        table_paths = glob.glob(f"{table_dir}/*")

        filter_tables = get_filtered_tables(table_paths)

        # Store
        with open(WDC_FILTERED_DIR + table_dir.split('/')[-1] + '.json', 'w') as outfile:
            json.dump(filter_tables, outfile)

    print("DONE!")
