"""
Extract LRDI problems using timestamps.
For each puzzle timestamp, extracts:
- Question frame(s) at start (first ~10 seconds)
- Explanation/answer frames (spaced through the segment)
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
    """
    Get frames around a timestamp.
    - Question frames: timestamp + 0s, +5s (first ~10 seconds)
    - Explanation frames: spaced through the segment
    """
    all_frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not all_frames:
        return []
    
    # Frames are extracted every 2 seconds, so frame index = timestamp / 2
    start_frame_idx = max(0, timestamp_seconds // 2)
    
    selected = []
    
    # Question frames (first ~10 seconds)
    for offset in [0, 5]:  # At timestamp and +5 seconds
        idx = start_frame_idx + (offset // 2)
        if idx < len(all_frames):
            selected.append(all_frames[idx])
    
    # Explanation frames (if duration provided, space them out)
    if duration_seconds:
        # Get frames at 20%, 40%, 60%, 80% of the segment
        for pct in [0.2, 0.4, 0.6, 0.8]:
            offset = int(duration_seconds * pct)
            idx = start_frame_idx + (offset // 2)
            if idx < len(all_frames) and all_frames[idx] not in selected:
                selected.append(all_frames[idx])
    else:
        # Default: get frames at +20s, +40s if available
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

    # Retry logic with exponential backoff
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
    parser = argparse.ArgumentParser(description="Extract LRDI puzzles using timestamps")
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--transcript-json", type=Path, help="Transcript JSON")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--out", type=Path, default=Path("data/drafts"))
    parser.add_argument("--timestamps-file", type=Path, help="JSON file with puzzle timestamps")
    args = parser.parse_args()
    
    # Puzzle timestamps (from user's message)
    puzzles = [
        ("0:00", "Intro & the process", 0),
        ("3:55", "Puzzle 1 (Circular Arrangements)", 1),
        ("8:31", "Puzzle 2 (New way to solve arrangements)", 2),
        ("17:11", "Puzzle 3 (Ring cutting concept)", 3),
        ("28:43", "Puzzle 4 (Correct Incorrect Concept)", 4),
        ("38:08", "Puzzle 5 (DI - Table Charts & learn how to deal with percentages)", 5),
        ("47:45", "Puzzle 6 (Grid approach)", 6),
        ("58:10", "Puzzle 7 (Fill in the table - Puzzle with conditions)", 7),
        ("1:05:36", "Puzzle 8 (Denominations - Type 1 puzzle)", 8),
        ("1:13:01", "Puzzle 9 (Set theory - 3 methods)", 9),
        ("1:26:53", "Puzzle 10 (Bottle Neck - Type 2 puzzle)", 10),
        ("1:30:54", "Puzzle 11 (Shifting averages concept)", 11),
        ("1:39:07", "Puzzle 12 (Options usage)", 12),
        ("1:47:19", "Puzzle 13 (Denominations - Type 2 Puzzle)", 13),
        ("1:50:12", "Puzzle 14 (4 set venn diagram)", 14),
        ("2:00:06", "Puzzle 15 (5 set venn diagram)", 15),
        ("2:11:28", "Puzzle 16 (Distribution concept & option usage)", 16),
        ("2:15:39", "Puzzle 17 (Binary or Truth & Lie concept)", 17),
        ("2:20:56", "Puzzle 18 (Rank shifting Puzzle)", 18),
        ("2:30:36", "Puzzle 19 (Flight timings)", 19),
        ("2:37:54", "Puzzle 20 (Maximize & Minimize - Set theory)", 20),
        ("2:52:29", "Puzzle 21 (At most 2 maximize - Set theory)", 21),
        ("2:58:41", "Puzzle 22 (Entry & Exit concept)", 22),
        ("3:05:21", "Puzzle 23 (Cricket - Puzzle concept)", 23),
        ("3:09:26", "Puzzle 24 (Unconventional Puzzle)", 24),
        ("3:14:04", "Puzzle 25 (Routes & Networks)", 25),
        ("3:20:39", "Puzzle 26 (Ranking based Matrix)", 26),
        ("3:26:21", "Puzzle 27 (Selections - Tabular method)", 27),
        ("3:36:12", "Puzzle 28 (Project Management)", 28),
        ("3:39:55", "Puzzle 29 (Cumulative Addition error concept)", 29),
        ("3:44:43", "Puzzle 30 (Rank/Order Concept)", 30),
        ("3:53:56", "Puzzle 31 (Cumulative addition complete concept)", 31),
        ("4:01:38", "Puzzle 32 (Bar graphs - Deal with percentages)", 32),
        ("4:06:26", "Puzzle 33 (Table Charts - Ways to read the data carefully)", 33),
        ("4:10:16", "Puzzle 34 (Project Management - Important type)", 34),
        ("4:14:26", "Puzzle 35 (Coins picking Method)", 35),
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
    print(f"EXTRACTING LRDI PUZZLES FROM TIMESTAMPS")
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
        
        print(f"Puzzle {puzzle_num}: {puzzle_type} (at {ts_str})", end=" ... ", flush=True)
        
        # Get frames for this puzzle
        frames = get_frames_at_timestamp(args.frames_dir, timestamp_seconds, duration)
        if not frames:
            print("⚠️  No frames found")
            continue
        
        print(f"{len(frames)} frames", end=" ", flush=True)
        
        try:
            # Extract relevant transcript chunk (simplified - could be improved)
            draft = call_vision_api(frames, transcript_text, puzzle_num, puzzle_type, args.api_url, args.api_key)
            all_results.append({
                "type": "puzzle",
                "puzzle_num": puzzle_num,
                "puzzle_type": puzzle_type,
                "timestamp": ts_str,
                "frames": [f.name for f in frames],
                "draft": draft
            })
            total_cost += 0.0055  # Approx cost per vision call
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

