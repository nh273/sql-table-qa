"""An answerer that will always assume the user question is correct and fully formed.
Will always attempt SQL execution and return the result or an error message.
Will not attempt to correct it's own faulty query."""
import os
import ast
import pandas as pd
from dotenv import dotenv_values
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import streamlit as st
from sql_table_qa.answerers.langchain_answerer.langchain_sql_connector import execute_sql
from CONSTANTS import ROOT_DIR


class LangchainNaiveAnswerer:
    def __init__(self):
        config = {**dotenv_values(f"{ROOT_DIR}/configs/local.env")}
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
        # Initialize your database and language model objects here
        self.db = SQLDatabase.from_uri(f"sqlite:///{ROOT_DIR}/data/Chinook.db")
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        # Tools and chain setup
        # TODO: this can be easily integrated with our custom db connector
        self.query_writer = create_sql_query_chain(self.llm, self.db)
        self.answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

            Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
        )
        self.answer_writer = self.answer_prompt | self.llm | StrOutputParser()

    def create_sql_query_from_question(self, question: str) -> str:
        return self.query_writer.invoke({"question": question})

    def answer_question(self, question: str, query: str, result: str) -> str:
        return self.answer_writer.invoke({"question": question, "query": query, "result": result})

    def call(self, msg: str) -> list[any]:
        query = self.create_sql_query_from_question(msg)
        result = execute_sql(query)
        answer = self.answer_question(msg, query, result)
        try:
            parsed_result = pd.DataFrame(ast.literal_eval(result))
        except Exception as e:
            print(e)
            parsed_result = result
        return [f"```\n{query}\n```", parsed_result, answer]
