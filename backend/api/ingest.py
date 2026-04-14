from fastapi import APIRouter, UploadFile, File
import shutil, os
from config import DATA_DIR
from ingest.pdf_loader import load_pdfs_from_folder
from ingest.chunker import chunk_documents
from ingest.embedder import generate_embeddings
from vectordb.store import save_index

router = APIRouter()

@router.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    # Save uploaded PDF to raw_pdfs folder
    save_path = os.path.join(DATA_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Re-run full pipeline
    docs   = load_pdfs_from_folder()
    chunks = chunk_documents(docs)
    chunks = generate_embeddings(chunks)
    save_index(chunks)

    return {
        "message": f"'{file.filename}' ingested successfully.",
        "total_chunks": len(chunks)
    }