"""Streamlit client for the Sherpo Academy response API."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_URL = "http://187.77.71.97:4015"
API_URL = os.getenv("SHERPO_API_URL", DEFAULT_API_URL).rstrip("/")
CHAT_ENDPOINT = f"{API_URL}/chat"

st.set_page_config(
    page_title="Sherpo Academy",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 Sherpo Academy")
st.caption("Ask a question and our academy assistants will help you.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("agents"):
            st.caption("Agents: " + ", ".join(message["agents"]))

user_message = st.chat_input("How can we help you?")

if user_message:
    previous_history = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": user_message})

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    CHAT_ENDPOINT,
                    json={
                        "message": user_message,
                        "chat_history": previous_history,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("response", "The API returned no response.")
                agents = data.get("agents", [])
                st.markdown(answer)
                if agents:
                    st.caption("Agents: " + ", ".join(agents))
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "agents": agents}
                )
            except requests.RequestException as exc:
                error = f"Could not reach the Sherpo Academy API: {exc}"
                st.error(error)
                st.session_state.messages.pop()
            except ValueError:
                error = "The API returned an invalid JSON response."
                st.error(error)
                st.session_state.messages.pop()

