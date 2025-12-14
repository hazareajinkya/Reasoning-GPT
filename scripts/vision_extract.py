"""
Takes frames + transcript chunks and calls a vision LLM to extract:
- Question text (including any table/arrangement)
- Teacher's solution steps
- Structured representation of diagrams/tables

This is a stub showing the contract. Wire to DeepSeek/Gemini/OpenAI Vision.
"""

import argparse
import json
import time
from pathlib import Path
from typing import Iterable

import base64
import httpx


def batched_frames(frames_dir: Path, batch_size: int = 1, skip: int = 0) -> Iterable[list[Path]]:
    """Process frames in batches. Default 1 frame at a time to avoid token limits."""
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if skip > 0:
        frames = frames[skip:]
    for i in range(0, len(frames), batch_size):
        yield frames[i : i + batch_size]


def call_vision_api(frames: list[Path], transcript_chunk: str, api_url: str, api_key: str, text_only: bool = False) -> dict:
    """
    OpenAI-compatible Vision call using chat/completions.
    Encodes each frame as base64 and sends as image_url with data URI.
    If text_only=True, skips images and only uses transcript.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    images = []
    if not text_only:
        for f in frames:
            b64 = base64.b64encode(f.read_bytes()).decode("utf-8")
            images.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    system_prompt = (
        "You are an educational content analyzer. Your task is to extract mathematical problem-solving content from tutorial video frames.\n\n"
        "For each frame, identify and extract:\n"
        "1. Question text: Any problem statement, including multiple choice options (A, B, C, D) if visible\n"
        "2. Visual elements: Diagrams, tables, circular tracks, speed/distance relationships shown\n"
        "3. Solution steps: Any mathematical steps, formulas, or reasoning shown on screen\n"
        "4. Answer: The final answer or option selected if visible\n\n"
        "Format your response clearly, preserving all numerical values and relationships exactly as shown."
    )
    user_content = []
    if not text_only:
        user_content.extend(images)
    
    if text_only:
        prompt_text = f"Below is a transcript from an educational tutorial video about circular tracks problems in CAT Quantitative Aptitude.\n\n"
        prompt_text += f"Please analyze the transcript and extract:\n"
        prompt_text += f"- The problem/question discussed\n"
        prompt_text += f"- Any mathematical concepts, formulas, or relationships mentioned\n"
        prompt_text += f"- Solution steps or explanations provided\n"
        prompt_text += f"- The answer if mentioned\n\n"
        prompt_text += f"Transcript:\n{transcript_chunk}"
    else:
        prompt_text = f"These are screenshots from an educational tutorial video about circular tracks problems in CAT Quantitative Aptitude.\n\n"
        prompt_text += f"Please analyze the frame(s) and extract:\n"
        prompt_text += f"- The problem/question shown\n"
        prompt_text += f"- Any diagrams or visual representations\n"
        prompt_text += f"- Solution steps or explanations visible\n"
        prompt_text += f"- The answer if shown\n\n"
        prompt_text += f"Transcript context: {transcript_chunk[:300] if len(transcript_chunk) > 300 else transcript_chunk}"
    
    user_content.append({
        "type": "text", 
        "text": prompt_text
    })

    payload = {
        "model": "gpt-4o-mini",  # Using gpt-4o-mini for vision (cheaper than gpt-4o)
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 800,
        "temperature": 0.2,
    }

    # Retry logic with exponential backoff for rate limits and timeouts
    max_retries = 10  # Increased retries
    base_wait = 30  # Start with 30 seconds (more conservative)
    for attempt in range(max_retries):
        try:
            resp = httpx.post(api_url, headers=headers, json=payload, timeout=300)
            
            # Log rate limit info (for debugging)
            if resp.status_code != 429:
                remaining_req = resp.headers.get("x-ratelimit-remaining-requests", "?")
                remaining_tok = resp.headers.get("x-ratelimit-remaining-tokens", "?")
                if attempt == 0:  # Only log on first attempt to avoid spam
                    print(f"[RPM:{remaining_req} TPM:{remaining_tok}]", end=" ", flush=True)
            
            if resp.status_code == 429:
                # Rate limited - check response for retry-after header and rate limit info
                retry_after = resp.headers.get("retry-after")
                limit_req = resp.headers.get("x-ratelimit-limit-requests", "?")
                limit_tok = resp.headers.get("x-ratelimit-limit-tokens", "?")
                remaining_req = resp.headers.get("x-ratelimit-remaining-requests", "0")
                remaining_tok = resp.headers.get("x-ratelimit-remaining-tokens", "0")
                
                print(f"\n[Rate Limit Info] RPM:{remaining_req}/{limit_req} TPM:{remaining_tok}/{limit_tok}", end=" ", flush=True)
                
                if retry_after:
                    wait_time = int(retry_after) + 5  # Add buffer
                    print(f"API says wait {retry_after}s. Waiting {wait_time}s...", end=" ", flush=True)
                else:
                    wait_time = min((2 ** attempt) * base_wait, 300)  # Cap at 5 minutes
                    print(f"Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...", end=" ", flush=True)
                
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    error_body = resp.text[:500] if resp.text else "No error details"
                    raise Exception(f"Rate limit exceeded after {max_retries} retries. Last error: {error_body}")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                retry_after = e.response.headers.get("retry-after")
                limit_req = e.response.headers.get("x-ratelimit-limit-requests", "?")
                limit_tok = e.response.headers.get("x-ratelimit-limit-tokens", "?")
                remaining_req = e.response.headers.get("x-ratelimit-remaining-requests", "0")
                remaining_tok = e.response.headers.get("x-ratelimit-remaining-tokens", "0")
                
                print(f"\n[Rate Limit Info] RPM:{remaining_req}/{limit_req} TPM:{remaining_tok}/{limit_tok}", end=" ", flush=True)
                
                if retry_after:
                    wait_time = int(retry_after) + 5
                    print(f"API says wait {retry_after}s. Waiting {wait_time}s...", end=" ", flush=True)
                else:
                    wait_time = min((2 ** attempt) * base_wait, 300)
                    print(f"Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
        except (httpx.TimeoutException, httpx.ReadTimeout):
            if attempt < max_retries - 1:
                wait_time = min((2 ** attempt) * base_wait, 300)
                print(f"Timeout. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            raise
    raise Exception("Max retries exceeded for rate limiting/timeouts")


def main():
    parser = argparse.ArgumentParser(description="Vision extraction stub.")
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--transcript-json", type=Path, help="Optional transcript json from ingest.")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--out", type=Path, default=Path("data/drafts"))
    parser.add_argument("--max-batches", type=int, help="Limit number of batches to process (for testing)")
    parser.add_argument("--skip-frames", type=int, default=0, help="Skip first N frames (to skip intro/logo frames)")
    parser.add_argument("--initial-wait", type=int, default=0, help="Wait N seconds before starting (to let rate limits reset)")
    parser.add_argument("--text-only", action="store_true", help="Skip images, only use transcript (for testing)")
    args = parser.parse_args()
    
    if args.initial_wait > 0:
        print(f"Waiting {args.initial_wait} seconds for rate limit window to reset...")
        time.sleep(args.initial_wait)

    transcript_text = ""
    if args.transcript_json and args.transcript_json.exists():
        meta = json.loads(args.transcript_json.read_text())
        transcript_text = json.dumps(meta.get("transcript", {}))

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{args.frames_dir.name}_drafts.jsonl"
    
    # Open file in append mode for incremental writing
    frames_list = sorted(args.frames_dir.glob("frame_*.jpg"))
    total_frames = len(frames_list)
    print(f"Found {total_frames} frames. Skipping first {args.skip_frames} frames. Processing in batches of 1...")
    
    batch_count = 0
    for idx, frame_batch in enumerate(batched_frames(args.frames_dir, skip=args.skip_frames)):
        if args.max_batches and idx >= args.max_batches:
            print(f"Stopping at {args.max_batches} batches (limit reached)")
            break
        batch_count += 1
        mode_str = "text-only" if args.text_only else f"{len(frame_batch)} frames"
        print(f"Processing batch {idx + 1} ({mode_str})...", end=" ", flush=True)
        chunk = transcript_text  # Simple pass-through; later chunk per timecodes.
        draft = call_vision_api(frame_batch, chunk, args.api_url, args.api_key, text_only=args.text_only)
        result = {"batch": idx, "frames": [f.name for f in frame_batch], "draft": draft}
        # Write incrementally so we can monitor progress
        with out_file.open("a") as f:
            f.write(json.dumps(result) + "\n")
        print("✓")
        # Rate limiting: wait time depends on mode
        if args.text_only:
            # Text-only uses much fewer tokens (~1-2K), so we can go faster
            time.sleep(2)  # 30 requests/minute = safe for text-only
        else:
            # With ~37K tokens per request, we need: 200K TPM / 37K = ~5.4 req/min max
            # 25s = 2.4 req/min = ~89K tokens/min (safe margin)
            time.sleep(25)

    print(f"Completed! Wrote {batch_count} batches to {out_file}")


if __name__ == "__main__":
    main()

