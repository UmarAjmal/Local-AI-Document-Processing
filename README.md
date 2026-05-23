# 🧠 Local AI Document Processing Pipeline

## 📌 Project Overview
This project is a very accessible, offline, CPU friendly Document Processing and Semantic Search pipeline. It was built with strict constraints: no external APIs (like OpenAI or Claude), no heavy GPUs, and only local open source libraries.

It takes a folder of mixed PDFs and text files and automatically:
1. **Classifies** them (Invoice, Resume, Utility Bill, Other).
2. **Extracts** structured data (Names, Amounts, Dates, etc.).
3. Creates a **Deep Hybrid Semantic Search** engine to chat with your documents.

We added super easy English comments inside the code so anyone can understand exactly what is happening where.

---

## 🏗️ Architecture and How It Works (Step by Step)

### 1. Ingestion (ingest.py)
* **What it does:** Reads raw text from .pdf and .txt files.
* **Library used:** pdfminer.six
* **Why?** PDFs often store text in weird geometrical blocks rather than clean lines. pdfminer is a lightweight, offline way to rip raw text accurately without needing a heavy OCR model.

### 2. Intelligent Classification (classifier.py)
* **What it does:** Decides if a document is an Invoice, Resume, Utility Bill, or Other.
* **How it works:** Instead of relying on the file name or a single keyword, it uses a **Keyword Density Scoring System**. It scans the entire document for vocabularies (e.g., tax, subtotal, experience, kwh). The category with the highest density score wins.
* **Why?** Since we cannot use heavy ML models due to CPU constraints, this heuristic approach reliably mimics ML classification and avoids false positives.

### 3. Smart Extraction (extractor.py)
* **What it does:** Extracts strict parameters (e.g., total_amount, invoice_number, experience_years).
* **How it works:** Uses robust Python Regex intertwined with geometric rule based algorithms. 
  * *Mathematical Fallback:* Instead of looking for the exact phrase Total Amount, the system collects all currency formats globally in the document and assumes the Maximum Value is the Total Amount.
  * *Geometric Fallback:* For Company Names or Candidate Names, if explicit labels are not found, it defaults to the first non generic, capitalized Title line (ignoring words like LOGO).
* **Why?** Pure Regex fails on arbitrary PDF layouts. Adding these algorithmic fallbacks creates AI like intelligence using just math and logic.

### 4. Vector Embeddings and Indexing (embedder.py)
* **What it does:** Converts human words into mathematical numbers (vectors) so the computer understands context.
* **Libraries used:** sentence-transformers (all-MiniLM-L6-v2) and faiss-cpu.
* **Why?** all-MiniLM-L6-v2 is a tiny (~90MB) NLP model that runs lightning fast on CPUs. faiss-cpu is the industry standard for searching millions of vectors in milliseconds.

### 5. Deep Hybrid Search Orchestrator (main.py)
* **What it does:** Glues everything together and runs the interactive terminal search.
* **Deep Chunking Mechanism:** A massive issue with local AI is the Token Limit (MiniLM only reads the first ~256 words). We solved this by implementing an overlapping Sliding Window Chunking algorithm. The script cuts PDFs into 100 word chunks with 25 word overlap so no deep detail (like an academic transcript mark) is lost or truncated.
* **Hybrid Search (Dense + Sparse):** Semantic AI is great for meaning but terrible at exact matches (like INV-000216). We implemented a Hybrid Scoring algorithm:
  * Dense Score: FAISS calculates semantic distance.
  * Sparse/Lexical Bonus: Standard Python logic bumps up the rank score massively if an exact ID or extracted keyword physically matches the search query.

---

## 🚀 How to Run

### Installation
Ensure you are using Python 3.10+ and a virtual environment.
\\ash
pip install -r requirements.txt
\*(Note: requires numpy<2 for FAISS compatibility)*

### Execution
Place your documents in a ./documents folder, then run:

\\ash
python main.py
\
The system will process the documents, save the parameters to output.json, and automatically drop you into an interactive chat prompt.
