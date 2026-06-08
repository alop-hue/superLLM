# superLLM

**Local-first and cloud-capable AI platform.** Run, manage, and serve models locally or in the cloud.

superLLM is not just a router to external providers — it is the actual system that serves models through its own API, manages its own model library, and runs inference locally or in the cloud.

## Features

- **Local Mode** — Run models entirely on your machine. No cloud dependency.
- **Cloud Mode** — Deploy the same stack to a server for production.
- **Hybrid Mode** — Local-first routing with automatic cloud fallback.
- **OpenAI-Compatible API** — Drop-in replacement for OpenAI clients.
- **Rich CLI** — All operations available from the terminal.
- **Web UI** — Modern interface on `localhost`.
- **Provider Abstraction** — Local, OpenAI, Anthropic, and more.
- **Model Library** — Searchable catalog of 10+ pre-configured models.
- **Conversation History** — Persistent chat storage.
- **Smart Routing** — Auto, local-first, cloud-first, fallback strategies.

## Quick Start

```bash
# Install from source
git clone https://github.com/superllm/superllm.git
cd superllm
pip install -e .

# For local inference (llama-cpp-python)
pip install -e ".[local]"

# For cloud routing (litellm)
pip install -e ".[cloud]"

# Initialize
superllm init

# Start the server
superllm start

# Open the UI
open http://localhost:8080

# Download a model
superllm pull llama-3.2-1b

# List installed models
superllm list

# Show model details
superllm show llama-3.2-1b
```
## Download the project as command tool

```
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/alop-hue/superLLM/main/install.sh | sh

# Windows (PowerShell)
irm https://raw.githubusercontent.com/alop-hue/superLLM/main/install.ps1 | iex
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `superllm init` | Initialize configuration and directories |
| `superllm start` | Start the API server (with optional web UI) |
| `superllm serve` | Alias for start |
| `superllm stop` | Stop the server |
| `superllm status` | Show server status and diagnostics |
| `superllm doctor` | Run system diagnostics |
| `superllm pull <model>` | Download a model from the library |
| `superllm remove <model>` | Delete an installed model |
| `superllm list` | List installed models |
| `superllm show <model>` | Show detailed model information |
| `superllm library` | Browse the model library |
| `superllm providers` | Manage inference providers |
| `superllm config` | Get/set configuration values |
| `superllm logs` | View server logs |
| `superllm login` | Login to superLLM cloud |
| `superllm logout` | Logout from superLLM cloud |

## API

superLLM exposes an OpenAI-compatible API:

```bash
# Chat completion
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.2-1b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'

# List models
curl http://localhost:8080/api/models

# Health check
curl http://localhost:8080/api/health
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    CLI (Typer)                    │
├─────────────────────────────────────────────────┤
│                 FastAPI Server                    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌───────────────┐  │
│  │ Chat │ │Models│ │Config│ │ Conversations │  │
│  └──────┘ └──────┘ └──────┘ └───────────────┘  │
├─────────────────────────────────────────────────┤
│              Inference Router                     │
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │ Local (llama.cpp) │  │ Cloud (LiteLLM)     │  │
│  └─────────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Model Registry  │  Provider Registry  │ Storage │
├─────────────────────────────────────────────────┤
│           SQLite (local) / PostgreSQL (cloud)    │
└─────────────────────────────────────────────────┘
```

## Project Structure

```
superllm/
├── superllm/           # Python package
│   ├── cli/           # CLI commands
│   ├── server/        # API server routes
│   ├── inference/     # Inference engines
│   ├── providers/     # Provider abstraction
│   ├── models/        # Model registry & library
│   ├── storage/       # Database layer
│   ├── config/        # Settings
│   └── ui/            # UI server
├── ui/                 # React frontend
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Usage examples
```

## Modes

### Local Mode
- Runs entirely on your machine
- Models downloaded and executed locally
- No internet required after initial download
- CPU and GPU support via llama.cpp
- Ideal for development, testing, and offline use

### Cloud Mode
- Deploy to any server or cloud GPU instance
- Full multi-user support with auth
- API key management
- Rate limiting and quotas
- Production-ready for team use

### Hybrid Mode
- Local models preferred, cloud fallback when unavailable
- Smart routing: auto, local-first, cloud-first
- Transparent failover between providers

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start in development mode
superllm start --debug

# Develop the UI
cd ui && npm install && npm run dev
```

## License

MIT
