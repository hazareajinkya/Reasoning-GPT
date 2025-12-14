"""
Test the DILR RAG pipeline with a sample question.
"""

import os
import json
from pathlib import Path

from retrieval.embed import embed
from retrieval.store import VectorStore, load_jsonl
from retrieval.prompt import build_user_prompt, SYSTEM_PROMPT
from backend.app import call_llm


def test_dilr_rag():
    """Test the DILR RAG pipeline."""
    print("=" * 80)
    print("🧪 TESTING DILR RAG PIPELINE")
    print("=" * 80)
    
    # Load vector store
    store_path = Path("data/vector_store_dilr.pkl")
    data_path = Path("data/seed_dilr.jsonl")
    
    if store_path.exists():
        print(f"\n📦 Loading vector store from {store_path}...")
        import pickle
        with open(store_path, "rb") as f:
            data = pickle.load(f)
            store = data["store"]
            items = data["items"]
        print(f"✅ Loaded {len(items)} problems from vector store")
    elif data_path.exists():
        print(f"\n📦 Building vector store from {data_path}...")
        items = load_jsonl(data_path)
        if not items:
            print("❌ No items found in data file")
            return
        
        print(f"Embedding {len(items)} problems...")
        texts = []
        for it in items:
            question = it.get("question", "")
            solutions = it.get("solutions", {})
            text = f"{question}\n\n"
            text += f"Direct: {solutions.get('direct', '')}\n"
            text += f"Step-by-step: {solutions.get('step_by_step', '')}\n"
            text += f"Intuitive: {solutions.get('intuitive', '')}\n"
            text += f"Shortcut: {solutions.get('shortcut', '')}"
            texts.append(text)
        
        embeddings = embed(texts)
        dim = len(embeddings[0])
        store = VectorStore(dim)
        store.add(embeddings, items)
        print(f"✅ Built vector store with {len(items)} problems")
    else:
        print(f"❌ Neither {store_path} nor {data_path} found")
        return
    
    # Test question
    test_question = """Six friends A, B, C, D, E, and F are sitting around a circular table. 
    A sits opposite to D. B sits to the immediate right of A. C sits between B and E. 
    Who sits opposite to F?"""
    
    print(f"\n❓ Test Question:")
    print(f"   {test_question}")
    
    # Embed query
    print("\n🔍 Embedding query...")
    q_embed = embed([test_question])[0]
    
    # Retrieve similar problems
    print("🔎 Retrieving similar problems...")
    results = store.search(q_embed, top_k=4)
    contexts = [r[1] for r in results]
    retrieved_ids = [c.get("id", "unknown") for c in contexts]
    
    print(f"\n📚 Retrieved {len(contexts)} similar problems:")
    for i, ctx in enumerate(contexts, 1):
        q = ctx.get("question", "")[:80] + "..." if len(ctx.get("question", "")) > 80 else ctx.get("question", "")
        print(f"   {i}. [{ctx.get('id', 'unknown')}] {q}")
    
    # Build prompt
    print("\n📝 Building prompt...")
    prompt = build_user_prompt(test_question, contexts)
    
    # Call LLM
    print("🤖 Calling LLM for explanation...")
    try:
        llm_res = call_llm(prompt)
        
        print("\n" + "=" * 80)
        print("✅ RAG PIPELINE TEST RESULTS")
        print("=" * 80)
        print(f"\n📋 Direct Answer:")
        print(f"   {llm_res.get('direct', 'N/A')}")
        print(f"\n📝 Step-by-Step:")
        print(f"   {llm_res.get('step_by_step', 'N/A')[:200]}...")
        print(f"\n💡 Intuitive:")
        print(f"   {llm_res.get('intuitive', 'N/A')[:200]}...")
        print(f"\n⚡ Shortcut:")
        print(f"   {llm_res.get('shortcut', 'N/A')[:200]}...")
        print(f"\n🔗 Retrieved IDs: {retrieved_ids}")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error calling LLM: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set up environment
    if not os.environ.get("EMBED_API_URL"):
        os.environ["EMBED_API_URL"] = "https://api.openai.com/v1/embeddings"
    if not os.environ.get("EMBED_API_KEY"):
        print("⚠️  Set EMBED_API_KEY environment variable")
    
    if not os.environ.get("LLM_API_URL"):
        os.environ["LLM_API_URL"] = "https://api.openai.com/v1/chat/completions"
    if not os.environ.get("LLM_API_KEY"):
        print("⚠️  Set LLM_API_KEY environment variable")
    
    test_dilr_rag()

