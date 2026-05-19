
import streamlit as st
from src.pipeline import generate_sql

st.set_page_config(page_title="SQLQueryAI")

st.title("SQLQueryAI")

user_query = st.text_area("Enter Natural Language Query")

if st.button("Generate SQL"):
    if user_query:
        sql = generate_sql(user_query)
        st.code(sql, language="sql")
