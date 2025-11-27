#!/usr/bin/env python3
"""
Web interface for querying documentation using Gradio.
Beautiful UI with automatic source citations.
Supports querying multiple documentation sources with dropdown selection.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import gradio as gr
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from src.core.doc_manager import get_available_docs

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Global variables
query_engines = {}
embed_model = None
llm = None

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def initialize_models():
    """Initialize LLM and embedding models once"""
    global llm, embed_model

    if not check_ollama():
        raise ValueError(
            "Ollama is not running! "
            "Start it with: ollama serve"
        )

    print("Loading models...")

    # Setup LLM (Ollama)
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0, base_url=OLLAMA_HOST)

    # Setup embedding model
    print("Loading embedding model...")
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Set global settings
    Settings.llm = llm
    Settings.embed_model = embed_model

def load_query_engine(doc_name):
    """Load a query engine for a specific documentation source"""
    global query_engines, llm, embed_model

    if doc_name in query_engines:
        return query_engines[doc_name]

    # Find the doc
    docs = get_available_docs()
    doc = next((d for d in docs if d['name'] == doc_name), None)

    if not doc:
        raise ValueError(f"Documentation '{doc_name}' not found")

    if not os.path.exists(doc['db_path']):
        raise FileNotFoundError(
            f"Database not found for '{doc['display_name']}' at {doc['db_path']}. "
            "Run the indexer first (option 4 in menu)."
        )

    print(f"Loading: {doc['display_name']}...")

    chroma_client = chromadb.PersistentClient(path=doc['db_path'])
    chroma_collection = chroma_client.get_or_create_collection(doc['name'])
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
        llm=llm
    )

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

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="refine",
        text_qa_template=qa_prompt
    )

    query_engines[doc_name] = query_engine
    return query_engine

def query_documentation(message, history, selected_docs):
    """Query selected documentation sources"""
    try:
        if not selected_docs:
            return "⚠️ Please select at least one documentation source from the dropdown above."

        # Load query engines for selected docs
        print(f"\n{'='*70}")
        print(f"📝 Question: {message}")
        print(f"📚 Querying {len(selected_docs)} documentation source(s): {selected_docs}")
        print(f"{'='*70}")

        if len(selected_docs) == 1:
            # Query single documentation
            query_engine = load_query_engine(selected_docs[0])
            print("🔍 Executing query...")
            response = query_engine.query(message)
        else:
            # Query multiple documentation sources - combine nodes
            all_nodes = []
            for doc_name in selected_docs:
                query_engine = load_query_engine(doc_name)
                # Get index from query engine
                index = VectorStoreIndex(list(query_engine._index.docstore.docs.values()), embed_model=embed_model, llm=llm)
                all_nodes.extend(index.docstore.docs.values())

            # Create combined index
            combined_index = VectorStoreIndex(all_nodes, embed_model=embed_model, llm=llm)

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

            query_engine = combined_index.as_query_engine(
                similarity_top_k=5,
                response_mode="refine",
                text_qa_template=qa_prompt
            )

            print("🔍 Executing query...")
            response = query_engine.query(message)

        # Debug: Check response
        print(f"✅ Got response: {len(str(response.response)) if response.response else 0} characters")
        print(f"📚 Source nodes: {len(response.source_nodes) if response.source_nodes else 0}")

        # Check if response is empty
        if not response.response or str(response.response).strip() == "" or str(response.response).strip().lower() == "empty response":
            return (
                "⚠️ **No relevant information found in the documentation.**\n\n"
                "This could mean:\n"
                "- The question is outside the scope of the indexed documentation\n"
                "- The documentation doesn't contain information about this topic\n\n"
                "**Tip:** Try rephrasing your question or ask about topics covered in the documentation.\n\n"
                f"**Documentation queried:** {', '.join(selected_docs)}"
            )

        # Format response with sources
        response_text = f"{response.response}\n\n"

        if response.source_nodes:
            response_text += "**📚 Sources:**\n\n"
            for i, node in enumerate(response.source_nodes[:3], 1):  # Show top 3 sources
                file_name = node.metadata.get('file_name', 'Unknown')
                source_url = node.metadata.get('source_url')
                score = node.score

                # Show URL if available, otherwise show file path
                if source_url:
                    response_text += f"{i}. **[{file_name}]({source_url})** (Relevance: {score:.1%})\n\n"
                else:
                    file_path = node.metadata.get('file_path', 'N/A')
                    response_text += f"{i}. **{file_name}** (Relevance: {score:.1%})\n"
                    response_text += f"   Path: `{file_path}`\n\n"

        return response_text

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error occurred:\n{error_details}")
        return f"❌ **Error:** {str(e)}\n\nPlease check the console for details."

def main():
    print("="*70)
    print("DocAI - Documentation Assistant (Web UI)")
    print("="*70)

    # Initialize models
    try:
        initialize_models()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Get available documentation
    docs = get_available_docs()
    indexed_docs = [d for d in docs if d['indexed']]

    if not indexed_docs:
        print("\n⚠️  No indexed documentation found!")
        print("Run the indexer first (option 4 in menu).")
        sys.exit(1)

    doc_choices = [d['display_name'] for d in indexed_docs]
    doc_name_map = {d['display_name']: d['name'] for d in indexed_docs}

    print(f"\nFound {len(indexed_docs)} indexed documentation source(s)")
    for doc in indexed_docs:
        print(f"  - {doc['display_name']}")

    # Get system information
    ollama_status = "🟢 Running" if check_ollama() else "🔴 Not Running"

    # Create Gradio interface with dropdown
    with gr.Blocks(title="DocAI - Documentation Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🔧 DocAI - Documentation Assistant")
        gr.Markdown("Ask questions about your documentation. Select one or more sources below.")

        # System status info
        with gr.Accordion("📊 System Information", open=False):
            gr.Markdown(f"""
### Current Configuration
- **Model:** `{OLLAMA_MODEL}`
- **Ollama Status:** {ollama_status}
- **Ollama Host:** `{OLLAMA_HOST}`
- **Documentation Sources:** {len(indexed_docs)} indexed
- **Embedding Model:** BAAI/bge-small-en-v1.5

### Available Documentation
{chr(10).join([f'- ✓ {doc["display_name"]}' for doc in indexed_docs])}
            """)

        # Documentation selector
        doc_selector = gr.Dropdown(
            choices=doc_choices,
            value=[doc_choices[0]] if doc_choices else [],
            multiselect=True,
            label="📚 Select Documentation Sources",
            info="Choose one or more documentation sources to query"
        )

        # Chat interface with additional input
        def chat_with_docs(message, history, selected_display_names):
            """Wrapper to pass selected docs to query function"""
            if not selected_display_names:
                return "⚠️ Please select at least one documentation source from the dropdown above."

            selected_doc_names = [doc_name_map[d] for d in selected_display_names]
            return query_documentation(message, history, selected_doc_names)

        # Examples need to include values for all inputs (message + dropdown)
        example_questions = [
            ["How do I configure authentication?", [doc_choices[0]] if doc_choices else []],
            ["What are the main features?", [doc_choices[0]] if doc_choices else []],
            ["How do I troubleshoot errors?", [doc_choices[0]] if doc_choices else []],
            ["What's in the application logs?", [doc_choices[0]] if doc_choices else []],
        ]

        chatbot = gr.ChatInterface(
            fn=chat_with_docs,
            additional_inputs=[doc_selector],
            examples=example_questions,
            retry_btn="🔄 Retry",
            undo_btn="↩️ Undo",
            clear_btn="🗑️ Clear",
        )

    print("\n" + "="*70)
    print("✅ Starting web interface...")
    print("="*70)
    print("\nThe interface will open in your default browser.")
    print("Press Ctrl+C to stop the server.\n")

    # Launch the interface
    server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    demo.launch(
        share=False,
        server_name=server_name,
        server_port=7860
    )

if __name__ == "__main__":
    main()
