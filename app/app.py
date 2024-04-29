import os
from dotenv import dotenv_values
from collections import deque
import streamlit as st
from sql_table_qa.answerers.langchain_answerer.langchain_naive_answerer import LangchainNaiveAnswerer
from openai import OpenAI
from CONSTANTS import ROOT_DIR


config = {**dotenv_values(f"{ROOT_DIR}/configs/local.env")}
os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
client = OpenAI()


answerer = LangchainNaiveAnswerer()
# Streamlit UI
st.title("LangChain SQL Query Answering System")
BOT = "assistant"
USER = "user"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_sql" not in st.session_state:
    st.session_state.current_sql = ""

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def submit_sql(sql: str):
    st.info(f"{sql} is being executed.")
    st.session_state.current_sql = sql
    result = answerer.call(st.session_state.current_sql)
    q = deque(result)
    with st.chat_message(BOT):
        while q:
            msg = q.popleft()
            st.session_state.messages.append(
                {"role": BOT, "content": msg}
            )


def get_bot_response(response) -> str:
    return response.choices[0].message.content


def render_sql_editor():
    with st.sidebar:
        with st.form(key="SQL"):
            text_area_content = st.text_area(
                "sql_query", value=st.session_state["current_sql"], key="sql_query_text_area")
            st.form_submit_button(
                "Execute", on_click=submit_sql, kwargs={'sql': text_area_content})


render_sql_editor()
if user_input := st.chat_input("Chat:"):
    st.session_state.messages.append({"role": USER, "content": user_input})
    with st.chat_message(USER):
        st.write(user_input)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """You are a helpful assistant, expert sqlite user and data analyst.
             You attempt to answer user questions about the Chinook database using SQL queries.
             You can also ask clarifying questions if needed. You can provide insight from SQL query answers.
             You can also answer politely if the answer cannot be found in the database.
             You will only write an SQL query when you know the query is good.
             It is very important that you enclose SQL keywords in triple backticks (```) to avoid confusion."""},
            {"role": USER, "content": user_input}
        ]
    )
    with st.chat_message(BOT):
        msg = get_bot_response(response)
        if "```" in msg:
            code = msg.split("```")[1].replace("\n", " ")
            st.session_state.current_sql = code
        st.write(msg)
        st.session_state.messages.append(
            {"role": BOT, "content": msg}
        )
    st.rerun()
