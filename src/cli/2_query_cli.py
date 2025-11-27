#!/usr/bin/env python3
"""
Command-line interface for querying documentation.
Shows answers WITH source citations.
Supports querying multiple documentation sources.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from src.core.doc_manager import get_available_docs

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def setup_query_engine(doc_names):
    """Initialize the query engine from selected documentation sources"""
    if not check_ollama():
        print("⚠️  Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Start: ollama serve")
        print("  2. Pull model (in another terminal): ollama pull " + OLLAMA_MODEL)
        sys.exit(1)

    print("🔧 Loading query engine...")

    # Setup LLM (Ollama)
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)

    # Setup embedding model
    print("   Loading embedding model...")
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Set global settings
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Load indices from multiple sources
    print(f"   Connecting to {len(doc_names)} documentation source(s)...")

    all_nodes = []
    for doc in get_available_docs():
        if doc['name'] in doc_names:
            if not os.path.exists(doc['db_path']):
                print(f"⚠️  Database not found for '{doc['display_name']}' at {doc['db_path']}")
                print("Run the indexer first (option 4 in menu).")
                sys.exit(1)

            print(f"   Loading: {doc['display_name']}...")
            chroma_client = chromadb.PersistentClient(path=doc['db_path'])
            chroma_collection = chroma_client.get_or_create_collection(doc['name'])
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embed_model,
                llm=llm
            )

            # Get all nodes from this index
            all_nodes.extend(index.docstore.docs.values())

    # Create combined index
    combined_index = VectorStoreIndex(all_nodes, embed_model=embed_model, llm=llm)

    # Custom prompt for detailed explanations
    from llama_index.core.prompts import PromptTemplate
    qa_prompt = PromptTemplate(
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information above, please provide a detailed and comprehensive answer to the question below. "
        "Include specific details, examples, and step-by-step explanations where applicable. "
        "If there are multiple aspects to the question, address each one thoroughly. "
        "Be clear, precise, and educational in your response.\n\n"
        "Question: {query_str}\n"
        "Detailed Answer: "
    )

    return combined_index.as_query_engine(
        similarity_top_k=5,
        response_mode="refine",
        text_qa_template=qa_prompt
    )

def print_response_with_sources(response):
    """Pretty print response with source citations"""
    print("\n" + "="*70)
    print("📝 ANSWER")
    print("="*70)

    # Check if response is empty
    if not response.response or str(response.response).strip() == "" or str(response.response).strip().lower() == "empty response":
        print("⚠️  No relevant information found in the documentation.")
        print("\nThis could mean:")
        print("- The question is outside the scope of the indexed documentation")
        print("- The documentation doesn't contain information about this topic")
        print("\nTip: Try rephrasing your question or ask about topics covered in the documentation.")
    else:
        print(response.response)

    if response.source_nodes:
        print("\n" + "="*70)
        print("📚 SOURCES")
        print("="*70)

        for i, node in enumerate(response.source_nodes, 1):
            file_name = node.metadata.get('file_name', 'Unknown')
            source_url = node.metadata.get('source_url')
            file_path = node.metadata.get('file_path', 'N/A')
            score = node.score

            print(f"\n[{i}] {file_name}")
            print(f"    Relevance: {score:.1%}")

            # Show URL if available, otherwise show file path
            if source_url:
                print(f"    URL: {source_url}")
            else:
                print(f"    Path: {file_path}")

            print(f"\n    Preview:")
            preview = node.text[:200].replace('\n', ' ')
            print(f"    \"{preview}...\"")

    print("\n" + "="*70 + "\n")

def main():
    print("="*70)
    print("🔧 DocAI - Documentation Assistant (CLI)")
    print("="*70)

    # Get available documentation
    docs = get_available_docs()
    indexed_docs = [d for d in docs if d['indexed']]

    if not indexed_docs:
        print("\n⚠️  No indexed documentation found!")
        print("Run the indexer first (option 4 in menu).")
        sys.exit(1)

    print("\nAvailable documentation:")
    print("")

    for i, doc in enumerate(indexed_docs, 1):
        print(f"  {i}) {doc['display_name']}")

    print(f"  {len(indexed_docs)+1}) All documentation")
    print("")

    try:
        choice = input(f"Select documentation [1-{len(indexed_docs)+1}]: ").strip()
        choice_num = int(choice)

        if choice_num == len(indexed_docs) + 1:
            selected_docs = [d['name'] for d in indexed_docs]
            print(f"\nQuerying all {len(selected_docs)} documentation sources")
        elif 1 <= choice_num <= len(indexed_docs):
            selected_docs = [indexed_docs[choice_num-1]['name']]
            print(f"\nQuerying: {indexed_docs[choice_num-1]['display_name']}")
        else:
            print("Invalid choice!")
            sys.exit(1)

    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
        sys.exit(0)

    print("")
    print("Commands:")
    print("  - Type your question and press Enter")
    print("  - 'sources on/off' - Toggle source display")
    print("  - 'quit' or 'exit' - Exit the program")
    print("="*70)

    query_engine = setup_query_engine(selected_docs)
    print("✅ Ready!\n")

    show_sources = True

    while True:
        try:
            question = input("\n💬 You: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if question.lower() in ['sources on', 'sources off']:
                show_sources = 'on' in question.lower()
                print(f"Source citations: {'ON ✅' if show_sources else 'OFF ❌'}")
                continue

            if not question:
                continue

            print("\n🔍 Searching documentation...")
            response = query_engine.query(question)

            if show_sources:
                print_response_with_sources(response)
            else:
                print("\n" + "="*70)
                print(response.response)
                print("="*70 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
