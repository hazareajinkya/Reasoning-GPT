"""
Extract LRDI problems using timestamps - Version 2 for 6-hour marathon.
"""

import argparse
import json
import time
from pathlib import Path
from typing import List

import base64
import httpx


def parse_timestamp(ts_str: str) -> int:
    """Convert timestamp string (e.g., '3:55' or '1:05:36') to seconds."""
    parts = ts_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def get_frames_at_timestamp(frames_dir: Path, timestamp_seconds: int, duration_seconds: int = None) -> List[Path]:
    """Get frames around a timestamp."""
    all_frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not all_frames:
        return []
    
    start_frame_idx = max(0, timestamp_seconds // 2)
    selected = []
    
    # Question frames (first ~10 seconds)
    for offset in [0, 5]:
        idx = start_frame_idx + (offset // 2)
        if idx < len(all_frames):
            selected.append(all_frames[idx])
    
    # Explanation frames
    if duration_seconds:
        for pct in [0.2, 0.4, 0.6, 0.8]:
            offset = int(duration_seconds * pct)
            idx = start_frame_idx + (offset // 2)
            if idx < len(all_frames) and all_frames[idx] not in selected:
                selected.append(all_frames[idx])
    else:
        for offset in [20, 40]:
            idx = start_frame_idx + (offset // 2)
            if idx < len(all_frames) and all_frames[idx] not in selected:
                selected.append(all_frames[idx])
    
    return sorted(set(selected))


def call_vision_api(frames: List[Path], transcript_chunk: str, puzzle_num: int, puzzle_type: str, api_url: str, api_key: str) -> dict:
    """Call vision API to extract puzzle content."""
    headers = {"Authorization": f"Bearer {api_key}"}
    images = []
    for f in frames:
        b64 = base64.b64encode(f.read_bytes()).decode("utf-8")
        images.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    system_prompt = (
        "You are an educational content analyzer. Extract LRDI (Logical Reasoning & Data Interpretation) puzzle content from tutorial video frames.\n\n"
        "For each frame, identify and extract:\n"
        "1. Question/Puzzle statement: Problem description, constraints, conditions\n"
        "2. Visual elements: Tables, diagrams, arrangements, distributions, Venn diagrams, grids\n"
        "3. Solution approach: Step-by-step reasoning, methods, techniques shown\n"
        "4. Answer: Final answer or solution if visible\n\n"
        "Format your response clearly, preserving all numerical values, constraints, and relationships exactly as shown."
    )
    
    user_content = []
    user_content.extend(images)
    user_content.append({
        "type": "text",
        "text": f"These are screenshots from Puzzle #{puzzle_num} ({puzzle_type}) in a CAT LRDI marathon tutorial.\n\n"
                f"Please analyze the frame(s) and extract:\n"
                f"- The complete puzzle/question statement\n"
                f"- Any tables, diagrams, or visual representations\n"
                f"- Solution approach and reasoning steps shown\n"
                f"- The answer if shown\n\n"
                f"Transcript context: {transcript_chunk[:300] if len(transcript_chunk) > 300 else transcript_chunk}"
    })

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
    }

    max_retries = 10
    base_wait = 25
    for attempt in range(max_retries):
        try:
            resp = httpx.post(api_url, headers=headers, json=payload, timeout=300)
            
            if resp.status_code != 429:
                remaining_req = resp.headers.get("x-ratelimit-remaining-requests", "?")
                remaining_tok = resp.headers.get("x-ratelimit-remaining-tokens", "?")
                if attempt == 0:
                    print(f"[RPM:{remaining_req} TPM:{remaining_tok}]", end=" ", flush=True)
            
            if resp.status_code == 429:
                retry_after = resp.headers.get("retry-after")
                if retry_after:
                    wait_time = int(retry_after) + 5
                    print(f"Rate limited. Waiting {wait_time}s...", end=" ", flush=True)
                else:
                    wait_time = min((2 ** attempt) * base_wait, 300)
                    print(f"Rate limited. Waiting {wait_time}s...", end=" ", flush=True)
                
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} retries")
            
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = min((2 ** attempt) * base_wait, 300)
                print(f"Rate limited. Waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
        except (httpx.TimeoutException, httpx.ReadTimeout):
            if attempt < max_retries - 1:
                wait_time = min((2 ** attempt) * base_wait, 300)
                print(f"Timeout. Waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
    
    raise Exception("Max retries exceeded")


def main():
    parser = argparse.ArgumentParser(description="Extract LRDI puzzles using timestamps (6-hour marathon)")
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--transcript-json", type=Path, help="Transcript JSON")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--out", type=Path, default=Path("data/drafts"))
    args = parser.parse_args()
    
    # Puzzle timestamps for 6-hour marathon
    puzzles = [
        ("0:00", "Intro & the process", 0),
        ("2:47", "Puzzle 1 - DI - Table filling & missing columns", 1),
        ("14:26", "Puzzle 2 - Routes & Networks - Most efficient paths", 2),
        ("33:56", "Puzzle 3 - Quant-based LR – Distribution", 3),
        ("49:14", "Puzzle 4 - DI - Bar Charts - Frequency Chart", 4),
        ("1:02:08", "Puzzle 5 - Conditional Table Filling & Selection Puzzle", 5),
        ("1:16:45", "Puzzle 6 - 3-Set Venn Diagram – Overlapping Categories Puzzle", 6),
        ("1:30:17", "Puzzle 7 - DI Scattered Charts", 7),
        ("1:42:34", "Puzzle 8 - Quantitative reasoning & logical table-filling, Min - Max Grid", 8),
        ("1:50:28", "Puzzle 9 - Sequential Ordering", 9),
        ("2:07:49", "Puzzle 10 - 3-Set Venn Diagram Puzzle with maxima minima Logics", 10),
        ("2:22:13", "Puzzle 11 - Percentage Bar-Chart Based DI", 11),
        ("2:30:53", "Puzzle 12 - Games - Round robin and Knockout tournament", 12),
        ("2:43:33", "Puzzle 13 - Movement based DILR Puzzle", 13),
        ("2:58:25", "Puzzle 14 - DI Caselet + Table filling", 14),
        ("3:13:49", "Puzzle 15 - Quant based Logical puzzle", 15),
        ("3:26:35", "Puzzle 16 - Logical reasoning based table filling", 16),
        ("3:38:52", "Puzzle 17 - Games Puzzle - One on One game with rules", 17),
        ("3:54:48", "Puzzle 18 - 4 Set venn diagram", 18),
        ("4:07:13", "Puzzle 19 - DI table filling - Complete the grid", 19),
        ("4:20:50", "Puzzle 20 - Games - Constant Sum game with values exchanged among them", 20),
        ("4:35:41", "Puzzle 21 - 2 day average & ranking puzzle", 21),
        ("4:45:15", "Puzzle 22 - DI Caselet with 4 x 2 x 2 working", 22),
        ("4:56:32", "Puzzle 23 - Binary Matrix / Logical Grid Identification Puzzle", 23),
        ("5:12:08", "Puzzle 24 - Currency exchange DILR puzzle", 24),
        ("5:28:04", "Puzzle 25 - Multiple constraints set theory - 2 set venn diagram with multiple connections", 25),
        ("5:37:59", "Puzzle 26 - Distribution Puzzle", 26),
        ("5:48:16", "Puzzle 27 - 3d - Routes and Networks - Finding correct paths", 27),
        ("5:57:59", "Puzzle 28 - Team Composition Puzzle", 28),
        ("6:09:55", "Puzzle 29 - Hard DI Caselet", 29),
    ]
    
    # Load transcript if available
    transcript_text = ""
    if args.transcript_json and args.transcript_json.exists():
        meta = json.loads(args.transcript_json.read_text())
        transcript_entries = meta.get("transcript", {}).get("text", [])
        if transcript_entries:
            transcript_text = " ".join([entry.get("text", "") for entry in transcript_entries])
    
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{args.frames_dir.name}_drafts.jsonl"
    
    all_results = []
    total_cost = 0.0
    
    print("=" * 80)
    print(f"EXTRACTING LRDI PUZZLES FROM 6-HOUR MARATHON")
    print("=" * 80)
    print(f"Total puzzles: {len(puzzles) - 1} (skipping intro)")
    print()
    
    # Skip intro, process puzzles
    for idx, (ts_str, puzzle_type, puzzle_num) in enumerate(puzzles[1:], 1):  # Skip intro
        timestamp_seconds = parse_timestamp(ts_str)
        
        # Calculate duration to next puzzle (or end)
        if idx < len(puzzles) - 1:
            next_ts = parse_timestamp(puzzles[idx][0])
            duration = next_ts - timestamp_seconds
        else:
            duration = 60  # Default 60s for last puzzle
        
        print(f"Puzzle {puzzle_num}: {puzzle_type[:60]}... (at {ts_str})", end=" ... ", flush=True)
        
        # Get frames for this puzzle
        frames = get_frames_at_timestamp(args.frames_dir, timestamp_seconds, duration)
        if not frames:
            print("⚠️  No frames found")
            continue
        
        print(f"{len(frames)} frames", end=" ", flush=True)
        
        try:
            draft = call_vision_api(frames, transcript_text, puzzle_num, puzzle_type, args.api_url, args.api_key)
            all_results.append({
                "type": "puzzle",
                "puzzle_num": puzzle_num,
                "puzzle_type": puzzle_type,
                "timestamp": ts_str,
                "frames": [f.name for f in frames],
                "draft": draft
            })
            total_cost += 0.0055
            print("✓")
            
            # Write incrementally
            with out_file.open("a") as f:
                f.write(json.dumps(all_results[-1]) + "\n")
            
            time.sleep(25)  # Rate limit delay
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("=" * 80)
    print("✅ EXTRACTION COMPLETE!")
    print("=" * 80)
    print(f"Output: {out_file}")
    print(f"Total puzzles processed: {len(all_results)}")
    print(f"💰 Estimated cost: ~${total_cost:.2f}")


if __name__ == "__main__":
    main()

