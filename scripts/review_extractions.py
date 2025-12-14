"""
Review script to analyze extracted problems from all videos.
Shows summary, best problems, and statistics.
"""

import json
from pathlib import Path
from collections import defaultdict

def extract_problem_info(content: str) -> dict:
    """Extract key information from content."""
    info = {
        "has_question": any(kw in content.lower() for kw in ["question", "problem", "after how", "if ratio"]),
        "has_data": any(kw in content.lower() for kw in ["120", "m/s", "speed", "circumference", "diameter", "km/h"]),
        "has_solution": any(kw in content.lower() for kw in ["solution", "step", "calculate", "formula", "answer"]),
        "has_formula": any(kw in content.lower() for kw in ["p+q", "p-q", "lcm", "relative speed", "ratio"]),
    }
    return info

def review_draft_file(draft_file: Path) -> dict:
    """Review a single draft file and extract statistics."""
    if not draft_file.exists():
        return None
    
    stats = {
        "total_entries": 0,
        "transcript_entries": 0,
        "frame_entries": 0,
        "problems_with_question": 0,
        "problems_with_data": 0,
        "problems_with_solution": 0,
        "best_problems": [],
        "concepts_found": set(),
    }
    
    with open(draft_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                stats["total_entries"] += 1
                
                if data.get("type") == "transcript":
                    stats["transcript_entries"] += 1
                elif data.get("type") == "frame":
                    stats["frame_entries"] += 1
                
                content = data.get("draft", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                info = extract_problem_info(content)
                
                if info["has_question"]:
                    stats["problems_with_question"] += 1
                if info["has_data"]:
                    stats["problems_with_data"] += 1
                if info["has_solution"]:
                    stats["problems_with_solution"] += 1
                
                # Track concepts
                if "ratio" in content.lower() and ("p:q" in content.lower() or "p+q" in content.lower()):
                    stats["concepts_found"].add("Speed Ratio (P:Q)")
                if "relative speed" in content.lower():
                    stats["concepts_found"].add("Relative Speed")
                if "lcm" in content.lower() or "least common multiple" in content.lower():
                    stats["concepts_found"].add("LCM")
                if "meet" in content.lower() and ("starting" in content.lower() or "point" in content.lower()):
                    stats["concepts_found"].add("Meeting at Starting Point")
                if "opposite direction" in content.lower() or "same direction" in content.lower():
                    stats["concepts_found"].add("Direction-based Problems")
                
                # Collect best problems (those with question + data)
                if info["has_question"] and info["has_data"]:
                    frame_name = data.get("frame", "transcript")
                    snippet = content[:300].replace("\n", " ")
                    stats["best_problems"].append({
                        "source": frame_name,
                        "snippet": snippet,
                        "full_content": content[:500] if len(content) > 500 else content
                    })
                    
            except Exception as e:
                continue
    
    return stats

def main():
    drafts_dir = Path("data/drafts")
    video_files = [
        "rdleefuXHQk_drafts.jsonl",
        "7-MKc9p6AwU_drafts.jsonl",
        "hkNVVMX06FE_drafts.jsonl",
        "v8kBd64_WAc_drafts.jsonl",
    ]
    
    print("=" * 80)
    print("📊 EXTRACTION REVIEW - CIRCULAR TRACKS TOPIC")
    print("=" * 80)
    print()
    
    all_stats = {}
    all_best_problems = []
    
    for video_file in video_files:
        draft_file = drafts_dir / video_file
        video_id = video_file.replace("_drafts.jsonl", "")
        
        print(f"📹 Video: {video_id}")
        print("-" * 80)
        
        stats = review_draft_file(draft_file)
        if not stats:
            print("  ⚠️  File not found")
            print()
            continue
        
        all_stats[video_id] = stats
        all_best_problems.extend([(video_id, p) for p in stats["best_problems"]])
        
        print(f"  Total entries: {stats['total_entries']}")
        print(f"    • Transcripts: {stats['transcript_entries']}")
        print(f"    • Frames: {stats['frame_entries']}")
        print()
        print(f"  Problems found:")
        print(f"    • With question: {stats['problems_with_question']}")
        print(f"    • With data: {stats['problems_with_data']}")
        print(f"    • With solution: {stats['problems_with_solution']}")
        print()
        
        if stats["concepts_found"]:
            print(f"  Concepts identified:")
            for concept in sorted(stats["concepts_found"]):
                print(f"    • {concept}")
        print()
    
    # Overall summary
    print("=" * 80)
    print("📈 OVERALL SUMMARY")
    print("=" * 80)
    total_entries = sum(s["total_entries"] for s in all_stats.values())
    total_problems = sum(s["problems_with_question"] for s in all_stats.values())
    total_with_data = sum(s["problems_with_data"] for s in all_stats.values())
    
    print(f"Total entries extracted: {total_entries}")
    print(f"Problems with questions: {total_problems}")
    print(f"Problems with data: {total_with_data}")
    print()
    
    # Show best problems
    print("=" * 80)
    print("🎯 BEST PROBLEMS (Question + Data)")
    print("=" * 80)
    print()
    
    for idx, (video_id, problem) in enumerate(all_best_problems[:10], 1):
        print(f"Problem #{idx} - {video_id} ({problem['source']})")
        print("-" * 80)
        print(problem["snippet"])
        print()
    
    if len(all_best_problems) > 10:
        print(f"... and {len(all_best_problems) - 10} more problems")
        print()
    
    print("=" * 80)
    print("✅ Review complete! Ready for formatting into dataset.")
    print("=" * 80)

if __name__ == "__main__":
    main()


