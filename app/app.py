from collections import deque
import streamlit as st
from answerers.langchain_answerer.langchain_naive_answerer import LangchainNaiveAnswerer

answerer = LangchainNaiveAnswerer()
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
        st.write(message["content"])

if question := st.chat_input("Enter your question:"):
    st.session_state.messages.append({"role": USER, "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    answers = answerer.call(question)
    q = deque(answers)
    with st.chat_message("assistant"):
        while q:
            msg = q.popleft()
            st.write(msg)
            st.session_state.messages.append(
                {"role": BOT, "content": msg}
            )
