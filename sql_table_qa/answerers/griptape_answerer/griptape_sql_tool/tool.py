import random
from griptape.artifacts import TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal, Optional

from sql_table_qa.dbutils.database_connector import DatabaseConnector


connect_methods = DatabaseConnector.get_methods_info()


class DatabaseQueryTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.connector = DatabaseConnector()

    @activity(config={
        "description": connect_methods.get("execute_sql").get("desc", ""),
        "schema": Schema({
            Literal("sql", description="sql"): str
        })
    })
    def execute_sql(self, params: dict) -> TextArtifact:
        result = self.connector.execute_sql(**params["values"])
        return TextArtifact(str(result))

    @activity(config={
        "description": connect_methods.get("get_methods_info").get("desc", ""),
        "schema": Schema({})
    })
    def get_methods_info(self, params: dict) -> TextArtifact:
        result = self.connector.get_methods_info()
        return TextArtifact(str(result))

    @activity(config={
        "description": connect_methods.get("get_methods_info_string").get("desc", ""),
        "schema": Schema({})
    })
    def get_methods_info_string(self, params: dict) -> TextArtifact:
        result = self.connector.get_methods_info_string()
        return TextArtifact(str(result))

    @ activity(config={
        "description": connect_methods.get("get_table_names_and_description").get("desc", ""),
        "schema": Schema({})
    })
    def get_table_names_and_description(self, params: dict) -> TextArtifact:
        result = self.connector.get_table_names_and_description()
        return TextArtifact(str(result))

    @activity(config={
        "description": connect_methods.get("get_table_schema").get("desc", ""),
        "schema": Schema({
            Literal("table_name", description="table_name"): str
        })
    })
    def get_table_schema(self, params: dict) -> TextArtifact:
        result = self.connector.get_table_schema(**params["values"])
        return TextArtifact(str(result))

    @activity(config={
        "description": connect_methods.get("validate_sql").get("desc", ""),
        "schema": Schema({
            Literal("sql", description="sql of type str)"): str
        })
    })
    def validate_sql(self, params: dict) -> TextArtifact:
        result = self.connector.validate_sql(**params["values"])
        return TextArtifact(str(result))
