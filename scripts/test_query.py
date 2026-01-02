#!/usr/bin/env python3
"""
Direct test query to ChromaDB to demonstrate the RAG system
"""

import os
import sys
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Configuration
CHROMA_DB_PATH = "./chroma_jira_db"
OLLAMA_MODEL = "qwen2.5:14b-instruct"
OLLAMA_HOST = "http://localhost:11434"

print("="*70)
print("Direct ChromaDB Query Test")
print("="*70)

# Setup LLM
print("\n🤖 Connecting to Ollama...")
llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0, base_url=OLLAMA_HOST)

# Setup embedding model
print("🧠 Loading embedding model...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Set global settings
Settings.llm = llm
Settings.embed_model = embed_model

# Load existing index
print("💾 Connecting to vector database...")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("jira_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model,
    llm=llm
)

print("✅ Ready!")

# Create query engine with your prompt
from llama_index.core.prompts import PromptTemplate

qa_prompt = PromptTemplate(
    "You are an Xray for Jira Support Specialist. Use ONLY the information provided in the context.\n\n"
    "=====================\n"
    "CONTEXT (from Xray Documentation):\n"
    "{context_str}\n"
    "=====================\n\n"
    "CRITICAL INSTRUCTIONS (follow strictly):\n\n"
    "1. **Use ONLY the provided documentation.**\n"
    "   - Do NOT use external knowledge.\n\n"
    "2. **Provide a structured and support-friendly answer.**\n"
    "   Your answer MUST include:\n"
    "   - **Summary (2–3 sentences)**\n"
    "   - **Detailed Explanation (3–5 paragraphs)**\n"
    "   - **Steps or How-To Instructions (if applicable)**\n"
    "   - **Important Notes / Limitations**\n"
    "   - **References**\n\n"
    "=====================\n"
    "Question: {query_str}\n\n"
    "Final Answer (based ONLY on the documentation above):\n"
)

query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact",
    text_qa_template=qa_prompt
)

# Test query
question = """When a team-managed Jira project containing Xray Test issues is archived and then unarchived, is the Xray configuration preserved? Are there any known limitations with Xray and archived/unarchived team-managed projects? Can test data be accessed after unarchiving?"""
print(f"\n📝 Question: {question}\n")
print("="*70)
print("Querying...")
print("="*70)

response = query_engine.query(question)

print("\n" + "="*70)
print("ANSWER:")
print("="*70)
print(response.response)

# Show sources
print("\n" + "="*70)
print("SOURCES:")
print("="*70)
for i, node in enumerate(response.source_nodes, 1):
    import math
    similarity = 100 * math.exp(-node.score) if node.score else 0
    file_name = node.metadata.get('file_name', 'Unknown')
    print(f"\n[{i}] {file_name}")
    print(f"    Distance: {node.score:.3f}")
    print(f"    Similarity: {similarity:.1f}%")
    print(f"    Preview: {node.text[:150]}...")

print("\n" + "="*70)
print("✅ Query complete!")
print("="*70)
