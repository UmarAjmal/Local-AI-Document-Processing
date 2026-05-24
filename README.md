# 🧠 Local AI Document Processing Pipeline
 
> **100% offline. No API keys. No GPU required. Runs entirely on your CPU.**
 
A complete document intelligence system that ingests PDFs and text files, classifies them automatically, extracts structured data, and lets you search across all your documents using natural language all through a sleek web UI or the command line.
 
---

## 📌 Demo Video Link
https://drive.google.com/file/d/1ox5C-ImIz8q7DkobAQwWwGvq9PLhn6zS/view?usp=sharing

--- 

## 📌 Project Overview
 
This pipeline combines classical NLP techniques with modern vector search to process documents locally. It was built to be beginner-friendly (heavy English comments inside every file), lightweight (runs on a basic laptop), and completely private (zero external API calls).
 
**What it can do:**
- Auto-classify documents as **Invoice**, **Resume**, **Utility Bill**, or **Other**
- Extract structured fields (names, emails, invoice numbers, amounts, account numbers, etc.)
- Build a **semantic vector search index** from all your documents using FAISS
- Answer natural language queries via a **chat-style web interface** (Flask)
- Save all extracted results to `output.json`
---
 
## 🗂️ Project Structure
 
```
Local-AI-Document-Processing/
│
├── app.py                    # Flask web server + API routes + chat endpoint
├── ingest.py                 # File reader (PDF + TXT support)
├── classifier.py             # Document classifier (keyword density scoring)
├── extractor.py              # Structured field extractor (regex-based)
├── embedder.py               # Sentence-Transformer + FAISS index builder
├── search.py                 # Standalone CLI semantic search script
│
├── doc_pipeline/             # Earlier modular version of classifier + extractor
│   ├── classifier.py
│   └── extractor.py
│
├── documents/                # Put your PDF and TXT files here
│   ├── *.pdf
│   └── *.txt
│
├── templates/
│   └── index.html            # Glassmorphism chat UI (served by Flask)
│
├── output.json               # Auto-generated: extracted structured data
└── requirements.txt          # All dependencies
```
 
---
 
## ❓ Required Questions Fully Answered
 
---
 
### 1. 📦 How to Install Dependencies
 
**Requirements:** Python 3.10 or higher. A virtual environment is strongly recommended.
 
**Step 1 Create and activate a virtual environment:**
 
```bash
# Windows
python -m venv venv
venv\Scripts\activate
 
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
 
**Step 2 Install all dependencies:**
 
```bash
pip install -r requirements.txt
```
 
> ⚠️ **Important:** `requirements.txt` intentionally pins `numpy` to a version below 2.0 because `faiss-cpu==1.8.0` is not compatible with NumPy 2.x. Do not manually upgrade numpy or FAISS will crash.
 
**What gets installed:**
 
| Package | Version | Purpose |
|---|---|---|
| `pdfminer.six` | 20231228 | PDF text extraction |
| `sentence-transformers` | 2.7.0 | Local AI embeddings (downloads ~90MB model on first run) |
| `faiss-cpu` | 1.8.0 | Vector similarity search database by Meta |
| `flask` | (auto) | Web server for the UI |
| `werkzeug` | (auto) | File upload handling |
| `numpy` | < 2.0 | Array math (pinned for FAISS compatibility) |
 
> 📡 On **first run**, `sentence-transformers` will automatically download the `all-MiniLM-L6-v2` model (~90MB) from HuggingFace. After that, it works fully offline.
 
---
 
### 2. 🚀 How to Run the Program Locally
 
There are **two ways** to run this project:
 
---
 
#### ▶️ Option A Web UI (Recommended)
 
This launches a full chat interface in your browser where you can upload documents and search them conversationally.
 
**Step 1 Place your documents** inside the `documents/` folder (PDF or TXT files).
 
**Step 2 Start the Flask server:**
 
```bash
python app.py
```
 
**Step 3 Open your browser and go to:**
 
```
http://127.0.0.1:5000
```
 
**What happens automatically:**
1. On startup, Flask reads every PDF/TXT in `documents/`, classifies and extracts structured fields from each one
2. Builds a FAISS semantic vector index from all document chunks in memory
3. Saves extracted results to `output.json`
4. The web UI opens you can upload new documents using the sidebar button
5. Type any natural language query in the chat box (e.g., *"show me invoices with amount over 5000"* or *"find resumes with Python skills"*)
6. The system returns the top 3 most relevant document matches with snippets
---
 
#### ▶️ Option B CLI Semantic Search Only
 
If you just want to run a quick one-off search from the terminal without the web UI:
 
```bash
python search.py ./documents "your query here"
```
 
**Example:**
 
```bash
python search.py ./documents "invoices with payment due in January"
```
 
**Output:** Ranks top 3 documents by semantic similarity, showing filename, L2 distance score, and a 200-character snippet.
 
---
 
### 3. 📚 What Libraries and Methods Were Used
 
---
 
#### 🔧 Libraries
 
| Library | What It Does in This Project |
|---|---|
| **`pdfminer.six`** | Extracts raw text from PDF files using geometric PDF block analysis. More reliable on complex layouts than basic PDF readers. Used in `ingest.py` via `pdfminer.high_level.extract_text()` |
| **`sentence-transformers`** | Loads the `all-MiniLM-L6-v2` model (~90MB) locally to convert text chunks into 384-dimensional vectors. Runs entirely on CPU. Used in `embedder.py` |
| **`faiss-cpu`** | Meta's high-performance vector database. Stores all document embeddings and performs fast nearest-neighbor search using L2 distance. Used in `embedder.py` and `app.py` |
| **`flask`** | Lightweight Python web framework. Serves the chat UI, handles file uploads, and exposes REST API endpoints (`/api/chat`, `/api/upload`, `/api/documents`, `/api/output`) |
| **`werkzeug`** | Used via `secure_filename()` to safely sanitize uploaded filenames before saving to disk |
| **`numpy`** | Used to convert sentence embeddings to float32 arrays and reshape query vectors before passing them to FAISS |
| **`re` (built-in)** | Python's standard regex library. Used extensively in `extractor.py` for field extraction (dates, emails, phone numbers, invoice numbers, amounts, account numbers) |
| **`json` (built-in)** | Used to serialize and save extracted document fields to `output.json` |
| **`os` (built-in)** | Used to walk the documents directory, check file extensions, and manage upload paths |
 
---
 
#### 🧠 Methods & Architecture
 
**1. Keyword Density Scoring (Classification)**
> File: `classifier.py`
 
Instead of using a heavy ML model for classification, the system scores each document by counting how many weighted vocabulary words from each category appear in the text. Each keyword has a custom weight (e.g., `'sngpl': 5` for Utility Bills, `'resume': 4` for Resumes). The category with the highest total score wins. A minimum threshold of 4.0 points is required below that, the document is tagged `Other`.
 
**2. Geometric & Mathematical Field Extraction (Extractor)**
> File: `extractor.py`
 
Uses a set of document-class-specific regex patterns. For Invoices, it uses the mathematical assumption that the largest number in the document is usually the Total Amount (`max(money_floats)`). For Resumes, it finds names by looking for short all-alpha lines near the top. For Utility Bills, it hunts for 11–14 digit consumer IDs with negative lookbehind to avoid capturing years from date strings.
 
**3. Sliding Window Chunking (app.py)**
> File: `app.py` `build_search_database()`
 
Because the `all-MiniLM-L6-v2` model has a 256-word token limit, each document is split into overlapping chunks of **100 words with a 25-word overlap**. This means no context is lost at chunk boundaries. Each chunk also carries metadata (filename, document type, extracted fields) so search results are rich.
 
**4. Hybrid Search Score (Dense + Sparse)**
> File: `app.py` `/api/chat` route
 
The search ranking combines two signals:
- **Semantic score**: `1.0 / (1.0 + FAISS_L2_distance)` higher is better, based on vector similarity
- **Keyword bonus**: `+2.0` if a query token appears in extracted fields or filename, `+1.0` if it appears in the raw chunk text
This means an exact literal match (like an invoice number `INV-000216`) will be correctly ranked #1 even if the semantic embedding doesn't fully capture it.
 
**5. FAISS IndexFlatL2**
> File: `embedder.py`
 
Uses a flat (brute-force) L2 index no approximation, 100% accurate results. Appropriate for small-to-medium document sets on CPU without needing GPU or an ANN index like IVF or HNSW.
 
---
 
## 🖥️ Web UI Features
 
The `templates/index.html` UI (served by Flask) includes:
 
- **Glassmorphism dark sidebar** lists all loaded documents
- **Upload button** drag & drop or pick multiple PDFs/TXTs; triggers automatic reprocessing
- **Chat interface** ask natural language questions, get ranked document results with snippets
- **Extracted data panel** view structured JSON output per document
---
 
## 📁 Supported File Types
 
| Format | Support |
|---|---|
| `.pdf` | ✅ Full support via pdfminer.six |
| `.txt` | ✅ Full support via standard Python file I/O |
| `.docx`, `.xlsx`, etc. | ❌ Not supported (extend `ingest.py` to add) |
 
---
 
## 📊 Document Types Supported
 
| Type | Extracted Fields |
|---|---|
| **Invoice** | `invoice_number`, `date`, `company`, `total_amount` |
| **Resume** | `name`, `email`, `phone`, `experience_years` |
| **Utility Bill** | `account_number`, `date`, `usage_kwh`, `amount_due` |
| **Other** | `class: Other` only |
 
---
 
## ⚡ Performance Notes
 
- Model download happens **once** on first run (~90MB), then cached locally
- Index builds in memory each time the server starts (fast for <500 docs)
- All processing is **CPU-only** no CUDA/GPU needed
- Tested on Python 3.10+ with Windows, macOS, and Linux
---
 
## 🙋 Author
 
**Muhammad Umar Ajmal** AI Engineer & Generative AI Specialist  
[GitHub](https://github.com/UmarAjmal) · [Portfolio](https://muhammadumarajmal.vercel.app/) · [LinkedIn](https://linkedin.com/in/muhammad-umar-ajmal-developer)
