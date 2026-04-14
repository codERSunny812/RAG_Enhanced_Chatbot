# RAG-Enhanced Insurance Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Indian health insurance
policy documents, built with LLaMA3.2, FAISS, and React.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| LLM | LLaMA3.2 3B via Ollama |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | FAISS (IndexFlatL2) |
| PDF Parsing | pdfplumber |

## Project Structure
'''javascript
Mini Project(RAG)/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Global settings
│   ├── data/raw_pdfs/       # Insurance PDF documents
│   ├── ingest/              # PDF loading, chunking, embedding
│   ├── vectordb/            # FAISS index + metadata
│   ├── rag/                 # Pipeline, prompt, cache
│   └── api/                 # /chat and /ingest routes
├── frontend/
│   └── src/
│       ├── components/      # Navbar, Hero, Chatbot, etc.
│       └── api/chatApi.js   # Backend API calls
├── evaluation/
│   ├── test_questions.json  # 40 test questions
│   ├── eval_runner.py       # Evaluation script
│   ├── eval_results.json    # Detailed results
│   └── eval_report.txt      # Summary report
└── docker-compose.yml
'''


## Dataset

6 Indian health insurance PDFs:

- Health Insurance Policy Retail (GEN633)
- United India CSC Individual Health Insurance
- Health Companion Health Insurance Plan
- Group Health Insurance Policy
- IRDAI Master Circular on Health Insurance 2024
- Tata AIG Wellsurance Family Policy

**Total chunks:** 689 (chunk size=700, overlap=150)

## Setup & Run

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama installed → <https://ollama.ai>

### 1. Clone and setup

```bash
git clone <your-repo-url>
cd "Mini Project(RAG)"
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Start Ollama

```bash
ollama pull llama3.2
ollama run llama3.2
```

### 3. Build the vector index

```bash
cd backend
python3 -m vectordb.store
```

### 4. Start backend

```bash
cd backend
uvicorn main:app --reload
```

### 5. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

### Docker (alternative)

```bash
docker-compose build
docker-compose up
```

## Evaluation Results

| Metric | Score |
|---|---|
| Keyword Accuracy | 69.9% |
| Faithfulness Score | 97.5% |
| Avg Response Time | 12.95s |
| Total Questions | 40 |

## RAG Pipeline

User Query
↓
Embedding (all-MiniLM-L6-v2)
↓
FAISS Similarity Search (Top-7 chunks)
↓
Prompt Builder (query + retrieved context)
↓
LLaMA3.2 via Ollama
↓
Answer + Source Attribution




## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /chat | Send query, get RAG answer |
| POST | /ingest | Upload new PDF to knowledge base |
| GET | / | Health check |

## Sample Questions to Ask

- What is the waiting period for pre-existing diseases?
- What expenses are covered during hospitalization?
- Is maternity benefit covered?
- What is the no claim bonus?
- Are daycare procedures covered?
- What is the grievance redressal process?
