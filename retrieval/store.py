import json
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np


class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatIP(dim)
        self.payloads: list[dict] = []

    def add(self, embeddings: List[List[float]], payloads: List[dict]):
        arr = np.array(embeddings).astype("float32")
        self.index.add(arr)
        self.payloads.extend(payloads)

    def search(self, query: List[float], top_k: int = 5) -> List[Tuple[float, dict]]:
        q = np.array([query]).astype("float32")
        scores, idxs = self.index.search(q, top_k)
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue
            results.append((float(score), self.payloads[idx]))
        return results


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f]

