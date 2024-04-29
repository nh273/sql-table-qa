from openai import OpenAI
from CONSTANTS import ROOT_DIR, BOT, USER


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
