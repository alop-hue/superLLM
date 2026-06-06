.PHONY: install install-local install-cloud install-all dev test lint clean build run stop

# Installation
install:
	pip install -e .

install-local:
	pip install -e ".[local]"

install-cloud:
	pip install -e ".[cloud]"

install-all:
	pip install -e ".[all]"

install-dev:
	pip install -e ".[dev]"

# Development
dev:
	superllm start --debug

run:
	superllm start

stop:
	superllm stop

status:
	superllm status

doctor:
	superllm doctor

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=superllm --cov-report=term

# Linting & formatting
lint:
	ruff check superllm/ tests/

format:
	ruff format superllm/ tests/

typecheck:
	mypy superllm/ --ignore-missing-imports

# Clean up
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

# Build
build:
	pip install build
	rm -rf dist/
	python -m build

# Publish (requires PyPI credentials)
publish: build
	pip install twine
	twine upload dist/*

# UI Development
ui-dev:
	cd ui && npm run dev

ui-build:
	cd ui && npm install && npm run build

# Initialize a new project
init:
	superllm init

# Full setup from scratch
setup: init install-all
	@echo "superLLM setup complete!"
