# ChromaDB and PgVector are two popular vector databases used for storing and querying embeddings.
# Choosing PgVector over Pinecone to optimizing embedding models for AI content

# File: chat_models/vector_database_pipeline.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


def process_document_file(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Reads a text file, splits it into chunks with overlap, wraps each chunk in a Document
    (with metadata), embeds them, and returns a Chroma vector store containing those chunks.

    Args:
        file_path (str): Path to a UTF‑8 encoded text file.
        chunk_size (int): Maximum characters per chunk.
        chunk_overlap (int): Number of overlapping characters between chunks.

    Returns:
        Chroma: A Chroma vector store ready for similarity search.
    """
    # 1) Read the entire file as a single string
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cannot find file at {file_path!r}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 2) Split the text “intelligently” into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)

    # 3) Wrap each chunk in a Document, attaching metadata for source + chunk index
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": file_path, "chunk_id": i}
        )
        for i, chunk in enumerate(chunks)
    ]

    # 4) Choose an embedding model (here: all-MiniLM-L6-v2)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5) Build a Chroma vector store from our documents + embeddings
    vectorstore = Chroma.from_documents(documents, embeddings)

    return vectorstore


# If someone “imports results, print_vector_db_pipeline” directly,
# we can provide a quick‐and‐dirty default example, but normally
# you’ll call process_document_file(...) from main.py.

def print_vector_db_pipeline(doc: Document, score: float):
    """
    Helper to print a Document + its similarity score in a uniform format.
    """
    print(f"Score: {score:.3f}")
    print(f"Text (first 100 chars): {doc.page_content[:100]!r}…")
    print(f"Metadata: {doc.metadata}")
    print("---")





