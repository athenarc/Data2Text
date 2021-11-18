import pandas as pd
import requests
from settings import read_settings_file
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

BACKEND_HOST = read_settings_file()['BACKEND_HOST']  # back
BACKEND_PORT = read_settings_file()['BACKEND_PORT']  # 4557


@retry(wait=wait_fixed(5), stop=stop_after_attempt(15), retry=retry_if_exception_type(ConnectionError))
def get_table_names():
    try:
        tables = requests.get(f"http://{BACKEND_HOST}:{BACKEND_PORT}/tables")
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to backend on http://{BACKEND_HOST}:{BACKEND_PORT}.") from e
    return tables.json()['tables']


@retry(wait=wait_fixed(5), stop=stop_after_attempt(15), retry=retry_if_exception_type(ConnectionError))
def preview_table(table_name, table_canvas):
    try:
        table_sample = requests.get(f"http://{BACKEND_HOST}:{BACKEND_PORT}/tables/{table_name}").json()['table_sample']
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to backend on http://{BACKEND_HOST}:{BACKEND_PORT}.") from e
    cols = table_sample['header']
    rows = table_sample['row']

    df = pd.DataFrame(rows, columns=cols)
    table_canvas.dataframe(df)


@retry(wait=wait_fixed(5), stop=stop_after_attempt(15), retry=retry_if_exception_type(ConnectionError))
def explain_query(query):
    try:
        nl_res = requests.post(f"http://{BACKEND_HOST}:{BACKEND_PORT}/explain_query", json={"query": query})
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to backend on http://{BACKEND_HOST}:{BACKEND_PORT}.") from e
    return nl_res.json()['explanation']
