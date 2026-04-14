from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
from tqdm import tqdm


# Load model once at module level (avoids reloading on every call)
print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)
print("[OK] Model loaded.")


def generate_embeddings(chunks: list[dict]) -> list[dict]:
    """
    Takes list of { "source", "chunk_id", "text" }
    Adds "embedding" key to each chunk and returns them.
    """
    print(f"\n[INFO] Generating embeddings for {len(chunks)} chunks...")

    texts = [chunk["text"] for chunk in chunks]

    # batch_size=64 is efficient for CPU; tqdm shows progress bar
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i]

    print(f"[DONE] Embeddings generated. Shape per vector: {embeddings[0].shape}")
    return chunks


# Quick test
if __name__ == "__main__":
    from ingest.pdf_loader import load_pdfs_from_folder
    from ingest.chunker import chunk_documents

    docs = load_pdfs_from_folder()
    chunks = chunk_documents(docs)
    chunks_with_embeddings = generate_embeddings(chunks)

    # Preview
    print("\n--- Preview: first chunk embedding ---")
    print(f"Source     : {chunks_with_embeddings[0]['source']}")
    print(f"Chunk ID   : {chunks_with_embeddings[0]['chunk_id']}")
    print(f"Text       : {chunks_with_embeddings[0]['text'][:100]}...")
    print(f"Embedding  : {chunks_with_embeddings[0]['embedding'][:5]}...")
    print(f"Vector size: {len(chunks_with_embeddings[0]['embedding'])}")