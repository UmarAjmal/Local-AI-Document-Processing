import os
import sys
import json
import re
from ingest import read_file
from classifier import classify_document
from extractor import extract_fields
from embedder import get_embedding, build_index

def main(data_dir):
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} not found.")
        sys.exit(1)
        
    results = {}
    
    # We will chunk documents into parts instead of reading them all at once
    chunks_meta = [] 
    chunk_texts = []
    
    print("=========================================================")
    print("STARTING LOCAL AI DOCUMENT PROCESSOR")
    print("=========================================================")
    print("Processing files, please wait...\n")
    
    # Loop through every file inside our folder
    for filename in os.listdir(data_dir):
        # We only care about text or pdf files
        if not filename.lower().endswith(('.pdf', '.txt')):
            continue
            
        file_path = os.path.join(data_dir, filename)
        print(f"Reading {filename}...")
        
        # 1. Read the text from the document
        text = read_file(file_path)
        
        # 2. Check what kind of document it is
        doc_class = classify_document(text)
        
        # 3. Pull out the useful data like names or amounts
        extracted_data = extract_fields(text, doc_class)
        results[filename] = extracted_data
        
        # 4. Break the document into small pieces so our local AI can understand it without failing
        if text.strip():
            words = text.split()
            chunk_size = 100 # How many words we want per chunk
            overlap = 25     # Keep old words in new chunk so we do not cut sentences in half
            
            for i in range(0, max(1, len(words)), max(1, chunk_size - overlap)):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                # Link all extracted facts with the chunk so the AI knows the context
                meta_string = f"File: {filename}. Type: {doc_class}. Data: {json.dumps(extracted_data)}. Paragraph: {chunk_text}"
                chunk_texts.append(meta_string)
                
                # Save details for the results menu later
                chunks_meta.append({
                    "filename": filename,
                    "chunk": chunk_text,
                    "extracted": extracted_data
                })
        
    # Write everything into the JSON file
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print("\n Pipeline complete. Output saved to 'output.json'.")
    print("\n" + "+" + "-"*28 + "+" + "-"*15 + "+" + "-"*40 + "+")
    print(f"| {'Filename':<26} | {'Category':<13} | {'Extracted Details':<38} |")
    print("+" + "-"*28 + "+" + "-"*15 + "+" + "-"*40 + "+")
    for fname, data in results.items():
        doc_class = data.get('class', 'Unknown')
        # Create a tiny snap of data to show in cell
        details_str = str(data)[:35] + "..." if len(str(data)) > 35 else str(data)
        print(f"| {fname[:26]:<26} | {doc_class[:13]:<13} | {details_str:<38} |")
    print("+" + "-"*28 + "+" + "-"*15 + "+" + "-"*40 + "+")

    if not chunk_texts:
        print("\n❌ No valid text documents found to build search index.")
        return

    # 5. Build our fast offline search database
    print("\n=========================================================")
    print("INITIALIZING DEEP HYBRID SEARCH AI")
    print("=========================================================")
    print("Building local AI database... Please hold.")
    index = build_index(chunk_texts)
    
    print("\n" + "="*70)
    print("WELCOME TO YOUR LOCAL AI SEARCH ASSISTANT")
    print("="*70)
    print("Instructions: Type what you are looking for (e.g., 'total amount').")
    print("Type 'exit', 'bye', or '0' to safely close the program.")
    print("="*70)
    
    while True:
        try:
            query = input("\nYou: ").strip()
        except KeyboardInterrupt:
            break
            
        if query.lower() in ['exit', 'bye', '0', 'quit']:
            print("\nAI: Goodbye! Have a great day!")
            break
            
        if not query:
            continue
            
        # Convert user question into numbers and find similar chunks
        query_vector = get_embedding(query).reshape(1, -1)
        distances, indices = index.search(query_vector, min(10, len(chunk_texts)))
        
        # Break user query down into standard words to do manual matching
        query_tokens = set(re.findall(r'\b[A-Za-z0-9\-]{3,}\b', query.lower()))
        
        ranked_results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx == -1: continue
            
            dist = distances[0][i]
            # Convert math distance into a score where 1.0 is perfect match
            semantic_score = 1.0 / (1.0 + dist)
            
            keyword_bonus = 0.0
            meta = chunks_meta[idx]
            chunk_str = meta['chunk'].lower()
            extracted_str = str(meta['extracted']).lower()
            fname_str = meta['filename'].lower()
            
            # Give extra points if words match exactly. Good for IDs and names
            for token in query_tokens:
                if token in extracted_str or token in fname_str:
                    keyword_bonus += 2.0  
                elif token in chunk_str:
                    keyword_bonus += 1.0 # Added more points for matching inside chunk text
                    
            final_score = semantic_score + keyword_bonus
            
            ranked_results.append({
                "filename": meta['filename'],
                "score": final_score,
                "semantic": semantic_score,
                "bonus": keyword_bonus,
                "chunk": meta['chunk']
            })
            
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter duplicates filenames to show top distinct matches
        seen_files = set()
        display_results = []
        for res in ranked_results:
            if res['filename'] not in seen_files:
                display_results.append(res)
                seen_files.add(res['filename'])
            if len(display_results) == 3:
                break
        
        print(f"\n--- TOP RESULTS ---")
        for i, res in enumerate(display_results):
            snippet = res['chunk'][:250].replace('\n', ' ').strip()
            print(f"Rank {i+1} | {res['filename']}")
            print(f"Match Score: {res['score']:.2f}")
            print(f"Relevant Segment: ...{snippet}...\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        data_dir = "./documents"
    else:
        data_dir = sys.argv[1]
    main(data_dir)
