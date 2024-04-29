import os
from dotenv import dotenv_values
from collections import deque
import streamlit as st
from sql_table_qa.answerers.langchain_answerer.langchain_naive_answerer import LangchainNaiveAnswerer
from openai import OpenAI
from CONSTANTS import ROOT_DIR, BOT, USER

# naive inclusion of last 20 messages as context
# TODO: Implement more sophisticated context management using tokens count
MAX_CONTEXT_LENGTH = 20
config = {**dotenv_values(f"{ROOT_DIR}/configs/local.env")}
os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
client = OpenAI()


sql_answerer = LangchainNaiveAnswerer()
# Streamlit UI
st.title("LangChain SQL Query Answering System")

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
    result = sql_answerer.call(st.session_state.current_sql)
    q = deque(result)
    while q:
        msg = q.popleft()
        st.session_state.messages.append(
            {"role": BOT, "content": msg}
        )


def render_sql_editor():
    with st.sidebar:
        with st.form(key="SQL"):
            text_area_content = st.text_area(
                "sql_query", value=st.session_state["current_sql"], key="sql_query_text_area")
            st.form_submit_button(
                "Execute", on_click=submit_sql, kwargs={'sql': text_area_content})


class OpenaiAnswerer:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI()
        self.system_prompt = """You are a helpful assistant, expert sqlite user and data analyst.
        You attempt to answer user questions about the Chinook database using SQL queries.
        You can also ask clarifying questions if needed. You can provide insight from SQL query answers.
        You can also answer politely if the answer cannot be found in the database.
        You will only write an SQL query when you know the query is good.
        It is very important that you enclose SQL keywords in triple backticks (```) to avoid confusion."""
        self.model = model

    def get_response(self, message: str, context: list[dict]):
        messages_to_send = [{"role": "system", "content": self.system_prompt}]
        if context:
            messages_to_send += context
        messages_to_send.append({"role": USER, "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages_to_send
        )
        return response

    def get_text_content_response(self, response) -> str:
        return response.choices[0].message.content

    def get_chat_response(self, message: str, context: list[dict]) -> str:
        response = self.get_response(message, context)
        return self.get_text_content_response(response)


general_answerer = OpenaiAnswerer()
render_sql_editor()
if user_input := st.chat_input("Chat:"):
    st.session_state.messages.append({"role": USER, "content": user_input})
    with st.chat_message(USER):
        st.write(user_input)

    response = general_answerer.get_chat_response(
        message=user_input,  context=st.session_state.messages[:-MAX_CONTEXT_LENGTH])
    with st.chat_message(BOT):
        if "```" in response:
            code = response.split("```")[1].replace("\n", " ").strip()
            st.session_state.current_sql = code
        st.write(response)
        st.session_state.messages.append(
            {"role": BOT, "content": response}
        )
    st.rerun()
