#!/usr/bin/env python3
"""
Visualize ChromaDB vector database contents.
Shows statistics, document clusters, and embedding visualizations.
"""

import os
import sys
import chromadb
from collections import Counter
import json

# Configuration
CHROMA_DB_PATH = "./chroma_jira_db"

def analyze_database():
    """Analyze and display ChromaDB statistics"""

    if not os.path.exists(CHROMA_DB_PATH):
        print(f"❌ Database not found at {CHROMA_DB_PATH}")
        print("Run '1_index_documents.py' first to create the index.")
        sys.exit(1)

    print("="*70)
    print("ChromaDB Visualization Tool")
    print("="*70)

    # Connect to ChromaDB
    print("\n📊 Connecting to database...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Get collection
    collection = client.get_or_create_collection("jira_docs")

    # Get all data
    print("   Loading collection data...")
    results = collection.get(include=['metadatas', 'documents', 'embeddings'])

    num_docs = len(results['ids'])

    print(f"\n✅ Database loaded successfully!")
    print("="*70)

    # Basic Statistics
    print("\n📈 BASIC STATISTICS")
    print("="*70)
    print(f"Total Documents: {num_docs}")
    print(f"Total Chunks: {num_docs}")

    if results['embeddings']:
        embedding_dim = len(results['embeddings'][0])
        print(f"Embedding Dimensions: {embedding_dim}")

    # Metadata analysis
    if results['metadatas']:
        print("\n📋 DOCUMENT BREAKDOWN")
        print("="*70)

        # Count by file_name
        file_names = [m.get('file_name', 'Unknown') for m in results['metadatas']]
        file_counts = Counter(file_names)

        print(f"\nUnique Documents: {len(file_counts)}")
        print("\nTop 20 Documents by Chunk Count:")
        for file, count in file_counts.most_common(20):
            print(f"  {count:3d} chunks - {file}")

        # Count by file_path if available
        if any('file_path' in m for m in results['metadatas']):
            print("\n📁 DOCUMENTS BY PATH")
            print("="*70)
            for i, metadata in enumerate(results['metadatas'][:10]):
                file_path = metadata.get('file_path', 'N/A')
                file_name = metadata.get('file_name', 'Unknown')
                print(f"  [{i+1}] {file_name}")
                print(f"      Path: {file_path}")

    # Document content preview
    print("\n📄 SAMPLE DOCUMENTS")
    print("="*70)
    for i, (doc_id, doc_text, metadata) in enumerate(zip(
        results['ids'][:5],
        results['documents'][:5],
        results['metadatas'][:5]
    )):
        print(f"\n[{i+1}] ID: {doc_id}")
        print(f"    File: {metadata.get('file_name', 'Unknown')}")
        print(f"    Preview: {doc_text[:150]}...")

    # Size analysis
    if results['documents']:
        doc_lengths = [len(doc) for doc in results['documents']]
        avg_length = sum(doc_lengths) / len(doc_lengths)
        min_length = min(doc_lengths)
        max_length = max(doc_lengths)

        print("\n📏 CHUNK SIZE ANALYSIS")
        print("="*70)
        print(f"Average chunk size: {avg_length:.0f} characters")
        print(f"Smallest chunk: {min_length} characters")
        print(f"Largest chunk: {max_length} characters")

    # Total storage estimate
    if results['documents'] and results['embeddings']:
        text_size = sum(len(doc.encode('utf-8')) for doc in results['documents'])
        embedding_size = len(results['embeddings']) * len(results['embeddings'][0]) * 4  # 4 bytes per float
        total_size = text_size + embedding_size

        print("\n💾 STORAGE USAGE")
        print("="*70)
        print(f"Text data: {text_size / 1024:.1f} KB")
        print(f"Embeddings: {embedding_size / 1024:.1f} KB")
        print(f"Total (estimated): {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.2f} MB)")

    return collection, results

def visualize_embeddings(results):
    """Create 2D visualization of embeddings using dimensionality reduction"""

    if not results['embeddings']:
        print("\n⚠️  No embeddings found in database")
        return

    try:
        import numpy as np
        from sklearn.manifold import TSNE
        import matplotlib.pyplot as plt

        print("\n🎨 GENERATING EMBEDDING VISUALIZATION")
        print("="*70)
        print("Creating 2D projection using t-SNE...")

        # Convert to numpy array
        embeddings = np.array(results['embeddings'])

        # Reduce to 2D using t-SNE
        print(f"   Reducing {embeddings.shape[0]} embeddings from {embeddings.shape[1]}D to 2D...")
        tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, embeddings.shape[0]-1))
        embeddings_2d = tsne.fit_transform(embeddings)

        # Create visualization
        plt.figure(figsize=(12, 8))

        # Color by file_name if available
        if results['metadatas']:
            file_names = [m.get('file_name', 'Unknown') for m in results['metadatas']]
            unique_files = list(set(file_names))
            color_map = {file: i for i, file in enumerate(unique_files)}
            colors = [color_map[f] for f in file_names]

            scatter = plt.scatter(
                embeddings_2d[:, 0],
                embeddings_2d[:, 1],
                c=colors,
                cmap='tab20',
                alpha=0.6,
                s=50
            )

            # Add legend for top files
            top_files = Counter(file_names).most_common(10)
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=plt.cm.tab20(color_map[file]/20),
                          label=file, markersize=8)
                for file, count in top_files
            ]
            plt.legend(handles=legend_elements, loc='best', fontsize=8)
        else:
            plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], alpha=0.6)

        plt.title('Document Embeddings Visualization (t-SNE)', fontsize=14, fontweight='bold')
        plt.xlabel('Dimension 1')
        plt.ylabel('Dimension 2')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save plot
        output_file = 'chromadb_visualization.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n✅ Visualization saved to: {output_file}")

        # Try to display
        try:
            plt.show(block=False)
            print("   (Displaying in window...)")
        except:
            print("   (Could not display - check the saved PNG file)")

    except ImportError as e:
        print(f"\n⚠️  Missing library: {e}")
        print("Install with: pip install scikit-learn matplotlib")
    except Exception as e:
        print(f"\n❌ Error creating visualization: {e}")

def search_similar(collection, query_text, top_k=5):
    """Find similar documents to a query"""

    print("\n🔍 SIMILARITY SEARCH")
    print("="*70)
    print(f"Query: \"{query_text}\"")
    print(f"Finding top {top_k} most similar documents...\n")

    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances']
    )

    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 - distance  # Convert distance to similarity
        print(f"[{i}] Similarity: {similarity:.1%}")
        print(f"    File: {metadata.get('file_name', 'Unknown')}")
        print(f"    Preview: {doc[:200]}...")
        print()

def export_stats(results):
    """Export database statistics to JSON"""

    stats = {
        'total_chunks': len(results['ids']),
        'unique_documents': len(set(m.get('file_name', 'Unknown') for m in results['metadatas'])),
        'embedding_dimensions': len(results['embeddings'][0]) if results['embeddings'] else 0,
        'documents': []
    }

    if results['metadatas']:
        file_counts = Counter(m.get('file_name', 'Unknown') for m in results['metadatas'])
        stats['documents'] = [
            {'file_name': file, 'chunks': count}
            for file, count in file_counts.most_common()
        ]

    output_file = 'chromadb_stats.json'
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n💾 Statistics exported to: {output_file}")

def main():
    print("\n" + "="*70)
    print("ChromaDB Visualization Tool for JiraDocAI")
    print("="*70)

    # Analyze database
    collection, results = analyze_database()

    # Show menu
    while True:
        print("\n" + "="*70)
        print("OPTIONS")
        print("="*70)
        print("1) Visualize embeddings (2D plot)")
        print("2) Search similar documents")
        print("3) Export statistics to JSON")
        print("4) Show all document names")
        print("5) Exit")
        print()

        choice = input("Choose an option [1-5]: ").strip()

        if choice == '1':
            visualize_embeddings(results)

        elif choice == '2':
            query = input("\nEnter search query: ").strip()
            if query:
                search_similar(collection, query, top_k=5)

        elif choice == '3':
            export_stats(results)

        elif choice == '4':
            print("\n📚 ALL DOCUMENTS")
            print("="*70)
            if results['metadatas']:
                file_counts = Counter(m.get('file_name', 'Unknown') for m in results['metadatas'])
                for i, (file, count) in enumerate(file_counts.most_common(), 1):
                    print(f"{i:3d}. {file} ({count} chunks)")

        elif choice == '5':
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
