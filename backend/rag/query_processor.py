import httpx
from config import OLLAMA_URL, OLLAMA_MODEL

def rewrite_query(query: str) -> str:
    prompt = f"""
Rewrite this user query into a clear, formal insurance question.
Keep it precise and include relevant insurance terminology.

Query: {query}
Rewritten:
"""

    response = httpx.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=30.0
    )

    return response.json().get("response", query).strip()