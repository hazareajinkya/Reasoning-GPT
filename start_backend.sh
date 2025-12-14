#!/bin/bash

# Start the FastAPI backend server

cd "$(dirname "$0")"

export PYTHONPATH="${PWD}:${PYTHONPATH}"
export EMBED_API_URL="${EMBED_API_URL:-https://api.openai.com/v1/embeddings}"
export EMBED_API_KEY="${EMBED_API_KEY:-}"
export LLM_API_URL="${LLM_API_URL:-https://api.openai.com/v1/chat/completions}"
export LLM_API_KEY="${LLM_API_KEY:-}"

echo "🚀 Starting DILR Reasoning Explainer Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Server will run at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
