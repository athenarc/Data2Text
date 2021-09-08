import pandas as pd
import requests

HOST = "127.0.0.1"
PORT = 4557


def get_table_names():
    try:
        tables = requests.get(f"http://{HOST}:{PORT}/tables")
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to backend on http://{HOST}:{PORT}.") from e
    return tables.json()['tables']


def preview_table(table_name, table_canvas):
    try:
        table_sample = requests.get(f"http://{HOST}:{PORT}/tables/{table_name}").json()['table_sample']
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to backend on http://{HOST}:{PORT}.") from e
    cols = table_sample['header']
    rows = table_sample['row']

    df = pd.DataFrame(rows, columns=cols)
    table_canvas.table(df)


def explain_query(query):
    try:
        nl_res = requests.post(f"http://{HOST}:{PORT}/explain_query", json={"query": query})
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to backend on http://{HOST}:{PORT}.") from e
    return nl_res.json()['explanation']
