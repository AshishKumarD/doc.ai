#!/usr/bin/env python3
"""
Quick query tool for direct ChromaDB queries
Usage: python quick_query.py "your question here"
"""

import os
import sys
import math
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core.prompts import PromptTemplate

# Configuration
CHROMA_DB_PATH = "./chroma_db"
OLLAMA_MODEL = "qwen2.5:14b-instruct"
OLLAMA_HOST = "http://localhost:11434"

# Setup (cached globally to avoid reloading)
_query_engine = None

def setup():
    global _query_engine

    if _query_engine is not None:
        return _query_engine

    # Setup LLM
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0, base_url=OLLAMA_HOST)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    Settings.llm = llm
    Settings.embed_model = embed_model

    # Load index
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection("docs")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
        llm=llm
    )

    # Create query engine with Xray Support Specialist prompt
    qa_prompt = PromptTemplate(
        "You are an Xray for Jira Support Specialist. Use ONLY the information provided in the context.\n\n"
        "=====================\n"
        "CONTEXT (from Xray Documentation):\n"
        "{context_str}\n"
        "=====================\n\n"
        "CRITICAL INSTRUCTIONS (follow strictly):\n\n"
        "1. **Use ONLY the provided documentation.**\n"
        "2. **Provide a structured and support-friendly answer with:**\n"
        "   - **Summary (2–3 sentences)**\n"
        "   - **Detailed Explanation (3–5 paragraphs)**\n"
        "   - **Steps or How-To Instructions (if applicable)**\n"
        "   - **Important Notes / Limitations**\n"
        "   - **References**\n\n"
        "=====================\n"
        "Question: {query_str}\n\n"
        "Final Answer:\n"
    )

    _query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact",
        text_qa_template=qa_prompt
    )

    return _query_engine

def query(question):
    """Query the documentation and return formatted answer with sources"""
    engine = setup()
    response = engine.query(question)

    # Format output
    output = response.response + "\n\n"
    output += "="*70 + "\n"
    output += "📚 SOURCES:\n"
    output += "="*70 + "\n"

    for i, node in enumerate(response.source_nodes, 1):
        similarity = 100 * math.exp(-node.score) if node.score else 0
        file_name = node.metadata.get('file_name', 'Unknown')

        # Try to get URL from file
        file_path = node.metadata.get('file_path', '')
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

    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_query.py \"your question here\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    print(f"\n📝 Question: {question}\n")
    print("="*70)

    result = query(question)
    print(result)
