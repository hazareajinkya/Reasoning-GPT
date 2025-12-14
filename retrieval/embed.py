import os
from typing import List

import httpx


EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-large")
EMBED_API_URL = os.environ.get("EMBED_API_URL")  # e.g., OpenAI compat endpoint
EMBED_API_KEY = os.environ.get("EMBED_API_KEY")


def embed(texts: List[str]) -> List[List[float]]:
    """Embed texts using OpenAI-compatible API."""
    if not EMBED_API_URL or not EMBED_API_KEY:
        raise RuntimeError("Set EMBED_API_URL and EMBED_API_KEY for embeddings.")
    
    # OpenAI embeddings endpoint format
    resp = httpx.post(
        EMBED_API_URL,
        headers={"Authorization": f"Bearer {EMBED_API_KEY}"},
        json={"model": EMBED_MODEL, "input": texts},
        timeout=60,
    )
    
    if resp.status_code == 401:
        raise RuntimeError(f"Embedding API authentication failed (401). Check EMBED_API_KEY. URL: {EMBED_API_URL}")
    
    resp.raise_for_status()
    data = resp.json()
    
    # Handle OpenAI response format: {"data": [{"embedding": [...]}, ...]}
    if "data" in data:
        return [item["embedding"] for item in data["data"]]
    # Handle alternative format: {"embeddings": [[...], ...]}
    elif "embeddings" in data:
        return data["embeddings"]
    else:
        raise ValueError(f"Unexpected API response format: {list(data.keys())}")

