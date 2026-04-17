
import numpy as np
from vectordb.store import load_index
from ingest.embedder import model
from config import TOP_K


# Load index and metadata once at module level
index, metadata = load_index()


def rerank(query: str, results: list[dict]) -> list[dict]:
    """
    Rerank results using query-chunk similarity.
    Since metadata doesn't have embeddings, we re-encode chunks.
    """
    # Encode query once
    query_vec = model.encode([query], convert_to_numpy=True)[0]
    
    for r in results:
        # Encode each chunk text
        chunk_vec = model.encode([r["text"]], convert_to_numpy=True)[0]
        # Calculate cosine similarity
        similarity = float(np.dot(query_vec, chunk_vec) / 
                          (np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec)))
        r["rerank_score"] = similarity
    
    # Sort by rerank score (higher is better)
    return sorted(results, key=lambda x: x["rerank_score"], reverse=True)


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Takes a user query string.
    Returns top_k most relevant chunks as list of dicts.
    """

    # Step 1 — Embed query
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")

    # Step 2 — FAISS search
    distances, indices = index.search(query_embedding, top_k)

    # Step 3 — Collect results
    results = []
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx == -1 or idx >= len(metadata):  # Skip invalid indices
            continue
        chunk = metadata[idx]
        results.append({
            "rank":     rank + 1,
            "score":    float(dist),
            "source":   chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text":     chunk["text"]
        })

    # Step 4 — Rerank results (if we have results)
    if results:
        results = rerank(query, results)
        
        # Step 5 — Keep top_k after rerank
        results = results[:top_k]
        
        # Step 6 — Fix ranks after rerank
        for i, r in enumerate(results):
            r["rank"] = i + 1

    return results


# Quick test
if __name__ == "__main__":
    test_queries = [
        "What is the waiting period for pre-existing diseases?",
        "What is covered under hospitalization?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        results = retrieve(query)

        for r in results:
            print(f"\nRank {r['rank']} | Score: {r['score']:.4f} | Source: {r['source']}")
            print(f"Text: {r['text'][:200]}...")