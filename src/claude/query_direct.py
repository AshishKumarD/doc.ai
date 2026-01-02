#!/usr/bin/env python3
"""
Direct ChromaDB query without LLM - just retrieves relevant documents
"""

import sys
import os
import chromadb
from sentence_transformers import SentenceTransformer

# Configuration - path relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "../..")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data/chroma_db/chroma_xray_cloud_db")

def query_chroma_direct(question, top_k=5):
    """Query ChromaDB directly and return relevant documents"""

    # Load embedding model
    print("Loading embedding model...")
    embed_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

    # Connect to ChromaDB
    print("Connecting to ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection("xray_cloud")

    # Generate embedding for question
    print(f"Searching for: {question}\n")
    question_embedding = embed_model.encode(question).tolist()

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format and print results
    print("="*70)
    print("RELEVANT DOCUMENTATION:")
    print("="*70)

    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = (1 - distance) * 100  # Convert distance to similarity percentage
        file_name = metadata.get('file_name', 'Unknown')

        print(f"\n[{i}] {file_name} • {similarity:.1f}% relevance")
        print("-"*70)
        print(doc[:500] + "..." if len(doc) > 500 else doc)
        print()

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_direct.py \"your question here\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    query_chroma_direct(question, top_k=10)
