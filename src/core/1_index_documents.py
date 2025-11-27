#!/usr/bin/env python3
"""
Index documentation into searchable vector databases.
Creates one database per documentation source.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.doc_manager import get_available_docs
from src.core.index_single_doc import index_documentation, check_ollama

def main():
    print("="*70)
    print("DocAI - Documentation Indexer")
    print("="*70)

    # Check if Ollama is running
    if not check_ollama():
        print("\n⚠️  Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Install: brew install ollama  (macOS)")
        print("              curl -fsSL https://ollama.com/install.sh | sh  (Linux)")
        print("  2. Start: ollama serve")
        print("\nThen run this script again.")
        sys.exit(1)

    # Get available documentation folders
    docs = get_available_docs()

    if not docs:
        print("\n⚠️  No documentation folders found in ./data/documentation/")
        print("\nPlease add documentation folders first using option 3 in the menu.")
        sys.exit(1)

    print("\nAvailable documentation folders:")
    print("")

    for i, doc in enumerate(docs, 1):
        status = "✅ Indexed" if doc['indexed'] else "❌ Not indexed"
        print(f"  {i}) {doc['display_name']} ({doc['name']}) - {status}")

    print("")
    print("  0) Exit")
    print("")

    try:
        choice = int(input("Select documentation to index [0-{}]: ".format(len(docs))))

        if choice == 0:
            print("Exiting...")
            sys.exit(0)

        if choice < 1 or choice > len(docs):
            print("Invalid choice!")
            sys.exit(1)

        selected_doc = docs[choice - 1]

        if selected_doc['indexed']:
            print(f"\n⚠️  '{selected_doc['name']}' is already indexed.")
            confirm = input("Do you want to re-index it? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Skipping...")
                sys.exit(0)

        # Index the selected documentation
        print("")
        index_documentation(selected_doc['name'])

    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
