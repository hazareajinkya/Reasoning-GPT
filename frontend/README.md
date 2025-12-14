# DILR Reasoning Explainer - Frontend

Next.js frontend for the DILR Reasoning Explainer AI.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Backend

Make sure the FastAPI backend is running on `http://localhost:8000`:

```bash
cd ../backend
uvicorn app:app --reload
```

## Features

- ✅ Question input with textarea
- ✅ 4-way explanation display (Direct, Step-by-Step, Intuitive, Shortcut)
- ✅ Tabbed interface for switching between explanation styles
- ✅ History panel with last 50 questions
- ✅ Mobile-responsive design
- ✅ Loading states and error handling

