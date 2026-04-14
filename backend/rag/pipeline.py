# import httpx
# from config import OLLAMA_MODEL, OLLAMA_URL
# from vectordb.retriever import retrieve
# from rag.prompt_template import build_prompt


# def generate_answer(query: str) -> dict:
#     """
#     Full RAG pipeline:
#     1. Retrieve top-K relevant chunks
#     2. Build prompt
#     3. Send to LLM
#     4. Return answer + sources
#     """
#     # Step 1 — Retrieve
#     chunks = retrieve(query)

#     # Step 2 — Build prompt
#     prompt = build_prompt(query, chunks)

#     # Step 3 — Call Ollama
#     try:
#         response = httpx.post(
#             OLLAMA_URL,
#             json={
#                 "model": OLLAMA_MODEL,
#                 "prompt": prompt,
#                 "stream": False
#             },
#             timeout=120.0
#         )
#         response.raise_for_status()
#         answer = response.json().get("response", "").strip()

#     except httpx.ConnectError:
#         answer = "[ERROR] Cannot connect to Ollama. Make sure 'ollama run llama3' is running."
#     except Exception as e:
#         answer = f"[ERROR] {str(e)}"

#     # Step 4 — Return result
#     return {
#         "query":   query,
#         "answer":  answer,
#         "sources": [
#             {"source": c["source"], "chunk_id": c["chunk_id"], "score": c["score"]}
#             for c in chunks
#         ]
#     }


# # Quick test
# if __name__ == "__main__":
#     also_create_init = True   # reminder to create rag/__init__.py

#     test_queries = [
#         "What is the waiting period for pre-existing diseases?",
#         "What expenses are covered during hospitalization?",
#         "Is maternity benefit covered under the policy?"
#     ]

#     for query in test_queries:
#         print(f"\n{'='*60}")
#         print(f"Q: {query}")
#         print(f"{'='*60}")

#         result = generate_answer(query)

#         print(f"\nANSWER:\n{result['answer']}")
#         print(f"\nSOURCES:")
#         for s in result["sources"]:
#             print(f"  - {s['source']} (chunk {s['chunk_id']}, score {s['score']:.4f})")



import httpx
from config import OLLAMA_MODEL, OLLAMA_URL
from vectordb.retriever import retrieve
from rag.prompt_template import build_prompt
from rag.cache import get_cached, set_cache


def generate_answer(query: str) -> dict:
    # Check cache first
    cached = get_cached(query)
    if cached:
        print(f"[CACHE HIT] {query[:50]}")
        return cached

    # Step 1 — Retrieve
    chunks = retrieve(query)

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