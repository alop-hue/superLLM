#!/bin/bash
# superLLM Quick Start Script
# Run this to get started with superLLM in local mode

set -e

echo "=== superLLM Quick Start ==="
echo ""

# 1. Install
echo "Step 1: Installing superLLM..."
pip install -e ".[local]" 2>/dev/null || pip install -e .
echo ""

# 2. Initialize
echo "Step 2: Initializing..."
superllm init
echo ""

# 3. Start server (background)
echo "Step 3: Starting server..."
superllm start --debug &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
sleep 2
echo ""

# 4. Download a small model
echo "Step 4: Downloading a small model for testing..."
superllm pull qwen2.5-0.5b
echo ""

# 5. Check status
echo "Step 5: Checking status..."
superllm status
echo ""

# 6. Test the API
echo "Step 6: Testing the API..."
curl -s http://localhost:8080/api/health | python3 -m json.tool
echo ""

echo "=== Done! ==="
echo ""
echo "Web UI: http://localhost:8080"
echo "API: http://localhost:8080/v1/chat/completions"
echo ""
echo "To stop: kill $SERVER_PID"
