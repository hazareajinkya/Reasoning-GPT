"""
Build and save the vector store from seed data.
This creates embeddings for all problems and stores them for fast retrieval.
"""

import json
import os
import pickle
from pathlib import Path

from retrieval.embed import embed
from retrieval.store import VectorStore, load_jsonl


def build_store(data_path: Path, output_path: Path):
    """Build vector store from JSONL data and save it."""
    print(f"Loading data from {data_path}...")
    items = load_jsonl(data_path)
    
    if not items:
        raise ValueError(f"No data found in {data_path}")
    
    print(f"Found {len(items)} problems")
    
    # Create embedding text: question + all solution styles
    texts = []
    for item in items:
        question = item.get("question", "")
        solutions = item.get("solutions", {})
        # Combine question with all solution styles for better retrieval
        text = f"{question}\n\n"
        text += f"Direct: {solutions.get('direct', '')}\n"
        text += f"Step-by-step: {solutions.get('step_by_step', '')}\n"
        text += f"Intuitive: {solutions.get('intuitive', '')}\n"
        text += f"Shortcut: {solutions.get('shortcut', '')}"
        texts.append(text)
    
    print("Generating embeddings...")
    embeddings = embed(texts)
    
    if not embeddings:
        raise ValueError("Failed to generate embeddings")
    
    dim = len(embeddings[0])
    print(f"Embedding dimension: {dim}")
    
    # Build vector store
    store = VectorStore(dim)
    store.add(embeddings, items)
    
    # Save store
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump({"store": store, "items": items, "dim": dim}, f)
    
    print(f"✅ Vector store saved to {output_path}")
    print(f"   - {len(items)} problems indexed")
    print(f"   - Dimension: {dim}")
    
    return store, items


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Build vector store from seed data")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/seed_circular_tracks.jsonl"),
        help="Path to seed JSONL file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/vector_store.pkl"),
        help="Path to save vector store",
    )
    args = parser.parse_args()
    
    # Check env vars
    if not os.environ.get("EMBED_API_URL"):
        print("⚠️  EMBED_API_URL not set. Using OpenAI default...")
        os.environ.setdefault("EMBED_API_URL", "https://api.openai.com/v1/embeddings")
    
    if not os.environ.get("EMBED_API_KEY"):
        raise RuntimeError("Set EMBED_API_KEY environment variable")
    
    build_store(args.data, args.output)


if __name__ == "__main__":
    main()

