import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(model_name: str, temperature: float = 0.0) -> BaseChatModel:
    if model_name == "gemini-2.5-flash":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            max_retries=3,
            temperature=temperature,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    elif model_name == "gpt-4o-mini":
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    elif model_name == "gpt-4o":
        return ChatOpenAI(model="gpt-4o", temperature=temperature)
    else:
        raise ValueError(f"Unknown model name: {model_name}")