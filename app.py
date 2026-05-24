import os
import json
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Import modules from the project
from ingest import read_file
from classifier import classify_document
from extractor import extract_fields
from embedder import get_embedding, build_index

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './documents'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables to hold our AI search database in memory
GLOBAL_INDEX = None
CHUNKS_META = []
CHUNK_TEXTS = []

def build_search_database():
    """Reads all valid documents in the folder, parses them, and builds the FAISS index."""
    global GLOBAL_INDEX, CHUNKS_META, CHUNK_TEXTS
    
    data_dir = app.config['UPLOAD_FOLDER']
    chunks_meta = []
    chunk_texts = []
    results = {}
    
    for filename in os.listdir(data_dir):
        if not filename.lower().endswith(('.pdf', '.txt')):
            continue
            
        file_path = os.path.join(data_dir, filename)
        text = read_file(file_path)
        doc_class = classify_document(text)
        extracted_data = extract_fields(text, doc_class)
        results[filename] = extracted_data
        
        if text.strip():
            words = text.split()
            chunk_size = 100 
            overlap = 25 
            
            for i in range(0, max(1, len(words)), max(1, chunk_size - overlap)):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                meta_string = f"File: {filename}. Type: {doc_class}. Data: {json.dumps(extracted_data)}. Paragraph: {chunk_text}"
                chunk_texts.append(meta_string)
                
                chunks_meta.append({
                    "filename": filename,
                    "chunk": chunk_text,
                    "extracted": extracted_data,
                    "type": doc_class
                })
    
    # Save the output JSON just like the CLI does
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    # Build FAISS index if we have chunks
    if chunk_texts:
        GLOBAL_INDEX = build_index(chunk_texts)
    else:
        GLOBAL_INDEX = None
        
    CHUNKS_META = chunks_meta
    CHUNK_TEXTS = chunk_texts
    
    return len(results)

# Build the database once when server starts
print("Building initial AI search index...")
build_search_database()
print("Ready!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Returns a list of correctly processed documents found in the folder."""
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith(('.pdf', '.txt'))]
    return jsonify({"documents": files})

@app.route('/api/output', methods=['GET'])
def get_output():
    """Returns the parsed output.json results."""
    try:
        with open("output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handles multiple file uploads from UI, stops them into folder and runs processing."""
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400
        
    files = request.files.getlist('files')
    uploaded_count = 0
    
    for file in files:
        if file.filename == '':
            continue
        if file.filename.lower().endswith(('.pdf', '.txt')):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_count += 1
            
    # Trigger full reprocessing to include new files into the AI database
    if uploaded_count > 0:
        processed_count = build_search_database()
        return jsonify({"message": "Success", "processed_count": processed_count})
        
    return jsonify({"error": "Invalid files"}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple replica of the CLI deep search to talk with the frontend."""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"reply": "Please ask a valid question."})
        
    if not GLOBAL_INDEX or not CHUNK_TEXTS:
        return jsonify({"reply": "I have no documents inside my database to search. Please upload some!"})
        
    # Vector Search
    query_vector = get_embedding(query).reshape(1, -1)
    distances, indices = GLOBAL_INDEX.search(query_vector, min(10, len(CHUNK_TEXTS)))
    
    query_tokens = set(re.findall(r'\b[A-Za-z0-9\-]{3,}\b', query.lower()))
    
    ranked_results = []
    for i in range(len(indices[0])):
        idx = indices[0][i]
        if idx == -1: continue
        
        dist = distances[0][i]
        semantic_score = 1.0 / (1.0 + dist)
        keyword_bonus = 0.0
        
        meta = CHUNKS_META[idx]
        chunk_str = meta['chunk'].lower()
        extracted_str = str(meta['extracted']).lower()
        fname_str = meta['filename'].lower()
        
        for token in query_tokens:
            if token in extracted_str or token in fname_str:
                keyword_bonus += 2.0  
            elif token in chunk_str:
                keyword_bonus += 1.0 
                
        final_score = semantic_score + keyword_bonus
        
        ranked_results.append({
            "filename": meta['filename'],
            "type": meta['type'],
            "score": final_score,
            "chunk": meta['chunk']
        })
        
    ranked_results.sort(key=lambda x: x['score'], reverse=True)
    
    seen_files = set()
    display_results = []
    for res in ranked_results:
        if res['filename'] not in seen_files:
            display_results.append(res)
            seen_files.add(res['filename'])
        if len(display_results) == 3:
            break
            
    # Format the Assistant's reply
    if not display_results:
        return jsonify({"reply": "I couldn't find any relevant information regarding your query."})
        
    reply_lines = [f"**Found these top {len(display_results)} matches for your query:**\n"]
    for i, res in enumerate(display_results):
        snippet = res['chunk'][:200].replace('\n', ' ').strip()
        reply_lines.append(f"**{i+1}. {res['filename']}** ({res['type']})")
        reply_lines.append(f"> \"...{snippet}...\"\n")
        
    return jsonify({"reply": "\n".join(reply_lines)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
