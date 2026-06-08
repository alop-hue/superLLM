Adapter & Provider Integration Guide

This document describes the local "provider" adapters added to superLLM:
- Ollama (`:ollama`) — local Ollama-like servers
- OpenClaw (`:openclaw`) — OpenClaw-style servers
- OpenCode (`:opencode`) — OpenCode-style servers

Overview

- The router supports provider suffixes on model names. Example: `llama-2-13b:ollama` will route to the Ollama adapter.
- Each adapter tries to use a native Python client first (if installed) and falls back to an HTTP endpoint (configurable `base_url`).
- Provider types were added to the settings enum: `ollama`, `openclaw`, `opencode`. You can also add providers to the DB using the API.

Adding a provider via API

1) Example curl to add an Ollama provider:

```bash
curl -X POST http://localhost:8080/api/providers -H "Content-Type: application/json" -d '{
  "name": "local-ollama",
  "provider_type": "ollama",
  "base_url": "http://localhost:11434",
  "default_model": "llama-2-13b",
  "is_enabled": true,
  "priority": 10,
  "config": {}
}'
```

2) For OpenClaw/OpenCode, replace `provider_type` and `base_url` accordingly.

Using suffixes directly

- Call the API/CLI with a model name that includes the suffix:
  - `some-model-name:ollama`
  - `some-model-name:openclaw`
  - `some-model-name:opencode`

The router strips the suffix and forwards the request to the correct adapter.

Adapter configuration & defaults

- Ollama default base URL: `http://localhost:11434`
- OpenClaw default base URL: `http://localhost:11435`
- OpenCode default base URL: `http://localhost:11436`

If you run a local service on a different port, register a provider or pass the model name suffixed and add a provider record via the API.

Developer setup & tests

1) Create and activate venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install minimal test and runtime dependencies (examples):

```bash
pip install -e .[local]   # for local llama-cpp runtime, optional
pip install -e .[cloud]   # for litellm/cloud
# or for lightweight testing
pip install pydantic pydantic-settings pytest pytest-asyncio httpx
```

3) Run the test suite:

```bash
python -m pytest
```

Notes

- The adapters are minimal, intended to be compatible with most Ollama/OpenClaw-like HTTP servers. If your server exposes a different endpoint or payload format, adjust the adapter's `chat()`/`chat_stream()` implementations accordingly.
- For production use, implement authentication and secure the provider endpoints (API keys, TLS).

