from __future__ import annotations

import enum
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Mode(str, enum.Enum):
    local = "local"
    cloud = "cloud"
    hybrid = "hybrid"


class ProviderType(str, enum.Enum):
    local = "local"
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    deepseek = "deepseek"
    openrouter = "openrouter"
    mistral = "mistral"
    cohere = "cohere"
    xai = "xai"
    fireworks = "fireworks"
    aws_bedrock = "aws_bedrock"
    azure = "azure"
    together = "together"
    groq = "groq"
    ollama = "ollama"
    openclaw = "openclaw"
    opencode = "opencode"
    custom = "custom"


class RouterStrategy(str, enum.Enum):
    auto = "auto"
    task = "task"
    local_first = "local_first"
    cloud_first = "cloud_first"
    local_only = "local_only"
    cloud_only = "cloud_only"


class LogLevel(str, enum.Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="superllm_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    mode: Mode = Mode.local
    debug: bool = False
    log_level: LogLevel = LogLevel.info

    # Server
    host: str = "127.0.0.1"
    port: int = 8080
    cors_origins: list[str] = ["*"]

    # Paths
    data_dir: Path = Field(
        default_factory=lambda: Path(os.environ.get("SUPERLLM_DATA_DIR", Path.home() / ".superllm"))
    )
    models_dir: Path = Field(
        default_factory=lambda: Path(
            os.environ.get("SUPERLLM_MODELS_DIR") or str(Path.home() / ".superllm" / "models")
        )
    )
    config_file: Path | None = None

    # Local inference
    local_inference: bool = True
    local_model_timeout: int = 300
    local_max_tokens: int = 4096
    local_n_ctx: int = 2048
    local_n_gpu_layers: int = 0
    local_n_threads: int | None = None
    local_verbose: bool = False

    # Cloud
    cloud_routing: bool = False
    cloud_fallback: bool = True
    cloud_request_timeout: int = 120

    # Smart Router
    router_strategy: RouterStrategy = RouterStrategy.task
    router_task_classification: bool = True
    router_max_ram_gb: float = 32.0
    router_auto_fallback: bool = True

    # Agent config
    agent_max_iterations: int = 10
    agent_default_model: str = "auto"
    agent_memory_max_messages: int = 50
    agent_tool_timeout: int = 30

    # Audio config
    audio_enabled: bool = True
    audio_whisper_model: str = "small"
    audio_device: str = "cpu"
    audio_compute_type: str = "int8"
    audio_tts_model: str = "bark"
    audio_sample_rate: int = 24000

    # Performance
    model_cache_enabled: bool = True
    model_cache_max_gb: float = 8.0
    model_lazy_load: bool = True
    model_max_gpu_layers: int = 0
    model_streaming_chunk_size: int = 1

    # Auth
    auth_enabled: bool = False
    api_key: str | None = None
    jwt_secret: str | None = None

    # UI
    ui_enabled: bool = True
    ui_dev_mode: bool = False
    ui_port: int = 5173

    # Hugging Face
    hf_token: str | None = None
    hf_username: str | None = None

    # Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None

    # Storage
    database_url: str = Field(
        default_factory=lambda: f"sqlite+aiosqlite:///{Path.home() / '.superllm' / 'superllm.db'}"
    )

    # Model defaults
    default_model: str = "llama-3.2-1b"
    model_pull_timeout: int = 600

    def ensure_dirs(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
