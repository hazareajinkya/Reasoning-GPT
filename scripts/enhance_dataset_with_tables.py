"""
Enhance existing dataset by adding tables/grids to solutions that don't have them.
This post-processes the dataset to include proper table-based solutions.
"""

import json
import os
import httpx
from pathlib import Path
from typing import Dict, List
import time

LLM_API_URL = os.environ.get("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


def has_table(solution_text: str) -> bool:
    """Check if solution already has table structures."""
    if not solution_text:
        return False
    return "|" in solution_text and ("---" in solution_text or "+" in solution_text)


def enhance_solution_with_tables(question: str, step_by_step: str, puzzle_type: str = None) -> str:
    """
    Use LLM to enhance step_by_step solution with tables.
    """
    if has_table(step_by_step):
        return step_by_step  # Already has tables
    
    prompt = f"""You are enhancing a DILR puzzle solution to match Gaurav Kapoor's methodology.

Original Question:
{question}

Current Solution (needs enhancement):
{step_by_step}

TASK: Enhance this solution by adding ASCII tables/grids showing:
1. Initial table/grid setup
2. Step-by-step table filling process
3. Constraint application shown visually in tables
4. Final solution table

CRITICAL REQUIREMENTS:
- Use ASCII tables with borders (| and -)
- Show actual tables, not just descriptions
- Match Gaurav Kapoor's table-based methodology
- For each step, display the complete table showing current state
- Use proper table formatting like:
  +--------+--------+--------+
  | Header1| Header2| Header3|
  +--------+--------+--------+
  | Value1 | Value2 | Value3 |
  +--------+--------+--------+

Return ONLY the enhanced solution with tables. Do not include explanations about what you did."""

    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a CAT DILR expert. Enhance solutions with proper ASCII tables matching Gaurav Kapoor's methodology."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
    }

    try:
        resp = httpx.post(LLM_API_URL, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        enhanced = data["choices"][0]["message"]["content"].strip()
        return enhanced
    except Exception as e:
        print(f"Error enhancing solution: {e}")
        return step_by_step  # Return original if enhancement fails


def enhance_dataset(input_path: Path, output_path: Path, max_items: int = None):
    """
    Enhance dataset by adding tables to solutions.
    """
    if not LLM_API_KEY:
        print("ERROR: Set LLM_API_KEY environment variable")
        return
    
    items = []
    with open(input_path, 'r') as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    
    if max_items:
        items = items[:max_items]
    
    print(f"Enhancing {len(items)} items from {input_path}...")
    print(f"Output will be saved to {output_path}")
    
    enhanced_items = []
    for i, item in enumerate(items, 1):
        print(f"\n[{i}/{len(items)}] Processing {item.get('id', 'unknown')}...")
        
        question = item.get('question', '')
        solutions = item.get('solutions', {})
        step_by_step = solutions.get('step_by_step', '')
        
        if not step_by_step:
            print("  ⚠️  No step_by_step solution found, skipping enhancement")
            enhanced_items.append(item)
            continue
        
        if has_table(step_by_step):
            print("  ✅ Already has tables, skipping")
            enhanced_items.append(item)
            continue
        
        print("  🔄 Enhancing with tables...")
        enhanced_step_by_step = enhance_solution_with_tables(question, step_by_step)
        
        # Update the item
        item['solutions']['step_by_step'] = enhanced_step_by_step
        enhanced_items.append(item)
        
        # Save incrementally
        with open(output_path, 'w') as f:
            for enhanced_item in enhanced_items:
                f.write(json.dumps(enhanced_item, ensure_ascii=False) + '\n')
        
        print(f"  ✅ Enhanced and saved")
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\n✅ Enhancement complete! Enhanced {len(enhanced_items)} items")
    print(f"Output saved to {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance dataset with tables")
    parser.add_argument("--input", type=Path, default=Path("data/seed_dilr.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/seed_dilr_enhanced.jsonl"))
    parser.add_argument("--max-items", type=int, help="Limit number of items to process (for testing)")
    
    args = parser.parse_args()
    
    enhance_dataset(args.input, args.output, args.max_items)


