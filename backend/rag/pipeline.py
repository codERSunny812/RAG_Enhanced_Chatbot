import httpx
from config import OLLAMA_MODEL, OLLAMA_URL
from vectordb.retriever import retrieve
from rag.prompt_template import build_prompt
from rag.cache import get_cached, set_cache
from rag.query_processor import rewrite_query


def generate_answer(query: str) -> dict:
    # Check cache first
    cached = get_cached(query)
    if cached:
        print(f"[CACHE HIT] {query[:50]}")
        return cached
    
    # new step
    redefined_query = rewrite_query(query)

    # Step 1 — Retrieve
    chunks = retrieve(redefined_query)

    if not chunks:
        return {
        "query": query,
        "answer": "I could not find any relevant information in the policy documents.",
        "sources": []
    }

    # Step 2 — Build prompt
    prompt = build_prompt(query, chunks)

    # Step 3 — Call Ollama
    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,   # lower = more factual, less creative
                    "top_p": 0.9,
                    "num_predict": 512    # max tokens in response
                }
            },
            timeout=120.0
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()

    except httpx.ConnectError:
        answer = "[ERROR] Cannot connect to Ollama. Make sure 'ollama run llama3.2' is running."
    except Exception as e:
        answer = f"[ERROR] {str(e)}"

    result = {
        "query":   query,
        "answer":  answer,
        "sources": [
            {"source": c["source"], "chunk_id": c["chunk_id"], "score": c["score"]}
            for c in chunks
        ]
    }

    # Save to cache
    set_cache(query, result)
    return result