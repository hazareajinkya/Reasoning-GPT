"""
Merge all LRDI/DILR datasets into one combined file.
"""

import json
from pathlib import Path


def merge_datasets():
    """Merge all LRDI seed files into one combined dataset."""
    
    # LRDI datasets to merge
    datasets = [
        "data/seed_lrdi.jsonl",  # 4-hour marathon
        "data/seed_lrdi_6hour.jsonl",  # 6-hour marathon
        "data/seed_LrdiRef1.jsonl",
        "data/seed_LrdiRef2.jsonl",
        "data/seed_LrdiRef3.jsonl",
        "data/seed_LrdiRef4.jsonl",
    ]
    
    output_file = Path("data/seed_dilr.jsonl")
    all_problems = []
    
    print("Merging LRDI datasets...")
    print("=" * 80)
    
    for dataset_path in datasets:
        path = Path(dataset_path)
        if not path.exists():
            print(f"⚠️  {path.name}: Not found, skipping")
            continue
        
        count = 0
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        problem = json.loads(line)
                        # Update ID to include source for tracking
                        original_id = problem.get('id', 'unknown')
                        source = path.stem.replace('seed_', '')
                        problem['id'] = f"dilr_{original_id}" if not original_id.startswith('dilr_') else original_id
                        problem['source'] = source
                        all_problems.append(problem)
                        count += 1
                    except Exception as e:
                        print(f"⚠️  Error parsing line in {path.name}: {e}")
                        continue
        
        print(f"✅ {path.name}: {count} problems")
    
    # Write merged dataset
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        for problem in all_problems:
            f.write(json.dumps(problem) + "\n")
    
    print()
    print("=" * 80)
    print(f"✅ Merged {len(all_problems)} problems into {output_file}")
    print("=" * 80)
    
    # Show breakdown by source
    from collections import Counter
    sources = Counter([p.get('source', 'unknown') for p in all_problems])
    print("\nBreakdown by source:")
    for source, count in sorted(sources.items()):
        print(f"  • {source}: {count} problems")
    
    return output_file


if __name__ == "__main__":
    merge_datasets()

