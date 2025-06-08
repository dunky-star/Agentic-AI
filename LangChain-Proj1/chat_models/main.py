# File: main.py
import sys

from chat_models.groq_llm_langchain import groq_response1
from chat_models.print_helper import print_hi
from chat_models.chat_models_starter import response
from chat_models.llm_function_chaining import result
from chat_models.vector_database_pipeline import process_document_file, print_vector_db_pipeline

def main():
    # 1) Greet / print any precomputed variables (same as before)
    print("\n--- Chat Model Response ---\n")
    print_hi(response)
    print("\n--- LLM Function Chaining Response ---\n")
    print_hi(result)
    print("\n--- Groq LLM Response ---\n")
    print_hi(groq_response1.content)

    # 2) Check that the user passed in a filename to process
    if len(sys.argv) < 2:
        print("Usage: python main.py <path/to/your_document.txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        # 3) Build the vectorstore from disk
        vectorstore = process_document_file(file_path)

        # 4) Perform a sample similarity search
        query = "What is a RAG system?"
        results = vectorstore.similarity_search_with_score(query, k=2)

        print(f"\nTop 2 chunks for query {query!r}:\n")
        for doc, score in results:
            print_vector_db_pipeline(doc, score)

    except FileNotFoundError as fnf:
        print(f"Error: {fnf}")
        sys.exit(1)


if __name__ == "__main__":
    main()


