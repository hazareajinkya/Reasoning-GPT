"""
Format extracted LRDI puzzles into canonical dataset structure with 4 solution styles.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

import httpx


def format_puzzle_to_canonical(puzzle_data: Dict, llm_api_url: str, llm_api_key: str) -> Dict:
    """Format a puzzle draft into canonical structure with 4 solution styles."""
    
    draft_content = puzzle_data.get("draft", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
    puzzle_num = puzzle_data.get("puzzle_num", 0)
    puzzle_type = puzzle_data.get("puzzle_type", "")
    
    # Extract question from draft
    question = ""
    if "### Puzzle/Question Statement:" in draft_content:
        parts = draft_content.split("### Puzzle/Question Statement:")
        if len(parts) > 1:
            question = parts[1].split("###")[0].strip()
    
    # Extract answer if available
    answer = ""
    if "### Answer:" in draft_content:
        parts = draft_content.split("### Answer:")
        if len(parts) > 1:
            answer = parts[1].split("###")[0].strip()
    
    # Extract solution approach
    solution_approach = ""
    if "### Solution Approach:" in draft_content:
        parts = draft_content.split("### Solution Approach:")
        if len(parts) > 1:
            solution_approach = parts[1].split("###")[0].strip()
    
    # Use LLM to generate 4 solution styles
    prompt = f"""You are formatting a CAT LRDI puzzle solution. Given the extracted content, generate 4 solution styles:

Puzzle Type: {puzzle_type}
Question: {question[:500]}

Solution Approach from video: {solution_approach[:500]}

Answer: {answer[:200]}

Generate 4 solution styles in JSON format:
1. direct: Brief direct answer (1-2 sentences)
2. step_by_step: Detailed step-by-step solution with all reasoning
3. intuitive: Simplest intuitive explanation (how to think about it)
4. shortcut: Quick exam trick/shortcut method

Return ONLY valid JSON with keys: direct, step_by_step, intuitive, shortcut"""

    try:
        headers = {"Authorization": f"Bearer {llm_api_key}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a CAT LRDI expert. Format solutions clearly and concisely."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 1500,
        }
        
        resp = httpx.post(llm_api_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        solutions = resp.json()
        
        # Extract from choices if OpenAI format
        if "choices" in solutions:
            content = solutions["choices"][0]["message"]["content"]
            solutions = json.loads(content)
        
    except Exception as e:
        print(f"⚠️  LLM call failed for puzzle {puzzle_num}: {e}")
        # Fallback: use extracted content
        solutions = {
            "direct": answer or "Answer not extracted",
            "step_by_step": solution_approach or draft_content[:500],
            "intuitive": "Use logical reasoning and constraints to solve systematically.",
            "shortcut": "Identify key constraints first, then eliminate options."
        }
    
    # Build canonical structure
    canonical = {
        "id": f"lrdi_{puzzle_num:03d}",
        "topic": "lrdi",
        "puzzle_type": puzzle_type,
        "question": question or f"Puzzle {puzzle_num}: {puzzle_type}",
        "answer": answer,
        "solutions": {
            "direct": solutions.get("direct", ""),
            "step_by_step": solutions.get("step_by_step", ""),
            "intuitive": solutions.get("intuitive", ""),
            "shortcut": solutions.get("shortcut", ""),
        },
        "difficulty": "medium",  # Default, can be updated
        "source": "4HourLrdiMarathon",
        "timestamp": puzzle_data.get("timestamp", ""),
    }
    
    return canonical


def main():
    parser = argparse.ArgumentParser(description="Format LRDI puzzles into canonical dataset")
    parser.add_argument("--drafts", type=Path, required=True, help="Input drafts JSONL file")
    parser.add_argument("--out", type=Path, default=Path("data/seed_lrdi.jsonl"), help="Output file")
    parser.add_argument("--api-url", required=True, help="LLM API URL")
    parser.add_argument("--api-key", required=True, help="LLM API key")
    parser.add_argument("--max-puzzles", type=int, help="Limit number of puzzles to format (for testing)")
    args = parser.parse_args()
    
    # Load drafts
    puzzles = []
    with open(args.drafts, 'r') as f:
        for line in f:
            puzzles.append(json.loads(line))
    
    if args.max_puzzles:
        puzzles = puzzles[:args.max_puzzles]
    
    print(f"Formatting {len(puzzles)} puzzles...")
    print("=" * 80)
    
    formatted = []
    for idx, puzzle in enumerate(puzzles, 1):
        puzzle_num = puzzle.get("puzzle_num", idx)
        puzzle_type = puzzle.get("puzzle_type", "Unknown")
        print(f"Formatting Puzzle {puzzle_num}: {puzzle_type[:50]}...", end=" ", flush=True)
        
        try:
            canonical = format_puzzle_to_canonical(puzzle, args.api_url, args.api_key)
            formatted.append(canonical)
            print("✓")
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Save formatted dataset
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w') as f:
        for item in formatted:
            f.write(json.dumps(item) + "\n")
    
    print()
    print("=" * 80)
    print(f"✅ Formatted {len(formatted)} puzzles")
    print(f"📁 Output: {args.out}")


if __name__ == "__main__":
    main()

