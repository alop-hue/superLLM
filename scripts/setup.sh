#!/bin/bash
# superLLM Development Setup
set -e

echo "=== superLLM Development Setup ==="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION >= 3.10" | bc -l) )); then
    echo "✓ Python $PYTHON_VERSION detected"
else
    echo "✗ Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install with all dependencies
echo "Installing superLLM with all dependencies..."
pip install --upgrade pip
pip install -e ".[all]"

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    pre-commit install 2>/dev/null || true
fi

# Setup UI
if [ -d "ui" ]; then
    echo "Setting up UI..."
    cd ui
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
fi

# Create config
echo "Initializing superLLM..."
superllm init

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Commands:"
echo "  superllm start     - Start the server"
echo "  superllm pull <m>  - Download a model"
echo "  superllm list      - List installed models"
echo "  pytest             - Run tests"
echo ""
echo "UI Development:"
echo "  cd ui && npm run dev"
