"""
Automatically formats vision extraction drafts into canonical dataset.
Extracts problems from drafts and uses LLM to generate 4 solution styles.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import time

SYSTEM_PROMPT = (
    "You are a CAT Quantitative Aptitude expert. Given a problem statement and extracted notes, "
    "generate four types of solutions:\n"
    "1. **direct**: The direct answer with minimal explanation\n"
    "2. **step_by_step**: Detailed step-by-step solution with all calculations\n"
    "3. **intuitive**: The simplest, most intuitive approach that's easy to understand\n"
    "4. **shortcut**: Exam shortcut/trick method for quick solving\n\n"
    "Preserve all numerical values exactly as given. Do not invent data. "
    "If the answer is not provided, calculate it from the given information."
)


def extract_problem_from_content(content: str) -> Optional[Dict[str, str]]:
    """Extract structured problem info from vision LLM output."""
    problem = {
        "question": "",
        "data": "",
        "solution_steps": "",
        "answer": "",
    }
    
    # Skip if content indicates blank/no problem
    skip_indicators = [
        "blank", "does not contain", "no specific problem", "no visible content",
        "not provided", "not visible", "not shown", "not mentioned"
    ]
    if any(indicator in content.lower()[:200] for indicator in skip_indicators):
        return None
    
    # Try to extract question - look for actual questions
    question_patterns = [
        r'Question[:\s]+["\']([^"\']+?)["\']',
        r'Question[:\s]+([^\n]+?)(?:\n|$)',
        r'After how much[^\n]+',
        r'If ratio of speeds[^\n]+',
        r'Problem[:\s]+([^\n]+?)(?:\n|$)',
    ]
    for pattern in question_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            q_text = match.group(1) if match.groups() else match.group(0)
            # Only accept if it's a real question (not "no question" or similar)
            if len(q_text) > 10 and not any(skip in q_text.lower() for skip in skip_indicators):
                problem["question"] = q_text.strip()
                break
    
    # Extract data (speeds, distances, etc.) - require actual numbers
    data_patterns = [
        (r'(\d+)\s*m/s', 'speed'),
        (r'circumference[:\s]+(\d+)', 'circumference'),
        (r'diameter[:\s]+(\d+)', 'diameter'),
        (r'radius[:\s]+(\d+)', 'radius'),
        (r'(\d+)\s*m[,\s]', 'distance'),
    ]
    data_found = []
    for pattern, label in data_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                data_found.append(f"{label}: {match[0]}")
            else:
                data_found.append(f"{label}: {match}")
    
    if data_found:
        problem["data"] = "; ".join(set(data_found[:8]))  # Limit to avoid too long
    
    # Extract solution steps
    if any(kw in content for kw in ["T_A", "T_B", "LCM", "=", "calculate", "formula"]):
        solution_lines = []
        for line in content.split('\n'):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['solution', 'step', 'calculate', 'formula', 'lcm', 't_a', 't_b']) and '=' in line:
                solution_lines.append(line.strip())
        if solution_lines:
            problem["solution_steps"] = "\n".join(solution_lines[:8])
    
    # Extract answer
    answer_patterns = [
        r'Answer[:\s]+([^\n]+?)(?:\n|$)',
        r'answer is[:\s]+([^\n]+?)(?:\n|$)',
        r'(\d+)\s*seconds?',
        r'(\d+)\s*minutes?',
    ]
    for pattern in answer_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            ans = match.group(1) if match.groups() else match.group(0)
            if len(ans) < 50:  # Reasonable answer length
                problem["answer"] = ans.strip()
                break
    
    # Only return if we have meaningful data (question with data, or significant data)
    has_question = problem["question"] and len(problem["question"]) > 15
    has_data = problem["data"] and len(problem["data"]) > 10
    
    if (has_question and has_data) or (has_data and any(num in problem["data"] for num in ["120", "5", "2", "m/s"])):
        return problem
    return None


def call_llm_for_formatting(problem_text: str, extracted_notes: str, api_url: str, api_key: str) -> Dict[str, Any]:
    """Call LLM to generate 4 solution styles."""
    headers = {"Authorization": f"Bearer {api_key}"}
    
    user_prompt = f"""Problem:
{problem_text}

Extracted Information:
{extracted_notes}

Generate four solution styles in JSON format with these exact keys:
- "direct": Direct answer (brief)
- "step_by_step": Detailed step-by-step solution
- "intuitive": Simplest intuitive approach
- "shortcut": Exam shortcut/trick method

Return only valid JSON."""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 1500,
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    
    max_retries = 5
    base_wait = 5
    for attempt in range(max_retries):
        try:
            resp = httpx.post(api_url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 429:
                wait_time = min((2 ** attempt) * base_wait, 60)
                if attempt < max_retries - 1:
                    print(f"Rate limited. Waiting {wait_time}s...", end=" ", flush=True)
                    time.sleep(wait_time)
                    continue
            resp.raise_for_status()
            result = resp.json()
            # Extract content from response
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            return json.loads(content)
        except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
            if attempt < max_retries - 1:
                wait_time = min((2 ** attempt) * base_wait, 60)
                print(f"Error. Waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
        except json.JSONDecodeError:
            # Try to extract JSON from response
            try:
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                # Try to find JSON block
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except:
                pass
            raise Exception(f"Failed to parse JSON from LLM response: {content[:200]}")
    
    raise Exception("Max retries exceeded")


def process_draft_file(draft_file: Path, topic: str, api_url: str, api_key: str, out_file: Path, start_id: int = 1):
    """Process a draft file and format problems."""
    problems_found = []
    
    print(f"Reading {draft_file}...")
    with open(draft_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                content = data.get("draft", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Extract problem
                problem = extract_problem_from_content(content)
                if problem:
                    problem["source_frame"] = data.get("frame", data.get("source", "unknown"))
                    problem["raw_content"] = content[:500]  # Keep some raw for reference
                    problems_found.append(problem)
            except Exception as e:
                print(f"  ⚠️  Error processing line: {e}")
                continue
    
    print(f"  Found {len(problems_found)} problems to format")
    
    # Deduplicate similar problems
    unique_problems = []
    seen_questions = set()
    for prob in problems_found:
        q_key = prob["question"][:50] if prob["question"] else prob["data"][:30]
        if q_key and q_key not in seen_questions:
            seen_questions.add(q_key)
            unique_problems.append(prob)
    
    print(f"  After deduplication: {len(unique_problems)} unique problems")
    
    # Format each problem
    formatted_items = []
    for idx, problem in enumerate(unique_problems, start_id):
        print(f"  Formatting problem {idx}/{len(unique_problems)}...", end=" ", flush=True)
        
        # Build problem text
        problem_text = problem["question"] or "Circular tracks problem"
        if problem["data"]:
            problem_text += f"\nGiven: {problem['data']}"
        
        # Build notes
        notes = f"Solution steps: {problem['solution_steps']}\n" if problem["solution_steps"] else ""
        notes += f"Raw extraction: {problem['raw_content'][:300]}"
        
        try:
            solutions = call_llm_for_formatting(problem_text, notes, api_url, api_key)
            
            formatted_item = {
                "id": f"{topic}_{idx:03d}",
                "topic": topic,
                "question": problem["question"] or problem_text,
                "options": None,  # Can be added manually later
                "answer": problem["answer"] or solutions.get("direct", "").split()[-1] if solutions.get("direct") else "",
                "difficulty": "Medium",  # Default, can be refined
                "solutions": {
                    "direct": solutions.get("direct", ""),
                    "step_by_step": solutions.get("step_by_step", ""),
                    "intuitive": solutions.get("intuitive", ""),
                    "shortcut": solutions.get("shortcut", ""),
                },
                "source_frame": problem["source_frame"],
            }
            formatted_items.append(formatted_item)
            print("✓")
            time.sleep(2)  # Rate limit protection
            
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    # Write to output file
    with open(out_file, 'a') as f:  # Append mode to combine multiple videos
        for item in formatted_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"  ✅ Wrote {len(formatted_items)} formatted problems to {out_file}")
    return len(formatted_items)


def main():
    parser = argparse.ArgumentParser(description="Format vision drafts into canonical dataset.")
    parser.add_argument("--drafts", type=Path, required=True, help="JSONL draft file(s) - can be directory or file")
    parser.add_argument("--topic", default="circular_tracks", help="Topic name")
    parser.add_argument("--api-url", required=True, help="LLM API URL")
    parser.add_argument("--api-key", required=True, help="LLM API key")
    parser.add_argument("--out", type=Path, default=Path("data/seed_circular_tracks.jsonl"), help="Output file")
    parser.add_argument("--max-problems", type=int, help="Limit number of problems to process (for testing)")
    args = parser.parse_args()
    
    # Handle directory or single file
    draft_files = []
    if args.drafts.is_dir():
        draft_files = list(args.drafts.glob("*_drafts.jsonl"))
    else:
        draft_files = [args.drafts]
    
    if not draft_files:
        print(f"❌ No draft files found at {args.drafts}")
        return
    
    print(f"📁 Processing {len(draft_files)} draft file(s)...")
    print(f"📝 Output: {args.out}")
    print()
    
    # Clear or create output file
    if args.out.exists():
        print(f"⚠️  Output file exists. Clearing and starting fresh.")
        args.out.unlink()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("")  # Create empty file
    
    total_formatted = 0
    next_id = 1
    for draft_file in draft_files:
        print(f"\n{'='*60}")
        print(f"Processing: {draft_file.name}")
        print('='*60)
        
        count = process_draft_file(draft_file, args.topic, args.api_url, args.api_key, args.out, start_id=next_id)
        total_formatted += count
        next_id += count
        
        if args.max_problems and total_formatted >= args.max_problems:
            print(f"\n⚠️  Reached max problems limit ({args.max_problems})")
            break
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE! Total formatted: {total_formatted} problems")
    print(f"📁 Output: {args.out}")
    print('='*60)


if __name__ == "__main__":
    main()

