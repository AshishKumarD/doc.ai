#!/usr/bin/env python3
"""
Documentation Manager - Handles multiple documentation sources
"""

import os
from pathlib import Path
from typing import List, Dict

DOCS_DIR = "./data/documentation"
CHROMA_DB_DIR = "./data/chroma_db"

def get_available_docs() -> List[Dict[str, str]]:
    """
    Get list of available documentation folders
    Returns list of dicts with 'name', 'path', and 'db_path'
    """
    docs = []

    if not os.path.exists(DOCS_DIR):
        return docs

    for item in os.listdir(DOCS_DIR):
        doc_path = os.path.join(DOCS_DIR, item)
        if os.path.isdir(doc_path):
            db_name = f"chroma_{item}_db"
            db_path = os.path.join(CHROMA_DB_DIR, db_name)

            docs.append({
                'name': item,
                'display_name': item.replace('_', ' ').title(),
                'doc_path': doc_path,
                'db_path': db_path,
                'indexed': os.path.exists(db_path)
            })

    return docs

def get_doc_db_path(doc_name: str) -> str:
    """Get database path for a specific documentation folder"""
    db_name = f"chroma_{doc_name}_db"
    return os.path.join(CHROMA_DB_DIR, db_name)

def get_doc_path(doc_name: str) -> str:
    """Get documentation folder path"""
    return os.path.join(DOCS_DIR, doc_name)
