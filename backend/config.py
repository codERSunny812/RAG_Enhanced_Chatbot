import os
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw_pdf")

# Chunking
CHUNK_SIZE = 700
CHUNK_OVERLAP = 150

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM
OLLAMA_MODEL = "llama3.2"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_URL  = f"http://{OLLAMA_HOST}:11434/api/generate"

# Retrieval
TOP_K = 7