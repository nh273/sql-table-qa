import os
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


def create_sql_query_from_question(question: str) -> str:
    return query_writer.invoke({"question": question})


def answer_question(question: str, query: str, result: str) -> str:
    return answer_writer.invoke({"question": question, "query": query, "result": result})


# Streamlit UI
st.title("LangChain SQL Query Answering System")

if question := st.chat_input("Enter your question:"):
    query = create_sql_query_from_question(question)
    result = execute_sql(query)
    answer = answer_question(question, query, result)
    st.code(query, language="sql")
    st.write(answer)
