#!/bin/bash
# Quick monitoring script for vision extraction process

cd "/Users/ajinkya642000/Desktop/Reasoning GPT"

echo "=== VISION EXTRACTION MONITOR ==="
echo ""

# Check if process is running
if ps aux | grep "vision_extract.py" | grep -v grep > /dev/null; then
    PID=$(ps aux | grep "vision_extract.py" | grep -v grep | awk '{print $2}')
    echo "✓ Status: RUNNING (PID: $PID)"
else
    echo "✗ Status: NOT RUNNING"
    exit 0
fi

echo ""

# Progress - check both file and log
if [ -f "data/drafts/rdleefuXHQk_drafts.jsonl" ]; then
    file_count=$(wc -l < data/drafts/rdleefuXHQk_drafts.jsonl | tr -d ' ')
    # Try to get current batch from log
    log_batch=$(grep -o "Processing batch [0-9]*" vision_extract.log 2>/dev/null | tail -1 | grep -o "[0-9]*" || echo "0")
    if [ "$log_batch" -gt "$file_count" ]; then
        completed=$log_batch
        echo "Note: Processing batch $log_batch (file has $file_count saved - may be buffering)"
    else
        completed=$file_count
    fi
    total=619
    if [ $total -gt 0 ]; then
        percent=$((completed * 100 / total))
        remaining=$((total - completed))
        echo "Progress: ~$completed / $total batches ($percent%)"
        echo "Remaining: ~$remaining batches"
        echo "Estimated time left: ~$((remaining * 5 / 60)) minutes"
    fi
else
    echo "Progress: No output file yet"
fi

echo ""

# Recent log activity
echo "=== RECENT ACTIVITY (last 5 lines) ==="
tail -5 vision_extract.log 2>/dev/null || echo "No log file yet"

echo ""
echo "Run this script anytime: ./monitor_extraction.sh"

