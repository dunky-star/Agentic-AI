import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY"),
)


def get_ai_response(user_message: str) -> str:
    messages = [
        SystemMessage(content="You are a helpful US immigration assistant. Answer the user's questions clearly and concisely."),
        HumanMessage(content=user_message),
    ]
    response = llm.invoke(messages)
    return response.content
