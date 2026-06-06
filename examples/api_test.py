#!/usr/bin/env python3
"""Example: Test the superLLM API with a chat completion request."""

import httpx
import json

BASE_URL = "http://localhost:8080"
MODEL = "llama-3.2-1b"


def chat_completion():
    """Send a chat completion request to superLLM."""
    response = httpx.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What can you do?"},
            ],
            "temperature": 0.7,
            "max_tokens": 200,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    print("Response:")
    print(json.dumps(data, indent=2))
    print(f"\nAssistant: {data['choices'][0]['message']['content']}")


def stream_chat():
    """Send a streaming chat completion request."""
    print("\nStreaming response:")
    with httpx.stream(
        "POST",
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "Count from 1 to 5."},
            ],
            "stream": True,
        },
        timeout=30,
    ) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        print(content, end="", flush=True)
                except json.JSONDecodeError:
                    pass
    print()


def list_models():
    """List available models."""
    response = httpx.get(f"{BASE_URL}/api/models", timeout=10)
    response.raise_for_status()
    data = response.json()
    print(f"\nInstalled models ({len(data['models'])}):")
    for m in data["models"]:
        print(f"  - {m['name']} ({m.get('size_display', '?')})")


def health_check():
    """Check server health."""
    response = httpx.get(f"{BASE_URL}/api/health", timeout=5)
    response.raise_for_status()
    data = response.json()
    print(f"Health: {data['status']} (mode: {data['mode']})")


if __name__ == "__main__":
    print("=== superLLM API Test ===")
    print(f"Server: {BASE_URL}")
    print(f"Model: {MODEL}")
    print()

    try:
        health_check()
        list_models()
        chat_completion()
        stream_chat()
    except httpx.ConnectError:
        print(f"Error: Could not connect to superLLM at {BASE_URL}")
        print("Make sure the server is running: superllm start")
    except Exception as e:
        print(f"Error: {e}")
