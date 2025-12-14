import os
import pickle
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from retrieval.embed import embed
from retrieval.prompt import SYSTEM_PROMPT, build_user_prompt
from retrieval.store import VectorStore, load_jsonl
from retrieval.table_generator import generate_table_for_problem

# Use absolute paths relative to project root (parent of backend/)
PROJECT_ROOT = Path(__file__).parent.parent
STORE_PATH = PROJECT_ROOT / "data" / "vector_store_dilr.pkl"
DATA_PATH = PROJECT_ROOT / "data" / "seed_dilr.jsonl"
MODEL_URL = os.environ.get("LLM_API_URL")
MODEL_KEY = os.environ.get("LLM_API_KEY")

# Debug: Log the raw environment variable (mask the key part)
if MODEL_URL:
    print(f"DEBUG: Raw LLM_API_URL from env: '{MODEL_URL}' (length: {len(MODEL_URL)})")
    # Show first and last 20 chars to see if there are hidden characters
    if len(MODEL_URL) > 40:
        print(f"DEBUG: First 20 chars: '{MODEL_URL[:20]}' | Last 20 chars: '{MODEL_URL[-20:]}'")

# Ensure MODEL_URL has protocol (but don't modify the original, we'll clean it in call_llm)
# Actually, let's clean it here too to be safe
if MODEL_URL:
    MODEL_URL = MODEL_URL.strip()
    # Remove any leading = or spaces
    while MODEL_URL.startswith(("=", " ")):
        MODEL_URL = MODEL_URL[1:].strip()

app = FastAPI(title="DILR Reasoning Explainer")

# Add CORS middleware
# When allow_credentials=True, cannot use allow_origins=["*"]
# Must specify exact origins
cors_origins = os.environ.get("CORS_ORIGINS", "https://reasoning-gpt.vercel.app,http://localhost:3000,http://localhost:3001")
if cors_origins == "*":
    # If wildcard is explicitly set, disable credentials (CORS spec requirement)
    allow_origins = ["*"]
    allow_creds = False
else:
    allow_origins = [origin.strip() for origin in cors_origins.split(",")]
    allow_creds = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add exception handler to ensure CORS headers are included in error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are included even in error responses."""
    origin = request.headers.get("origin")
    if origin and origin in allow_origins:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true" if allow_creds else "false",
        }
    elif allow_origins == ["*"]:
        headers = {
            "Access-Control-Allow-Origin": "*",
        }
    else:
        headers = {}
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers=headers
        )


class SolveRequest(BaseModel):
    question: str
    top_k: int = 4
    use_vision: bool = False  # Optional: use images from frames if available (costs more)


class SolveResponse(BaseModel):
    direct: str
    step_by_step: str
    intuitive: str
    shortcut: str
    retrieved_ids: List[str]


def load_store() -> tuple[VectorStore, List[dict]]:
    """Load vector store from pickle file, or build from JSONL if not exists."""
    if STORE_PATH.exists():
        print(f"Loading vector store from {STORE_PATH}...")
        try:
            with open(STORE_PATH, "rb") as f:
                data = pickle.load(f)
                store = data.get("store")
                items = data.get("items", [])
                
                # Check if store is actually populated
                try:
                    ntotal = store.index.ntotal if hasattr(store, 'index') and hasattr(store.index, 'ntotal') else 0
                    if ntotal > 0 and len(items) > 0:
                        print(f"Successfully loaded vector store with {ntotal} items")
                        return store, items
                    else:
                        print(f"Warning: Vector store file exists but is empty (ntotal={ntotal}, items={len(items)}). Rebuilding from JSONL...")
                except Exception as e:
                    print(f"Warning: FAISS version mismatch or invalid store structure: {e}. Rebuilding from JSONL...")
        except Exception as e:
            print(f"Error loading vector store: {e}. Rebuilding from JSONL...")
    
    # Fallback: build from JSONL (slower, but works)
    print(f"Building vector store from {DATA_PATH}...")
    items = load_jsonl(DATA_PATH) if DATA_PATH.exists() else []
    if not items:
        print(f"Warning: No JSONL data found at {DATA_PATH}")
        return VectorStore(dim=1), []
    
    print(f"Found {len(items)} items in JSONL. Building embeddings...")
    from retrieval.embed import embed
    
    # Check if embedding API is configured
    embed_key = os.environ.get("EMBED_API_KEY")
    if not embed_key:
        print("ERROR: EMBED_API_KEY not set. Cannot rebuild vector store.")
        return VectorStore(dim=1), []
    
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
    
    print("Generating embeddings...")
    try:
        embeddings = embed(texts)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise
    dim = len(embeddings[0])
    store = VectorStore(dim)
    store.add(embeddings, items)
    print(f"Successfully built vector store with {store.index.ntotal} items")
    return store, items


STORE, ITEMS = load_store()


def call_llm(prompt: str) -> Dict[str, Any]:
    """Call LLM API (Groq/DeepSeek/GPT-4o-mini compatible)."""
    if not MODEL_URL or not MODEL_KEY:
        raise HTTPException(500, "Set LLM_API_URL and LLM_API_KEY environment variables.")
    
    # Clean and validate URL (handle common formatting issues)
    api_url = MODEL_URL.strip() if MODEL_URL else ""
    
    # Debug: Log before cleaning
    print(f"DEBUG call_llm: Raw MODEL_URL: '{MODEL_URL}' -> api_url before clean: '{api_url}'")
    
    # Remove any leading/trailing whitespace, equals signs, quotes, or other formatting issues
    api_url = api_url.strip()
    # Remove leading =, spaces, quotes, and any other weird characters
    while api_url and api_url[0] in ("=", " ", "'", '"', "\t", "\n", "\r"):
        api_url = api_url[1:].strip()
    # Remove trailing =, spaces, quotes
    while api_url and api_url[-1] in ("=", " ", "'", '"', "\t", "\n", "\r"):
        api_url = api_url[:-1].strip()
    
    # Debug: Log after cleaning
    print(f"DEBUG call_llm: After cleaning: '{api_url}'")
    
    # Only add https:// if it doesn't already have a protocol
    if api_url and not api_url.startswith("http://") and not api_url.startswith("https://"):
        api_url = f"https://{api_url}"
        print(f"DEBUG call_llm: Added https:// -> '{api_url}'")
    
    # Final validation
    if not api_url or (not api_url.startswith("http://") and not api_url.startswith("https://")):
        raise HTTPException(500, f"Invalid LLM_API_URL format: '{MODEL_URL}' (cleaned: '{api_url}'). Must be a valid URL starting with http:// or https://")
    
    # Log the final URL for debugging
    print(f"DEBUG call_llm: Final API URL: '{api_url}'")
    
    headers = {"Authorization": f"Bearer {MODEL_KEY}"}
    
    # Detect provider from URL or use default
    model_name = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 16000,  # Significantly increased to prevent truncation (GPT-4o-mini supports up to 16k)
        # Note: For more detailed educational solutions with 4-5 tables, this should be sufficient
        # If truncation occurs, consider using a model with higher token limits
    }
    
    # Add JSON mode for OpenAI-compatible APIs
    if "openai" in api_url.lower() or "api.openai.com" in api_url:
        payload["response_format"] = {"type": "json_object"}
    
    try:
        resp = httpx.post(api_url, headers=headers, json=payload, timeout=180)  # Increased timeout for longer responses
        resp.raise_for_status()
        data = resp.json()
    except httpx.ConnectError as e:
        raise HTTPException(500, f"Failed to connect to LLM API at {api_url}. Check LLM_API_URL is correct. Error: {str(e)}")
    except httpx.HTTPStatusError as e:
        error_msg = f"LLM API error: {e.response.status_code}"
        try:
            error_detail = e.response.json().get("error", {}).get("message", e.response.text[:200])
            error_msg += f" - {error_detail}"
        except:
            error_msg += f" - {e.response.text[:200]}"
        raise HTTPException(e.response.status_code, error_msg)
        
        # Extract content from response
        if "choices" in data:
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "")
            
            # Check if response was truncated
            if finish_reason == "length":
                print(f"WARNING: LLM response was truncated (finish_reason=length). Content length: {len(content)}")
                print(f"Consider: 1) Using a model with higher token limit, 2) Making prompt more concise, 3) Splitting response")
                # Try to extract what we have, but warn
                content += "\n\n[NOTE: Response was truncated. The solution may be incomplete. Consider rephrasing the question or using a model with higher token limits.]"
            
            # Try to parse as JSON
            import json
            try:
                llm_res = json.loads(content)
                # Ensure all fields are strings (convert dicts/lists to strings)
                result = {}
                for key in ["direct", "step_by_step", "intuitive", "shortcut"]:
                    value = llm_res.get(key, "")
                    if isinstance(value, dict):
                        # Convert dict to formatted string
                        result[key] = "\n".join([f"{k}: {v}" for k, v in value.items()])
                    elif isinstance(value, list):
                        # Convert list to string
                        result[key] = "\n".join(str(item) for item in value)
                    else:
                        result[key] = str(value) if value else ""
                
                # Log response lengths for debugging
                print(f"Response lengths - direct: {len(result.get('direct', ''))}, step_by_step: {len(result.get('step_by_step', ''))}, intuitive: {len(result.get('intuitive', ''))}, shortcut: {len(result.get('shortcut', ''))}")
                
                return result
            except json.JSONDecodeError as e:
                print(f"WARNING: Failed to parse JSON response: {e}")
                print(f"Response preview (first 500 chars): {content[:500]}")
                # If not JSON, return as dict with content in all fields
                return {"direct": content, "step_by_step": content, "intuitive": content, "shortcut": content}
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, f"LLM API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(500, f"LLM call failed: {str(e)}")


@app.get("/")
def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Reasoning GPT API",
        "docs": "/docs",
        "health": "/health",
        "solve": "/solve"
    }


@app.get("/health")
def health():
    # Check if API keys are set
    embed_key_set = bool(os.environ.get("EMBED_API_KEY"))
    llm_key_set = bool(os.environ.get("LLM_API_KEY"))
    
    try:
        items_count = len(ITEMS) if ITEMS else 0
        store_loaded = STORE.index.ntotal > 0 if hasattr(STORE, 'index') and hasattr(STORE.index, 'ntotal') else False
        store_exists = STORE_PATH.exists() if STORE_PATH else False
    except Exception as e:
        # If there's an error accessing store, return safe defaults
        items_count = 0
        store_loaded = False
        store_exists = False
    
    return {
        "status": "ok", 
        "items": items_count,
        "store_loaded": store_loaded,
        "vector_store_path": str(STORE_PATH) if STORE_PATH else "unknown",
        "vector_store_exists": store_exists,
        "api_keys_configured": embed_key_set and llm_key_set,
        "embed_api_key_set": embed_key_set,
        "llm_api_key_set": llm_key_set,
    }


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    """Solve a reasoning problem using RAG."""
    # Check if vector store is loaded
    try:
        store_ntotal = STORE.index.ntotal if hasattr(STORE, 'index') and hasattr(STORE.index, 'ntotal') else 0
    except Exception:
        store_ntotal = 0
    
    if not ITEMS or len(ITEMS) == 0:
        raise HTTPException(
            400, 
            f"Dataset empty. Vector store file exists: {STORE_PATH.exists() if STORE_PATH else False}. "
            f"Path: {STORE_PATH}. Please ensure vector store is built and committed to Git."
        )
    
    if store_ntotal == 0:
        raise HTTPException(
            400, 
            f"Vector store is empty (ntotal={store_ntotal}). "
            f"Store file exists: {STORE_PATH.exists() if STORE_PATH else False}. "
            f"Please rebuild the vector store."
        )

    # Embed query
    try:
        q_embed = embed([req.question])[0]
    except RuntimeError as e:
        # Embedding API key issue
        raise HTTPException(500, f"Embedding API error: {str(e)}. Make sure EMBED_API_URL and EMBED_API_KEY are set.")
    except Exception as e:
        raise HTTPException(500, f"Embedding failed: {str(e)}")
    
    # Retrieve similar problems
    results = STORE.search(q_embed, top_k=req.top_k)
    if not results:
        raise HTTPException(404, "No similar problems found.")
    
    contexts = [r[1] for r in results]
    
    # Optionally use vision enhancement (if requested and frames available)
    if req.use_vision:
        try:
            from retrieval.vision_enhance import call_llm_with_vision
            frames_base_dir = PROJECT_ROOT / "data" / "raw" / "frames"
            if frames_base_dir.exists():
                llm_res = call_llm_with_vision(
                    req.question,
                    contexts,
                    frames_base_dir,
                    MODEL_URL,
                    MODEL_KEY,
                    SYSTEM_PROMPT,
                    max_frames=2  # Limit to 2 frames to control costs
                )
            else:
                # Fallback to text-only if frames directory doesn't exist
                print("Warning: Vision requested but frames directory not found. Using text-only.")
                prompt = build_user_prompt(req.question, contexts)
                llm_res = call_llm(prompt)
        except Exception as e:
            print(f"Warning: Vision enhancement failed: {e}. Falling back to text-only.")
            prompt = build_user_prompt(req.question, contexts)
            llm_res = call_llm(prompt)
    else:
        # Standard text-only approach
        prompt = build_user_prompt(req.question, contexts)
        try:
            llm_res = call_llm(prompt)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"LLM call failed: {str(e)}")
    
    # Ensure all response fields are strings (handle dicts/lists from LLM)
    def ensure_string(value, default=""):
        if isinstance(value, dict):
            # Convert dict to formatted string
            return "\n".join([f"{k}: {v}" for k, v in value.items()])
        elif isinstance(value, list):
            # Convert list to string
            return "\n".join(str(item) for item in value)
        else:
            return str(value) if value else default
    
    direct = ensure_string(llm_res.get("direct", ""))
    step_by_step_raw = ensure_string(llm_res.get("step_by_step", ""))
    intuitive = ensure_string(llm_res.get("intuitive", ""))
    shortcut = ensure_string(llm_res.get("shortcut", ""))
    
    # Clean up step_by_step if it contains Python dict/array formats
    import re
    # Remove patterns like "tables: [{'table': '...'}]" and extract the actual table content
    if "tables:" in step_by_step_raw or "table:" in step_by_step_raw.lower():
        # Try to extract table content from dict/array formats
        # Pattern 1: table: [{'table': 'line1\nline2\n...'}]
        dict_pattern = r"table[s]?:\s*\[\s*\{[^}]*['\"]table['\"]:\s*['\"]([^'\"]*)['\"][^}]*\}\s*\]"
        matches = re.findall(dict_pattern, step_by_step_raw, re.DOTALL | re.IGNORECASE)
        if matches:
            # Replace with the actual table content
            for match in matches:
                table_content = match.replace('\\n', '\n')
                step_by_step_raw = re.sub(dict_pattern, f"\n{table_content}\n", step_by_step_raw, count=1, flags=re.DOTALL | re.IGNORECASE)
        
        # Pattern 2: tables: ['line1', 'line2', ...] - extract and join
        array_pattern = r"table[s]?:\s*\[([^\]]+)\]"
        array_matches = re.findall(array_pattern, step_by_step_raw, re.DOTALL | re.IGNORECASE)
        if array_matches:
            for array_match in array_matches:
                # Extract quoted strings
                quoted_strings = re.findall(r"['\"]([^'\"]*)['\"]", array_match)
                if quoted_strings:
                    table_content = '\n'.join(quoted_strings)
                    step_by_step_raw = re.sub(array_pattern, f"\n{table_content}\n", step_by_step_raw, count=1, flags=re.DOTALL | re.IGNORECASE)
        
        # Pattern 3: Remove any remaining "tables:" or "table:" labels if they're not followed by proper format
        step_by_step_raw = re.sub(r"table[s]?:\s*\[[^\]]*\]", "", step_by_step_raw, flags=re.DOTALL | re.IGNORECASE)
    
    # Post-process step_by_step to add tables if missing
    step_by_step = generate_table_for_problem(req.question, step_by_step_raw)
    
    return {
        "direct": direct,
        "step_by_step": step_by_step,
        "intuitive": intuitive,
        "shortcut": shortcut,
        "retrieved_ids": [c.get("id", "unknown") for c in contexts],
    }

