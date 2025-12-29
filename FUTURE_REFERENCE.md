# Future Reference & Deployment Details

## Accounts

### Railway (Backend Hosting)
- **Account Email:** ajinkya642000@gmail.com
- **Project:** Reasoning GPT (Backend)

### Vercel (Frontend Hosting)
- **Account Handle/Email:** ajaxx642000
- **Project:** Reasoning GPT (Frontend)

## Deployment Notes

- **Backend:** Deployed via Railway. Uses `start_backend.sh` as the entry point. Requires `LLM_API_KEY` and `EMBED_API_KEY` environment variables.
- **Frontend:** Deployed via Vercel. Next.js app. Connects to backend via `NEXT_PUBLIC_API_URL`.

## Key Commands

- Start Backend: `./start_backend.sh`
- Start Frontend: `./start_frontend.sh`
- Build Vector Store: `python scripts/build_vector_store.py`

