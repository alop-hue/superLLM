from __future__ import annotations

import enum
import os
from pathlib import Path
from typing import Optional

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
    aws_bedrock = "aws_bedrock"
    azure = "azure"
    together = "together"
    groq = "groq"
    custom = "custom"


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
        default_factory=lambda: Path(
            os.environ.get("SUPERLLM_DATA_DIR", Path.home() / ".superllm")
        )
    )
    models_dir: Path = Field(
        default_factory=lambda: Path(
            os.environ.get("SUPERLLM_MODELS_DIR")
            or str(Path.home() / ".superllm" / "models")
        )
    )
    config_file: Optional[Path] = None

    # Local inference
    local_inference: bool = True
    local_model_timeout: int = 300
    local_max_tokens: int = 4096
    local_n_ctx: int = 2048
    local_n_gpu_layers: int = 0
    local_n_threads: Optional[int] = None
    local_verbose: bool = False

    # Cloud
    cloud_routing: bool = False
    cloud_fallback: bool = True
    cloud_request_timeout: int = 120

    # Auth
    auth_enabled: bool = False
    api_key: Optional[str] = None
    jwt_secret: Optional[str] = None

    # UI
    ui_enabled: bool = True
    ui_dev_mode: bool = False
    ui_port: int = 5173

    # Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Storage
    database_url: str = Field(
        default_factory=lambda: (
            f"sqlite+aiosqlite:///{Path.home() / '.superllm' / 'superllm.db'}"
        )
    )

    # Model defaults
    default_model: str = "llama-3.2-1b"
    model_pull_timeout: int = 600

    def ensure_dirs(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
