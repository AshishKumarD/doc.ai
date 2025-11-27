#!/usr/bin/env python3
"""
Index a single documentation folder into its own vector database.
Creates one database per documentation source.
"""

import os
import sys
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.core.doc_manager import get_doc_db_path, get_doc_path

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def index_documentation(doc_name: str):
    """Index a specific documentation folder"""
    print("="*70)
    print(f"DocAI - Indexing: {doc_name}")
    print("="*70)

    # Check if Ollama is running
    if not check_ollama():
        print("\n⚠️  Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Install: brew install ollama  (macOS)")
        print("              curl -fsSL https://ollama.com/install.sh | sh  (Linux)")
        print("  2. Start: ollama serve")
        print("  3. Pull model (in another terminal): ollama pull " + OLLAMA_MODEL)
        print("\nThen run this script again.")
        sys.exit(1)

    # Get paths
    docs_path = get_doc_path(doc_name)
    db_path = get_doc_db_path(doc_name)

    # Check docs directory
    if not os.path.exists(docs_path):
        print(f"\n⚠️  Documentation directory not found: {docs_path}")
        sys.exit(1)

    print(f"\n📁 Documentation path: {docs_path}")
    print(f"💾 Database path: {db_path}")
    print(f"🤖 LLM: Ollama ({OLLAMA_MODEL})")

    # Setup LLM (Ollama)
    print("\n🤖 Initializing Ollama...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)

    # Setup embedding model
    print("🧠 Loading embedding model (this may take a moment)...")
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Setup ChromaDB
    print("💾 Setting up vector database...")
    os.makedirs(db_path, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=db_path)
    chroma_collection = chroma_client.get_or_create_collection(doc_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Load documents
    print(f"\n📖 Loading documents from {docs_path}...")
    try:
        documents = SimpleDirectoryReader(
            docs_path,
            recursive=True,
            required_exts=[".md", ".txt", ".pdf", ".log", ".html"]
        ).load_data()
        print(f"✅ Loaded {len(documents)} documents")

        # Extract source URLs from markdown files
        print("🔗 Extracting source URLs from documents...")
        url_count = 0
        for doc in documents:
            # Check if document has "Source: <url>" in first few lines
            text = doc.text
            lines = text.split('\n')[:5]  # Check first 5 lines
            for line in lines:
                if line.startswith('Source: '):
                    url = line.replace('Source: ', '').strip()
                    if url:
                        doc.metadata['source_url'] = url
                        url_count += 1
                        break
        print(f"✅ Extracted {url_count} source URLs")

    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        sys.exit(1)

    if len(documents) == 0:
        print("⚠️  No documents found! Check your documentation folder.")
        sys.exit(1)

    # Create index
    print("\n🔨 Creating index (this will take a few minutes)...")
    print("   - Chunking documents...")
    print("   - Generating embeddings...")
    print("   - Storing in vector database...")

    try:
        # Parse documents into nodes with metadata preservation
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.core.schema import TextNode

        parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
        nodes = parser.get_nodes_from_documents(documents, show_progress=True)

        # Propagate source_url to ALL nodes from their source documents
        print(f"\n🔗 Ensuring URL metadata on all {len(nodes)} chunks...")

        # Build mapping of file_path -> source_url from documents
        file_to_url_map = {}
        for doc in documents:
            if 'source_url' in doc.metadata:
                file_path = doc.metadata.get('file_path')
                if file_path:
                    file_to_url_map[file_path] = doc.metadata['source_url']

        print(f"📋 Found {len(file_to_url_map)} documents with URLs")

        # Propagate URLs to all chunks based on file_path
        urls_propagated = 0
        for node in nodes:
            file_path = node.metadata.get('file_path')
            if file_path and file_path in file_to_url_map:
                node.metadata['source_url'] = file_to_url_map[file_path]
                urls_propagated += 1

        print(f"✅ Propagated URLs to {urls_propagated}/{len(nodes)} chunks")

        # Create index from nodes
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            llm=llm,
            show_progress=True
        )
        print("\n✅ Index created successfully!")
    except Exception as e:
        print(f"\n❌ Error creating index: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "="*70)
    print(f"✅ SUCCESS! Documentation '{doc_name}' has been indexed.")
    print("="*70)
    print(f"\nDatabase saved to: {db_path}")
    print("\nYou can now query this documentation using the Web UI or CLI.")
    print("="*70)

def main():
    if len(sys.argv) < 2:
        print("Usage: python index_single_doc.py <doc_folder_name>")
        print("\nExample: python index_single_doc.py xray_cloud")
        sys.exit(1)

    doc_name = sys.argv[1]
    index_documentation(doc_name)

if __name__ == "__main__":
    main()
