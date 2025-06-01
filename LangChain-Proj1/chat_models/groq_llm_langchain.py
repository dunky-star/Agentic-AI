# Import libraries
import os

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import yaml

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # Fast and capable
    temperature=0.7,  # Deterministic output
    api_key=os.getenv("GROQ_API_KEY")
)

# Basic question
messages = [
    SystemMessage(content="You are a helpful AI assistant."),
    HumanMessage(content="What are variational autoencoders and list the top 5 applications for them?")
]

groq_response = llm.invoke(messages)
