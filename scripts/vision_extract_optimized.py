"""
OPTIMIZED VISION EXTRACTION - Cost-effective approach:
1. Process transcript first (text-only, cheap)
2. Only process frames every 30 seconds (key moments)
3. Combine transcript + visual info intelligently
"""

import argparse
import json
import time
from pathlib import Path
from typing import Iterable

import base64
import httpx


def get_frame_interval(frames_dir: Path, interval_seconds: int = 30) -> list[Path]:
    """
    Get frames at specified intervals (e.g., every 30 seconds).
    Assumes frames were extracted every 2 seconds (from ingest_youtube.py).
    So every 30 seconds = every 15th frame (30/2 = 15).
    """
    all_frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not all_frames:
        return []
    
    # Frames are extracted every 2 seconds, so interval_seconds/2 = frame skip
    frame_skip = max(1, interval_seconds // 2)  # Every 15 frames for 30 seconds
    
    # Also skip first few frames (intro/logo)
    skip_intro = 5  # Skip first ~10 seconds
    
    selected_frames = []
    for i in range(skip_intro, len(all_frames), frame_skip):
        selected_frames.append(all_frames[i])
    
    return selected_frames


def call_text_api(transcript_text: str, api_url: str, api_key: str) -> dict:
    """Call API with text-only (transcript) - much cheaper."""
    headers = {"Authorization": f"Bearer {api_key}"}
    
    system_prompt = (
        "You are an educational content analyzer. Extract mathematical problem-solving content from tutorial video transcripts.\n\n"
        "For the transcript, identify and extract:\n"
        "1. Question text: Problem statements, including multiple choice options (A, B, C, D) if mentioned\n"
        "2. Mathematical concepts: Formulas, relationships, speed/distance/time calculations\n"
        "3. Solution steps: Step-by-step explanations and reasoning\n"
        "4. Answer: Final answer or selected option if mentioned\n\n"
        "Format your response clearly, preserving all numerical values and relationships exactly as mentioned."
    )
    
    user_content = (
        f"Below is a transcript from an educational tutorial video about circular tracks problems in CAT Quantitative Aptitude.\n\n"
        f"Please analyze the transcript and extract:\n"
        f"- The problem/question discussed\n"
        f"- Any mathematical concepts, formulas, or relationships mentioned\n"
        f"- Solution steps or explanations provided\n"
        f"- The answer if mentioned\n\n"
        f"Transcript:\n{transcript_text}"
    )
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
    }
    
    # Retry logic
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
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = min((2 ** attempt) * base_wait, 60)
                print(f"Rate limited. Waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
        except (httpx.TimeoutException, httpx.ReadTimeout):
            if attempt < max_retries - 1:
                wait_time = min((2 ** attempt) * base_wait, 60)
                print(f"Timeout. Waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
    raise Exception("Max retries exceeded")


def call_vision_api(frame: Path, transcript_chunk: str, api_url: str, api_key: str) -> dict:
    """Call API with single frame + transcript context - only for key moments."""
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Encode frame
    b64 = base64.b64encode(frame.read_bytes()).decode("utf-8")
    
    system_prompt = (
        "You are an educational content analyzer. Extract mathematical problem-solving content from tutorial video frames.\n\n"
        "For this frame, identify and extract:\n"
        "1. Question text: Any problem statement, including multiple choice options (A, B, C, D) if visible\n"
        "2. Visual elements: Diagrams, tables, circular tracks, speed/distance relationships shown\n"
        "3. Solution steps: Any mathematical steps, formulas, or reasoning shown on screen\n"
        "4. Answer: The final answer or option selected if visible\n\n"
        "Format your response clearly, preserving all numerical values and relationships exactly as shown."
    )
    
    user_content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        {
            "type": "text",
            "text": (
                f"This is a key frame from an educational tutorial video about circular tracks problems in CAT Quantitative Aptitude.\n\n"
                f"Please analyze the frame and extract:\n"
                f"- The problem/question shown\n"
                f"- Any diagrams or visual representations\n"
                f"- Solution steps or explanations visible\n"
                f"- The answer if shown\n\n"
                f"Transcript context: {transcript_chunk[:500]}"
            )
        }
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 800,
        "temperature": 0.2,
    }
    
    # Retry logic with longer waits for vision (expensive)
    max_retries = 5
    base_wait = 30
    for attempt in range(max_retries):
        try:
            resp = httpx.post(api_url, headers=headers, json=payload, timeout=300)
            if resp.status_code == 429:
                wait_time = min((2 ** attempt) * base_wait, 300)
                if attempt < max_retries - 1:
                    print(f"Rate limited. Waiting {wait_time}s...", end=" ", flush=True)
                    time.sleep(wait_time)
                    continue
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
    parser = argparse.ArgumentParser(description="Optimized vision extraction - transcript-first, frames at intervals.")
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--transcript-json", type=Path, required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--out", type=Path, default=Path("data/drafts"))
    parser.add_argument("--frame-interval", type=int, default=30, help="Process frames every N seconds (default: 30)")
    parser.add_argument("--skip-vision", action="store_true", help="Skip vision API calls, only use transcript")
    args = parser.parse_args()
    
    # Load transcript
    if not args.transcript_json.exists():
        raise FileNotFoundError(f"Transcript not found: {args.transcript_json}")
    
    meta = json.loads(args.transcript_json.read_text())
    transcript_data = meta.get("transcript", {})
    
    # Extract transcript text - try to fetch, but fallback gracefully
    transcript_text = ""
    transcript_available = False
    
    if isinstance(transcript_data, dict):
        tracks = transcript_data.get("tracks", [])
        if tracks and isinstance(tracks, list) and len(tracks) > 0:
            # Try to fetch transcript from URL
            for track in tracks:
                if isinstance(track, dict):
                    track_url = track.get("url", "")
                    if track_url:
                        try:
                            resp = httpx.get(track_url, timeout=10, follow_redirects=True)
                            if resp.status_code == 200:
                                content = resp.text
                                # Try parsing as JSON3
                                try:
                                    data = json.loads(content)
                                    text_parts = []
                                    for event in data.get("events", []):
                                        for seg in event.get("segs", []):
                                            if "utf8" in seg:
                                                text_parts.append(seg["utf8"])
                                    transcript_text = " ".join(text_parts)
                                    transcript_available = True
                                    break
                                except:
                                    # Not JSON, use as text
                                    transcript_text = content
                                    transcript_available = True
                                    break
                        except Exception as e:
                            continue
    
    if not transcript_available:
        # Fallback: use metadata as context
        transcript_text = json.dumps(transcript_data)
        print("⚠️  Could not fetch transcript from URL, using metadata as context")
    
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{args.frames_dir.name}_drafts.jsonl"
    
    # STEP 1: Process transcript (text-only, cheap)
    print("=" * 60)
    print("STEP 1: Processing transcript (text-only, low cost)...")
    print("=" * 60)
    
    if transcript_text and len(transcript_text) > 100:  # Only if we have meaningful transcript
        print("Extracting from transcript...", end=" ", flush=True)
        try:
            transcript_result = call_text_api(transcript_text, args.api_url, args.api_key)
            result = {
                "type": "transcript",
                "source": "text_only",
                "draft": transcript_result
            }
            with out_file.open("w") as f:  # Write mode to start fresh
                f.write(json.dumps(result) + "\n")
            print("✓")
            time.sleep(2)  # Small delay between text requests
        except Exception as e:
            print(f"✗ Failed: {e}")
            # Continue with frames even if transcript fails
            with out_file.open("w") as f:
                f.write(json.dumps({"type": "transcript", "error": str(e)}) + "\n")
    else:
        print("⚠️  Skipping transcript (not available or too short)")
        with out_file.open("w") as f:
            f.write(json.dumps({"type": "transcript", "skipped": True}) + "\n")
    
    # STEP 2: Process key frames (every 30 seconds, expensive but necessary)
    if not args.skip_vision:
        print("\n" + "=" * 60)
        print(f"STEP 2: Processing key frames (every {args.frame_interval} seconds)...")
        print("=" * 60)
        
        key_frames = get_frame_interval(args.frames_dir, args.frame_interval)
        print(f"Selected {len(key_frames)} key frames from {len(list(args.frames_dir.glob('frame_*.jpg')))} total frames")
        
        for idx, frame in enumerate(key_frames):
            print(f"Processing frame {idx + 1}/{len(key_frames)} ({frame.name})...", end=" ", flush=True)
            
            # Use relevant transcript chunk (first 500 chars for context)
            frame_result = call_vision_api(frame, transcript_text[:500], args.api_url, args.api_key)
            
            result = {
                "type": "frame",
                "source": "vision",
                "frame": frame.name,
                "draft": frame_result
            }
            with out_file.open("a") as f:
                f.write(json.dumps(result) + "\n")
            print("✓")
            
            # Wait 25 seconds between vision API calls (rate limit safety)
            if idx < len(key_frames) - 1:  # Don't wait after last frame
                time.sleep(25)
    
    print("\n" + "=" * 60)
    print("✅ EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"Output: {out_file}")
    
    # Cost estimate
    text_cost = 0.00015 * (len(transcript_text) / 4 / 1_000_000)  # ~$0.15 per 1M input tokens
    if not args.skip_vision:
        vision_cost = len(key_frames) * 0.0055  # ~$0.0055 per frame (37K tokens)
        total_cost = text_cost + vision_cost
        print(f"\n💰 Estimated cost:")
        print(f"   Transcript: ~${text_cost:.4f}")
        print(f"   {len(key_frames)} frames: ~${vision_cost:.2f}")
        print(f"   Total: ~${total_cost:.2f}")


if __name__ == "__main__":
    main()

