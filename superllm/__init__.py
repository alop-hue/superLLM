__version__ = "0.2.0"

from superllm.config.settings import LogLevel, Mode, ProviderType, RouterStrategy, Settings

settings = Settings()

__all__ = [
    "__version__",
    "settings",
    "Settings",
    "Mode",
    "ProviderType",
    "RouterStrategy",
    "LogLevel",
]
