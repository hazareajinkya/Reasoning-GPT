"""
Formats raw vision drafts + human notes into the canonical schema.
Uses an LLM (e.g., GPT-4o mini / DeepSeek) to produce four solution styles.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import httpx

SYSTEM_PROMPT = (
    "You are a CAT reasoning explainer. Given a question and rough notes, "
    "produce four outputs: direct answer; step-by-step; simplest intuitive approach; "
    "shortcut/exam hack. Keep numbers consistent; do not invent data."
)


def call_llm(question: str, notes: str, api_url: str, api_key: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": f"Question:\n{question}\n\nNotes:\n{notes}\n\nReturn JSON with keys direct, step_by_step, intuitive, shortcut."}
        ],
        "response_format": {"type": "json_object"},
    }
    resp = httpx.post(api_url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Format drafts into schema.")
    parser.add_argument("--drafts", type=Path, required=True, help="JSONL drafts with cleaned question/notes.")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--out", type=Path, default=Path("data/seed_circular_tracks.jsonl"))
    args = parser.parse_args()

    with args.drafts.open() as f:
        lines = [json.loads(line) for line in f]

    with args.out.open("w") as out_f:
        for idx, row in enumerate(lines, start=1):
            question = row.get("question") or row.get("draft", {}).get("question", "")
            notes = row.get("notes") or row.get("draft", {}).get("steps", "")
            llm_res = call_llm(question, notes, args.api_url, args.api_key)
            formatted = {
                "id": f"{args.topic}_%03d" % idx,
                "topic": args.topic,
                "question": question,
                "options": row.get("options"),
                "answer": row.get("answer") or row.get("draft", {}).get("answer"),
                "difficulty": row.get("difficulty", "Medium"),
                "solutions": {
                    "direct": llm_res.get("direct"),
                    "step_by_step": llm_res.get("step_by_step"),
                    "intuitive": llm_res.get("intuitive"),
                    "shortcut": llm_res.get("shortcut"),
                },
                "source_frames": row.get("frames"),
            }
            out_f.write(json.dumps(formatted) + "\n")

    print(f"Wrote {len(lines)} items to {args.out}")


if __name__ == "__main__":
    main()

