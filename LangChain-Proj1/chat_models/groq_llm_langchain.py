# Import libraries
"""
Multi-Turn Conversations: The user asks two questions in sequence, and the LLM uses contextual memory to answer.
"""

import os

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import yaml

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # Fast and capable
    temperature=0.7,  # Deterministic output
    api_key=os.getenv("GROQ_API_KEY")
)

# Sample publication content (abbreviated for example)
# In the code repo, we will load this from a markdown file.
publication_content = """
    Title: One Model, Five Superpowers: The Versatility of Variational Auto-Encoders
    
    TL;DR
    Variational Auto-Encoders (VAEs) are versatile deep learning models with applications in data compression, noise reduction, 
    synthetic data generation, anomaly detection, and missing data imputation. This publication demonstrates these capabilities using the MNIST dataset,
    providing practical insights for AI/ML practitioners.
    
    Introduction
    Variational Auto-Encoders (VAEs) are powerful generative models that exemplify unsupervised deep learning. 
    They use a probabilistic approach to encode data into a distribution of latent variables, enabling both data compression and the generation of new,
     similar data instances.
    [rest of publication content... truncated for brevity]
"""

# Initialize conversation
conversation = [
    SystemMessage(content=f"""
    You are a helpful AI assistant discussing a research publication.
    Based your answer only on this on this publication content: {publication_content}
""")
]

# User question 1
conversation.append(
    HumanMessage(content="""
        What are variational autoencoders and list the top 5 applications for them as discussed in this publication.
"""))

groq_response1 = llm.invoke(conversation)

print("🤖 AI Response to Question 1:")
print(groq_response1.content)
print("\n" + "="*50 + "\n")

# Add AI's response to conversation history
conversation.append(AIMessage(content=groq_response1.content))

# User question 2 (follow-up)
conversation.append(HumanMessage(content="""
How does it work in case of anomaly detection?
"""))

response2 = llm.invoke(conversation)
print("🤖 AI Response to Question 2:")
print(response2.content)