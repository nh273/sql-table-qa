from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

from sql_table_qa.dbutils.database_connector import DatabaseConnector


connector = DatabaseConnector()


@tool
def execute_sql(sql: str) -> str:
    """Executes an SQL statement on the Chinook database and get back the results.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    try:
        result = connector.execute_sql(sql)
    except Exception as e:
        return str(e)
    return str(result)
