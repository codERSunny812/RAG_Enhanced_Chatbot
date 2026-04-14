import numpy as np
from vectordb.store import load_index
from ingest.embedder import model
from config import TOP_K


# Load index and metadata once at module level
index, metadata = load_index()


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Takes a user query string.
    Returns top_k most relevant chunks as list of dicts.
    """
    # Embed the query using the same model
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")

    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        chunk = metadata[idx]
        results.append({
            "rank":     rank + 1,
            "score":    float(dist),
            "source":   chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text":     chunk["text"]
        })

    return results


# Quick test
if __name__ == "__main__":
    test_queries = [
        "What is the waiting period for pre-existing diseases?",
        "What is covered under hospitalization?",
        "क्या मातृत्व लाभ कवर किया जाता है?"   # Hindi query
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        results = retrieve(query)

        for r in results:
            print(f"\nRank {r['rank']} | Score: {r['score']:.4f} | Source: {r['source']}")
            print(f"Text: {r['text'][:200]}...")