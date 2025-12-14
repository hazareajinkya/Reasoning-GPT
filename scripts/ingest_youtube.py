"""
Lightweight YouTube ingestion helper.
- Downloads video audio/stream with yt-dlp.
- Extracts frames every N seconds via ffmpeg.
- Saves transcript if available.

Prereqs:
- ffmpeg installed on PATH.
- python -m pip install -r requirements.txt
"""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL


def download_video(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "format": "mp4/bestaudio/best",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = Path(ydl.prepare_filename(info))
    return filename


def extract_transcript(url: str) -> dict | None:
    """Pull auto-captions via yt-dlp; returns None if unavailable."""
    try:
        with YoutubeDL({"writesubtitles": True, "writeautomaticsub": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get("subtitles") or info.get("automatic_captions") or {}
            # Pick english-ish track if present.
            for key in ("en", "en-US", "en-GB"):
                if key in subs:
                    return {"url": url, "language": key, "tracks": subs[key]}
    except Exception:
        return None
    return None


def extract_frames(video_path: Path, out_dir: Path, every_seconds: int = 2) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        f"fps=1/{every_seconds}",
        str(out_dir / "frame_%05d.jpg"),
        "-hide_banner",
        "-loglevel",
        "error",
    ]
    subprocess.run(cmd, check=True)
    return sorted(out_dir.glob("frame_*.jpg"))


def main():
    parser = argparse.ArgumentParser(description="Download YT, extract transcript and frames.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--every-seconds", type=int, default=2)
    parser.add_argument("--out", type=Path, default=Path("data/raw"))
    args = parser.parse_args()

    video_out = args.out / "videos"
    frames_out = args.out / "frames"
    meta_out = args.out / "meta"

    video_path = download_video(args.url, video_out)
    frames = extract_frames(video_path, frames_out / video_path.stem, args.every_seconds)
    transcript = extract_transcript(args.url)

    meta_out.mkdir(parents=True, exist_ok=True)
    meta_file = meta_out / f"{video_path.stem}.json"
    meta = {"url": args.url, "video_path": str(video_path), "frames_dir": str(frames_out / video_path.stem), "transcript": transcript}
    meta_file.write_text(json.dumps(meta, indent=2))

    print(f"Downloaded: {video_path}")
    print(f"Frames: {len(frames)} -> {frames_out / video_path.stem}")
    print(f"Meta: {meta_file}")


if __name__ == "__main__":
    main()

