import streamlit as st
from api_calls import explain_query, get_table_names, preview_table

st.set_page_config(page_title='QR2T',
                   page_icon='favicon.png')

st.title('Query Results to Text')
selected_table = st.sidebar.selectbox('Choose a table:', get_table_names(), index=0)

show_preview = st.sidebar.checkbox("Preview Table", value=True)
if show_preview:
    st.markdown("**Table preview**")
    table_preview = st.empty()
    preview_table(selected_table, table_preview)

st.text("")
st.text("")


col1, col2 = st.columns([1.5, 1])
with col1:
    st.markdown("**Input Query**")
    input_query = st.text_area("", value="SELECT start_year, end_year FROM projects WHERE acronym='OPTIMALT'")

with col2:
    st.markdown("**Explain the query in NL (Optional)**")
    nl_query = st.text_area("", value="When did the project OPTIMALT started and ended?")


query_explanation = ""
explanation_area = st.empty()
if st.button("Execute"):
    with st.spinner('Executing...'):
        query_explanation = explain_query(input_query, nl_query)

if query_explanation != "":
    st.markdown(f"Results verbalisation: **{query_explanation}**")
