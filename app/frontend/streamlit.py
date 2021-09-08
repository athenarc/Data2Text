import pandas as pd
import requests
import streamlit as st

HOST = "127.0.0.1"
PORT = 4557


def get_table_names():
    tables = requests.get(f"http://{HOST}:{PORT}/tables")
    return tables.json()['tables']


def preview_table(table_name, table_canvas):
    table_sample = requests.get(f"http://{HOST}:{PORT}/tables/{table_name}").json()['table_sample']
    cols = table_sample['header']
    rows = table_sample['row']

    df = pd.DataFrame(rows, columns=cols)
    table_canvas.table(df)


def explain_query(query):
    nl_res = requests.post(f"http://{HOST}:{PORT}/explain_query", json={"query": query})
    return nl_res.json()['explanation']


st.title('Query Results to Text')
selected_table = st.sidebar.selectbox('Choose a table:', get_table_names(), index=0)

show_preview = st.sidebar.checkbox("Preview Table", value=True)
if show_preview:
    st.markdown("**Table preview**")
    table_preview = st.empty()
    preview_table(selected_table, table_preview)


st.markdown("**Input Query**")
input_query = st.text_area("", value="SELECT Name FROM titanic WHERE PassengerId=1")

query_explanation = ""
explanation_area = st.empty()
if st.button("Execute"):
    query_explanation = explain_query(input_query)
st.markdown(f"Query explanation: **{query_explanation}**")


if __name__ == '__main__':
    explain_query("SELECT Name FROM titanic WHERE PassengerId=1")
