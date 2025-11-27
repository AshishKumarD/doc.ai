#!/usr/bin/env python3
"""
Retrieval-only tool for Claude to access Xray documentation
Retrieves relevant documents from ChromaDB without LLM generation
Usage: python query_chroma.py "question here"
"""

import os
import sys
import math
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Configuration
CHROMA_DB_PATH = "/Users/ashish/Jira/jiradocai/chroma_jira_db"

def retrieve_relevant_docs(question, top_k=5):
    """Retrieve relevant documents from ChromaDB (no LLM needed)"""

    # Setup embedding model (for query encoding only)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection("jira_docs")

    # Generate query embedding
    query_embedding = embed_model.get_query_embedding(question)

    # Retrieve similar documents
    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances']
    )

    # Format results
    output = f"📝 Question: {question}\n\n"
    output += "="*70 + "\n"
    output += "📚 Retrieved Documents (Most Relevant First):\n"
    output += "="*70 + "\n"

    if results['documents'] and results['documents'][0]:
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            # Calculate similarity
            similarity = 100 * math.exp(-distance) if distance is not None else 0
            file_name = metadata.get('file_name', 'Unknown')
            file_path = metadata.get('file_path', '')

            # Get URL
            url = None
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            if line.startswith('Source: '):
                                url = line.replace('Source: ', '').strip()
                                break
                except:
                    pass

            output += f"\n[{i}] {file_name} • {similarity:.1f}% relevance\n"
            if url:
                output += f"    🔗 {url}\n"
            output += f"\n{doc}\n"
            output += "\n" + "-"*70 + "\n"

    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: No question provided")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = retrieve_relevant_docs(question, top_k=5)
    print(result)
