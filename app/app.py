import os
import ast
from dotenv import dotenv_values
from collections import deque, namedtuple
import streamlit as st
from sql_table_qa.answerers.langchain_answerer.langchain_naive_answerer import LangchainNaiveAnswerer
from openai import OpenAI
from sql_table_qa.dbutils.database_connector import DatabaseConnector
from CONSTANTS import ROOT_DIR


config = {**dotenv_values(f"{ROOT_DIR}/configs/local.env")}
os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
client = OpenAI()


answerer = LangchainNaiveAnswerer()
tool_executor = DatabaseConnector()
SYSTEM_PROMPT = f"""You are a helpful assistant, expert sqlite user and data analyst.
You attempt to answer user questions about the data in the Chinook database using SQL queries.
This is the Chinook database schema:
{tool_executor.get_table_names_and_description()}
You will think step-by-step. You will first check the SQL query and then provide the answer.
You can also ask clarifying questions if needed. You can provide insight about the data from SQL query answers.
You can also answer politely if the answer cannot be found in the database.
IMPORTANT: Always show your reasoning and SQL query used to answer the question.
It is very important that you enclose SQL keywords in triple backticks (```) to avoid confusion."""

assistant = client.beta.assistants.create(
    instructions=SYSTEM_PROMPT,
    model="gpt-3.5-turbo",
    tools=DatabaseConnector.create_open_ai_assistant_tools()
)

# Streamlit UI
st.title("LangChain SQL Query Answering System")
BOT = "assistant"
USER = "user"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_sql" not in st.session_state:
    st.session_state.current_sql = ""


def get_text_content(message, allow_failure=False) -> str:
    """Get the text content from a message returned by the OpenAI Assistant API.

    Args:
        message (ChatMessage): openai.ChatMessage object.
        allow_failure (bool, optional): handles exceptions by
        returning the exception message as string or raises the exception.
        Defaults to False.

    Returns:
        str: _description_
    """
    try:
        return message.content[0].text.value
    except Exception as e:
        if allow_failure:
            raise e
        return str(e)


Message = namedtuple("Message", ["role", "content", "created_at"])
if st.session_state.messages:
    st.session_state.messages = sorted(
        st.session_state.messages, key=lambda x: x.created_at)
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message.role):
        try:
            st.write(get_text_content(message, allow_failure=True))
        except AttributeError:
            st.write(message.content)


def submit_sql(sql: str):
    st.info(f"{sql} is being executed.")
    st.session_state.current_sql = sql
    result = answerer.call(st.session_state.current_sql)
    q = deque(result)
    with st.chat_message(BOT):
        while q:
            msg = q.popleft()
            st.session_state.messages.append(
                Message(role=BOT, content=msg,
                        created_at=st.session_state.messages[-1].created_at)
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
    submission_messages = [{"role": m.role, "content": get_text_content(m)}
                           for m in st.session_state.messages]
    submission_messages.append({"role": USER, "content": user_input})
    thread = client.beta.threads.create(
        messages=submission_messages
    )
    with st.chat_message(USER):
        st.write(user_input)

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(messages)
    else:
        print(run.status)

    # Define the list to store tool outputs
    tool_outputs = []

    # Loop through each tool in the required action section
    if run.required_action:
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            func_name = tool.function.name
            try:
                output = str(getattr(tool_executor, func_name)(
                    **ast.literal_eval(tool.function.arguments)))
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": output
                })
            except Exception as e:
                st.error(f"Failed to execute tool {func_name}: {e}")
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": str(e)
                })
        print(tool_outputs)

    # Submit all tool outputs at once after collecting them in a list
    if tool_outputs:
        try:
            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            st.info("Tool outputs submitted successfully.")
        except Exception as e:
            st.error(f"Failed to submit tool outputs: {e}")
    else:
        st.info("No tool outputs to submit.")

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(messages)
        #  Convert into list so we can append
        st.session_state.messages = [m for m in messages.data]
        responses = [get_text_content(m)
                     for m in messages if m.role == BOT]
        for msg in responses:
            if "```" in msg:
                code = msg.split("```")[1].replace("\n", " ")
                st.session_state.current_sql = code
        st.rerun()
    else:
        st.info(run.status)
