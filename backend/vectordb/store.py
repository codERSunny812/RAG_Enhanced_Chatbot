import numpy as np
import pickle
import json
import os
import faiss

# Paths - adjust based on your actual file locations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "vectordb", "faiss_index.bin")
METADATA_PATH = os.path.join(BASE_DIR, "vectordb", "metadata.json")


def save_index(chunks: list[dict]):
    """
    Save FAISS index and metadata to disk.
    chunks: list of dicts with 'embedding', 'source', 'chunk_id', 'text'
    """
    if not chunks:
        print("[WARN] No chunks to save")
        return
    
    # Extract embeddings
    embeddings = np.array([c["embedding"] for c in chunks]).astype("float32")
    dimension = embeddings.shape[1]
    
    # Create and save FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    # Save metadata (without embeddings to save space)
    metadata = []
    for c in chunks:
        metadata.append({
            "source": c["source"],
            "chunk_id": c["chunk_id"],
            "text": c["text"]
        })
    
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved FAISS index with {len(chunks)} vectors to {FAISS_INDEX_PATH}")
    print(f"[OK] Saved metadata for {len(metadata)} chunks to {METADATA_PATH}")


def load_index():
    """
    Load FAISS index and metadata from disk.
    Returns (index, metadata)
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"[WARN] FAISS index not found at {FAISS_INDEX_PATH}")
        print("[INFO] Please run ingestion first to create the index.")
        # Return empty index and metadata
        return faiss.IndexFlatL2(384), []  # 384 is embedding dimension
    
    if not os.path.exists(METADATA_PATH):
        print(f"[WARN] Metadata not found at {METADATA_PATH}")
        return faiss.IndexFlatL2(384), []
    
    try:
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        print(f"[OK] Loaded FAISS index with {index.ntotal} vectors")
        print(f"[OK] Loaded metadata for {len(metadata)} chunks")
        return index, metadata
    except Exception as e:
        print(f"[ERROR] Failed to load index: {e}")
        return faiss.IndexFlatL2(384), []


# Quick test
if __name__ == "__main__":
    # Test loading
    index, metadata = load_index()
    print(f"Index contains {index.ntotal} vectors")
    print(f"Metadata contains {len(metadata)} chunks")
    
    if metadata:
        print(f"\nSample chunk:")
        print(f"  Source: {metadata[0]['source']}")
        print(f"  Chunk ID: {metadata[0]['chunk_id']}")
        print(f"  Text preview: {metadata[0]['text'][:100]}...")