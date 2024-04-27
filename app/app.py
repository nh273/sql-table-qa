import os
import ast
import streamlit as st
from operator import itemgetter
from dotenv import dotenv_values
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from sql_table_qa.answerers.langchain_answerer.langchain_sql_connector import execute_sql
from CONSTANTS import ROOT_DIR


config = {**dotenv_values(f"{ROOT_DIR}/configs/local.env")}

os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
# Initialize your database and language model objects here
db = SQLDatabase.from_uri("sqlite:///./data/Chinook.db")
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# Tools and chain setup
# TODO: this can be easily integrated with our custom db connector
query_writer = create_sql_query_chain(llm, db)
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
)

answer_writer = answer_prompt | llm | StrOutputParser()


@st.cache_data
def create_sql_query_from_question(question: str) -> str:
    return query_writer.invoke({"question": question})


@st.cache_data
def answer_question(question: str, query: str, result: str) -> str:
    return answer_writer.invoke({"question": question, "query": query, "result": result})


# Streamlit UI
st.title("LangChain SQL Query Answering System")
BOT = "bot"
USER = "user"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message:
            st.code(message["sql"], language="sql")
        if "result" in message:
            try:
                st.dataframe(message["result"])
            except Exception as e:
                st.write(e)


def is_valid_parsed_result(parsed_result: any) -> bool:
    return parsed_result and isinstance(parsed_result, list) and isinstance(parsed_result[0], dict)


if question := st.chat_input("Enter your question:"):
    st.session_state.messages.append({"role": USER, "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    query = create_sql_query_from_question(question)
    result = execute_sql(query)
    answer = answer_question(question, query, result)
    try:
        parsed_result = ast.literal_eval(result)
    except Exception as e:
        parsed_result = result
    with st.chat_message("assistant"):
        if is_valid_parsed_result(parsed_result):
            st.dataframe(parsed_result)
        if query:
            st.code(query, language="sql")
        st.write(answer)
    st.session_state.messages.append(
        {"role": BOT, "content": answer, "sql": query,
            "result": parsed_result if is_valid_parsed_result(parsed_result) else None}
    )
