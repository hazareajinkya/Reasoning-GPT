#!/usr/bin/env python3
"""Simple test to check if OpenAI API is working"""
import httpx
import json
import sys

api_url = "https://api.openai.com/v1/chat/completions"
if len(sys.argv) < 2:
    print("Usage: python3 test_api_simple.py <API_KEY>")
    print("Error: API key required as command-line argument")
    sys.exit(1)
api_key = sys.argv[1]

headers = {"Authorization": f"Bearer {api_key}"}

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "user", "content": "Say 'API is working' if you can read this."}
    ],
    "max_tokens": 10,
}

print("Testing API connection...")
try:
    resp = httpx.post(api_url, headers=headers, json=payload, timeout=30)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 429:
        print("❌ RATE LIMITED")
        print(f"Headers: {dict(resp.headers)}")
        retry_after = resp.headers.get("retry-after")
        if retry_after:
            print(f"Wait {retry_after} seconds")
    elif resp.status_code == 200:
        result = resp.json()
        print(f"✅ SUCCESS: {result['choices'][0]['message']['content']}")
        print(f"Remaining RPM: {resp.headers.get('x-ratelimit-remaining-requests', '?')}")
        print(f"Remaining TPM: {resp.headers.get('x-ratelimit-remaining-tokens', '?')}")
    else:
        print(f"❌ ERROR: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")



