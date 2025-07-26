import json, os
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import collection, DOCS_DIR

def safe_load_json(path):
    for enc in ("utf-8", "latin-1"):
        try:
            with open(path, encoding=enc) as f: d = json.load(f); break
        except UnicodeDecodeError: continue
    return [Document(page_content=d.get("text",""),
                     metadata={"title": d.get("title", os.path.basename(path)),
                               "URL": d.get("URL","")})]

def ingest_json():
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".json"): continue
        chunks = splitter.split_documents(safe_load_json(os.path.join(DOCS_DIR, filename)))
        collection.add(
            documents=[c.page_content for c in chunks],
            metadatas=[{**c.metadata, "chunk": i} for i, c in enumerate(chunks)],
            ids=[f"{filename}_{i}" for i in range(len(chunks))]
        )

if __name__ == "__main__":
    ingest_json()
    print("Ingestion complete.")