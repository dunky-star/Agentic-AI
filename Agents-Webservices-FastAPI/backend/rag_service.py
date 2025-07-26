from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from database import embeddings, collection
import os
from dotenv import load_dotenv
import yaml
import re

load_dotenv()

# Load prompt config
with open(os.path.join(os.path.dirname(__file__), "config/prompt_config.yaml"), "r") as f:
    prompt_cfg = yaml.safe_load(f)["us_immigration_assistant_cfg"]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

def build_us_immigration_prompt(context: str, question: str) -> str:
    constraints = "\n".join(f"- {c}" for c in prompt_cfg["output_constraints"])
    style = "\n".join(f"- {s}" for s in prompt_cfg["style_or_tone"])
    prompt = f"""
Role: {prompt_cfg['role']}
Instruction: {prompt_cfg['instruction']}
Output Constraints:\n{constraints}
Style or Tone:\n{style}
Goal: {prompt_cfg['goal']}
Context:\n{prompt_cfg['context']}
\nResearch Context:\n{context}\n\nUser Question: {question}\n\nAnswer: """
    return prompt

def search_research_db(query: str, top_k: int = 3):
    query_embedding = embeddings.embed_query(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    print(results)
    # return results
    return [
        {
            "content": doc,
            "title": results["metadatas"][0][i].get("title", "Unknown"),
            "score": results["distances"][0][i],
        }
        for i, doc in enumerate(results["documents"][0])
    ]

IMMIGRATION_KEYWORDS = [
    "visa", "green card", "asylum", "citizenship", "immigration", "uscis", "adjustment of status",
    "naturalization", "deportation", "work permit", "travel ban", "refugee", "DACA", "TPS", "I-94", "I-130",
    "I-485", "I-140", "I-765", "I-539", "I-601", "I-212", "I-864", "I-129", "I-131", "I-797", "I-9",
    "EAD", "H-1B", "F-1", "J-1", "EB-1", "EB-2", "EB-3", "EB-5", "E-2", "E-3", "E-1", "L-1", "O-1", "TN",
    "US immigration", "USCIS", "CBP", "ICE", "consular processing", "removal proceedings"
]

def is_immigration_related(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in IMMIGRATION_KEYWORDS)

def answer_research_question(query: str):
    if not is_immigration_related(query):
        return ("Sorry, I am an assistant for US immigration topics only. Please ask a question related to US immigration.", [])
    chunks = search_research_db(query)
    if not chunks:
        return ("I don't have enough information to answer this question.", [])

    context = "\n\n".join([f"From {c['title']}:\n{c['content']}" for c in chunks])
    prompt = build_us_immigration_prompt(context, query)
    return llm.invoke(prompt).content, chunks