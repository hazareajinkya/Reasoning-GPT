"""
Optional vision enhancement for RAG - uses images only when needed.
This is cost-effective: text-only retrieval first, then optionally enhance with images.
"""

import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
import httpx


def get_frames_for_item(item: Dict[str, Any], frames_base_dir: Path) -> List[Path]:
    """
    Get frame paths for a retrieved item if available.
    Items can have:
    - frame_paths: list of frame file paths
    - timestamp: video timestamp to find frames
    - source: video source name
    """
    frames = []
    
    # Check if item has direct frame paths
    if "frame_paths" in item:
        for fp in item["frame_paths"]:
            path = Path(fp)
            if path.exists():
                frames.append(path)
        return frames
    
    # Try to find frames by timestamp and source
    if "timestamp" in item and "source" in item:
        source = item["source"]
        timestamp = item["timestamp"]
        
        # Try to find frames directory
        frames_dir = frames_base_dir / source
        if frames_dir.exists():
            # Find frames near the timestamp
            # Assuming frames are named like frame_001.jpg, frame_002.jpg, etc.
            # and correspond to time intervals
            all_frames = sorted(frames_dir.glob("frame_*.jpg"))
            if all_frames:
                # Simple heuristic: take 1-3 frames around the timestamp
                # This is a placeholder - you'd need to map timestamp to frame number
                # For now, just take first few frames as example
                frames = all_frames[:3]
    
    return frames


def enhance_with_vision(
    question: str,
    contexts: List[Dict[str, Any]],
    frames_base_dir: Path,
    api_url: str,
    api_key: str,
    max_frames_per_context: int = 2
) -> Optional[str]:
    """
    Optionally enhance the prompt with visual context from frames.
    Only uses images for the top 1-2 contexts to save costs.
    
    Returns enhanced prompt text, or None if no frames found.
    """
    # Only use images for top 1-2 contexts to save costs
    top_contexts = contexts[:2]
    all_frames = []
    
    for ctx in top_contexts:
        frames = get_frames_for_item(ctx, frames_base_dir)
        if frames:
            all_frames.extend(frames[:max_frames_per_context])
            break  # Only use frames from first matching context
    
    if not all_frames:
        return None  # No frames available, use text-only
    
    # Build vision-enhanced prompt
    # Encode frames as base64
    images = []
    for frame_path in all_frames:
        try:
            b64 = base64.b64encode(frame_path.read_bytes()).decode("utf-8")
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        except Exception as e:
            print(f"Warning: Could not read frame {frame_path}: {e}")
            continue
    
    if not images:
        return None
    
    # Return a note that images are included (actual image data handled in API call)
    return f"[Vision enhancement: {len(images)} frame(s) from reference solution included]"


def call_llm_with_vision(
    question: str,
    contexts: List[Dict[str, Any]],
    frames_base_dir: Path,
    api_url: str,
    api_key: str,
    system_prompt: str,
    max_frames: int = 2
) -> Dict[str, Any]:
    """
    Call LLM with optional vision enhancement.
    Only uses images if available and cost-effective.
    """
    from retrieval.prompt import build_user_prompt
    
    # Get frames for top context only (cost optimization)
    top_context = contexts[0] if contexts else {}
    frames = get_frames_for_item(top_context, frames_base_dir)[:max_frames]
    
    # Build text prompt
    text_prompt = build_user_prompt(question, contexts)
    
    # Prepare messages
    messages = [{"role": "system", "content": system_prompt}]
    
    user_content = []
    
    # Add images if available
    if frames:
        for frame_path in frames:
            try:
                b64 = base64.b64encode(frame_path.read_bytes()).decode("utf-8")
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                })
            except Exception as e:
                print(f"Warning: Could not read frame {frame_path}: {e}")
    
    # Add text prompt
    user_content.append({"type": "text", "text": text_prompt})
    
    messages.append({"role": "user", "content": user_content})
    
    # Call API
    headers = {"Authorization": f"Bearer {api_key}"}
    model_name = "gpt-4o-mini"  # Supports vision
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 16000,
    }
    
    resp = httpx.post(api_url, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()
    data = resp.json()
    
    if "choices" in data:
        choice = data["choices"][0]
        content = choice["message"]["content"]
        
        # Try to parse as JSON
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Return as dict with content in all fields
            return {
                "direct": content,
                "step_by_step": content,
                "intuitive": content,
                "shortcut": content
            }
    
    return data

