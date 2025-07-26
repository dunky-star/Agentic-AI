"""
Streamlit AI Chatbot App
Built with LangChain + Groq + Streamlit

This app demonstrates how to build a professional AI chatbot interface
using Streamlit's powerful UI components and session state management.
"""

import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# FastAPI backend endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

def get_ai_response(user_message: str) -> str:
    try:
        res = requests.post(API_URL, json={"message": user_message})
        res.raise_for_status()
        return res.json().get("response", "⚠️ No response from backend.")
    except requests.RequestException as e:
        st.error(f"❌ API call failed: {e}")
        return "⚠️ Something went wrong! Please try again later."

def main():
    # Page configuration
    st.set_page_config(
        page_title="AI Chatbot Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Main title and description
    st.title("🤖 AI Chatbot Assistant")
    st.markdown("Ask me anything and I'll help you with intelligent responses!")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    # Sidebar for additional features
    with st.sidebar:
        st.markdown("### About This App")
        st.markdown("This AI chatbot is powered by:")
        st.markdown("- **OpenAI** for fast LLM inference")
        st.markdown("- **LangChain** for AI orchestration")
        st.markdown("- **Streamlit** for the beautiful UI")

        st.markdown("---")
        st.markdown("### Chat Controls")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("### Stats")
        st.metric("Messages in Chat", len(st.session_state.messages))

        if st.session_state.messages:
            user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
            st.metric("Questions Asked", user_messages)

if __name__ == "__main__":
    main()
