# 🧠 Local AI Document Processing Pipeline

## 📌 Project Overview
This project is a very accessible, offline, CPU friendly Document Processing and Semantic Search pipeline. It leverages local open source AI without requiring external APIs (like OpenAI) or heavy GPUs. 

We added super easy English comments inside the code so anyone can understand exactly what is happening where.

---

## ❓ Required Information

### 1. What libraries and methods were used?
**Libraries Used:**
* **pdfminer.six:** For safely extracting raw text from geometrical PDF blocks.
* **sentence-transformers (all-MiniLM-L6-v2):** A fast, lightweight (~90MB) NLP model for offline vector embeddings on the CPU.
* **faiss-cpu:** A high performance vector database by Meta to rapidly search vector semantics.
* **numpy:** Restricted to versions < 2.0 for solid FAISS compatibility.
* **re (Regex):** Standard Python library for robust pattern matching.

**Methods & Architecture Used:**
* **Keyword Density Scoring Method:** Classifies documents by counting targeted vocabularies instead of relying on heavy ML models that choke CPUs.
* **Geometric & Mathematical Extraction Methods:** Uses math logic (e.g., getting the max() currency in an invoice as Total Amount) to bypass rigid regex limits on unpredictable PDFs.
* **Sliding Window Chunking Method:** Solves the 256 word token limit of local AI models by splitting documents into 100 word chunks with a 25 word overlap for maximum context retention.
* **Hybrid Search Score Method (Dense + Sparse):** Combines FAISS Semantic Search distances with Lexical/Keyword bonuses. If a query asks for an exact ID like INV-000216, the search score accurately pushes the exact literal match to Rank 1.

---

### 2. How to install dependencies?
Ensure you are using Python 3.10+ and it is highly recommended to use a virtual environment.

Run this simple command in your terminal:
\\\ash
pip install -r requirements.txt
\\\
*(Note: It will lock numpy on an older version to keep faiss-cpu from crashing).*

---

### 3. How to run the program locally?

**Step 1:** Place all your PDF and TXT files inside a folder named \documents\ right next to the code files.

**Step 2:** Run the main orchestrator script from your terminal:
\\\ash
python main.py
\\\

**What will happen next?**
1. The AI will ingest, classify, and extract data from all your files.
2. It will save the extracted structured results inside a file called \output.json\.
3. It will automatically load the chunks into the Vector Database and drop you into an interactive chat prompt.
4. You can type queries to search your documents.
5. Type \exit\ or \ye\ to stop the system.
