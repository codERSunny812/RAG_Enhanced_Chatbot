import hashlib
import json
import os

CACHE_PATH = os.path.join(os.path.dirname(__file__), "response_cache.json")

def _load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(cache: dict):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_cached(query: str):
    cache = _load_cache()
    key = hashlib.md5(query.lower().strip().encode()).hexdigest()
    return cache.get(key)

def set_cache(query: str, result: dict):
    cache = _load_cache()
    key = hashlib.md5(query.lower().strip().encode()).hexdigest()
    cache[key] = result
    _save_cache(cache)