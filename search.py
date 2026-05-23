import os
import sys
import numpy as np
from ingest import read_file
from embedder import get_embedding, build_index

def run_semantic_search(data_dir, query):
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found.")
        sys.exit(1)
        
    print(f"Loading documents from {data_dir}...")
    documents = []
    filenames = []
    
    for filename in os.listdir(data_dir):
        if not filename.lower().endswith(('.pdf', '.txt')):
            continue
            
        file_path = os.path.join(data_dir, filename)
        text = read_file(file_path)
        
        # We index the raw text for semantic search
        if text.strip():
            documents.append(text)
            filenames.append(filename)
            
    if not documents:
        print("No documents found to index.")
        sys.exit(0)
        
    print(f"Building local embeddings FAISS index for {len(documents)} documents using CPU... Please hold.")
    index = build_index(documents)
    
    # Generate query embedding
    query_vector = get_embedding(query).reshape(1, -1)
    
    # Retrieve top 3
    distances, indices = index.search(query_vector, min(3, len(documents)))
    
    print(f"\n==========================================")
    print(f"SEMANTIC SEARCH RESULTS")
    print(f"Query: '{query}'")
    print(f"==========================================\n")
    
    for i in range(len(indices[0])):
        idx = indices[0][i]
        if idx != -1: 
            # FAISS uses L2 distance; lower is closer
            dist = distances[0][i]
            # Show a snippet of the text
            snippet = documents[idx][:200].replace('\n', ' ').strip() + "..."
            
            print(f"Rank {i+1} | Distance: {dist:.4f}")
            print(f"File: {filenames[idx]}")
            print(f"Snippet: {snippet}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python search.py <documents_directory> \"<query string>\"")
        print("Example: python search.py ./documents \"invoices with payment due in January\"")
        sys.exit(1)
        
    run_semantic_search(sys.argv[1], sys.argv[2])
