from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from database import embeddings, collection
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

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

def answer_research_question(query: str):
    chunks = search_research_db(query)
    if not chunks:
        return ("I don't have enough information to answer this question.", [])

    context = "\n\n".join([f"From {c['title']}:\n{c['content']}" for c in chunks])
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Based on the following context document(s), answer the researcher's question:

Research Context:
{context}

Researcher's Question: {question}

Answer: Provide a answer based on the context above. Answer the user's questions clearly and concisely.
If the context doesn't contain enough information to fully answer the question, say so clearly.
Only answer based on the provided context, do not make assumptions or provide additional information.
If the question is not related to the context, respond with "I don't have enough information in my
knowledge base to answer this question. Please try adding some documents first.".
Answer clearly and concisely, without unnecessary details.
"""
    ).format(context=context, question=query)
    return llm.invoke(prompt).content, chunks