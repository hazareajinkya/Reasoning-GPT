"""
Test script for the RAG pipeline.
Tests embedding, retrieval, and LLM inference.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from retrieval.embed import embed
from retrieval.store import VectorStore, load_jsonl


def test_embeddings():
    """Test embedding generation."""
    print("Testing embeddings...")
    
    if not os.environ.get("EMBED_API_KEY"):
        print("⚠️  EMBED_API_KEY not set. Skipping embedding test.")
        return False
    
    os.environ.setdefault("EMBED_API_URL", "https://api.openai.com/v1/embeddings")
    os.environ.setdefault("EMBED_MODEL", "text-embedding-3-small")  # Cheaper for testing
    
    try:
        test_texts = ["Two runners on a circular track", "Speed ratio problems"]
        embeddings = embed(test_texts)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Dimension: {len(embeddings[0])}")
        return True
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


def test_retrieval():
    """Test vector store retrieval."""
    print("\nTesting retrieval...")
    
    data_path = Path("data/seed_circular_tracks.jsonl")
    if not data_path.exists():
        print(f"⚠️  {data_path} not found. Skipping retrieval test.")
        return False
    
    items = load_jsonl(data_path)
    if not items:
        print("⚠️  No items in dataset. Skipping retrieval test.")
        return False
    
    print(f"✅ Loaded {len(items)} problems from dataset")
    
    # Test query
    query = "Two runners start from same point, same direction, when do they meet?"
    print(f"   Query: {query}")
    
    if not os.environ.get("EMBED_API_KEY"):
        print("⚠️  EMBED_API_KEY not set. Skipping retrieval test.")
        return False
    
    try:
        os.environ.setdefault("EMBED_API_URL", "https://api.openai.com/v1/embeddings")
        os.environ.setdefault("EMBED_MODEL", "text-embedding-3-small")
        
        # Build store
        texts = []
        for it in items[:5]:  # Just test with first 5
            question = it.get("question", "")
            solutions = it.get("solutions", {})
            text = f"{question}\n\nDirect: {solutions.get('direct', '')}"
            texts.append(text)
        
        embeddings = embed(texts)
        dim = len(embeddings[0])
        store = VectorStore(dim)
        store.add(embeddings, items[:5])
        
        # Search
        q_embed = embed([query])[0]
        results = store.search(q_embed, top_k=2)
        
        print(f"✅ Retrieved {len(results)} results:")
        for score, item in results:
            print(f"   - {item.get('id')}: {item.get('question', '')[:60]}... (score: {score:.3f})")
        
        return True
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("RAG PIPELINE TEST")
    print("=" * 60)
    
    embed_ok = test_embeddings()
    retrieval_ok = test_retrieval()
    
    print("\n" + "=" * 60)
    if embed_ok and retrieval_ok:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Check your API keys and data files.")
    print("=" * 60)


if __name__ == "__main__":
    main()

