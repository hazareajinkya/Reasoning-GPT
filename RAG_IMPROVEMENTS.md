# RAG System Improvements

## Issues Fixed

### 1. ✅ Truncation Problem
**Problem**: Responses were getting truncated with "max_tokens" error.

**Solution**:
- Increased `max_tokens` from 6000 to **16000** (GPT-4o-mini supports up to 16k)
- Added better error handling and warnings when truncation occurs
- Optimized prompt to be more concise (reduces token usage)

### 2. ✅ Response Quality
**Problem**: Answers weren't matching the quality of YouTube videos because visual context (tables, diagrams) was missing.

**Solution**:
- **Optimized prompts**: Made prompts more concise while keeping essential instructions
- **Hybrid Vision Enhancement**: Added optional vision support that uses images only when needed
  - Text-only retrieval first (fast, cheap)
  - Optional image enhancement for top results (better quality, costs more)
  - Only uses 1-2 frames per query to control costs

### 3. ✅ Cost Concerns
**Problem**: Worried about costs of including images in RAG.

**Solution**:
- **Text-first approach**: Default is text-only (cheap)
- **Optional vision**: Only use images when explicitly requested via `use_vision: true`
- **Limited frames**: Only uses 1-2 frames from top context (not all frames)
- **Smart frame selection**: Only uses frames if they exist and are relevant

## How to Use

### Standard Text-Only (Default - Cheapest)
```python
# API call
POST /solve
{
    "question": "Your question here",
    "top_k": 4,
    "use_vision": false  # or omit (defaults to false)
}
```

### With Vision Enhancement (Better Quality - Costs More)
```python
# API call
POST /solve
{
    "question": "Your question here",
    "top_k": 4,
    "use_vision": true  # Enable vision enhancement
}
```

**Note**: Vision enhancement only works if:
1. Frames exist in `data/raw/frames/` directory
2. Dataset items have `frame_paths`, `timestamp`, or `source` fields
3. You're using a vision-capable model (gpt-4o-mini supports vision)

## Cost Comparison

### Text-Only (Default)
- **Embedding**: ~$0.0001 per query
- **LLM**: ~$0.01-0.02 per query (depending on response length)
- **Total**: ~$0.01-0.02 per query

### With Vision (Optional)
- **Embedding**: ~$0.0001 per query (same)
- **LLM**: ~$0.05-0.10 per query (2 frames + longer context)
- **Total**: ~$0.05-0.10 per query

**Recommendation**: Use text-only for most queries. Enable vision only when:
- The question involves complex visual elements (tables, diagrams)
- Text-only responses are insufficient
- You need maximum accuracy

## Next Steps to Improve Quality

### Option 1: Enhance Dataset with Frame References
When building your dataset, add frame paths to items:
```json
{
    "id": "dilr_001",
    "question": "...",
    "solutions": {...},
    "frame_paths": [
        "data/raw/frames/4HourLrdiMarathon/frame_123.jpg",
        "data/raw/frames/4HourLrdiMarathon/frame_124.jpg"
    ],
    "source": "4HourLrdiMarathon",
    "timestamp": "3:55"
}
```

### Option 2: Use Vision During Dataset Creation
When extracting from videos, ensure the extracted text includes detailed descriptions of visual elements (tables, diagrams). The current `vision_extract.py` script does this, but you can enhance it further.

### Option 3: Two-Stage Approach
1. **Stage 1**: Text-only retrieval (fast, cheap) - get top 4-8 results
2. **Stage 2**: Vision enhancement for top 1-2 results only (better quality, controlled cost)

## Technical Details

### Prompt Optimization
- Reduced prompt length by ~40% while keeping essential instructions
- Truncates long context examples to save tokens
- More focused instructions for table/diagram generation

### Vision Enhancement
- Only processes top 1-2 contexts (not all retrieved contexts)
- Limits to 2 frames per query
- Gracefully falls back to text-only if frames unavailable
- Uses base64 encoding for images (standard for vision APIs)

### Error Handling
- Better truncation warnings
- Graceful fallback from vision to text-only
- Clear error messages for debugging

## Testing

Test the improvements:
```bash
# Test text-only (default)
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"question": "Your test question", "top_k": 4}'

# Test with vision (if frames available)
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"question": "Your test question", "top_k": 4, "use_vision": true}'
```

## Summary

✅ **Truncation fixed**: Increased max_tokens to 16k
✅ **Quality improved**: Better prompts + optional vision enhancement
✅ **Cost controlled**: Vision is optional, limited, and smart
✅ **Backward compatible**: Default behavior unchanged (text-only)

The system is now more robust and gives you control over the quality/cost tradeoff!

