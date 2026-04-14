import os
import json
import numpy as np
import faiss
from config import BASE_DIR


# Paths where FAISS index and metadata will be saved
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "vectordb", "faiss_index.bin")
METADATA_PATH    = os.path.join(BASE_DIR, "vectordb", "metadata.json")


def save_index(chunks: list[dict]):
    """
    Takes chunks with embeddings, builds FAISS index, saves to disk.
    Also saves metadata (source, chunk_id, text) separately as JSON.
    """
    embeddings = np.array([chunk["embedding"] for chunk in chunks]).astype("float32")

    dimension = embeddings.shape[1]  # 384
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save FAISS binary index
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"[OK] FAISS index saved → {FAISS_INDEX_PATH}")
    print(f"[INFO] Total vectors in index: {index.ntotal}")

    # Save metadata (everything except the embedding array)
    metadata = []
    for chunk in chunks:
        metadata.append({
            "source":   chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text":     chunk["text"]
        })

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"[OK] Metadata saved  → {METADATA_PATH}")


def load_index():
    """
    Loads FAISS index and metadata from disk.
    Returns (index, metadata_list)
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}. Run store.py first.")

    index    = faiss.read_index(FAISS_INDEX_PATH)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"[OK] Loaded FAISS index with {index.ntotal} vectors.")
    return index, metadata


# Quick test
if __name__ == "__main__":
    from ingest.pdf_loader  import load_pdfs_from_folder
    from ingest.chunker     import chunk_documents
    from ingest.embedder    import generate_embeddings

    docs   = load_pdfs_from_folder()
    chunks = chunk_documents(docs)
    chunks = generate_embeddings(chunks)

    save_index(chunks)

    # Verify by reloading
    print("\n--- Verifying saved index ---")
    index, metadata = load_index()
    print(f"Vectors in index : {index.ntotal}")
    print(f"Metadata entries : {len(metadata)}")
    print(f"Sample metadata  : {metadata[0]}")