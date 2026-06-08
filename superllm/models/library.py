from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModelCard:
    name: str
    display_name: str
    description: str
    architecture: str
    parameter_count: str
    context_length: int
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    capabilities: dict[str, bool] = field(
        default_factory=lambda: {
            "chat": False,
            "code": False,
            "reasoning": False,
            "embeddings": False,
            "vision": False,
            "audio": False,
            "agent": False,
        }
    )
    source: str = "local"
    provider: str | None = None
    recommended_ram: str | None = None
    size_estimates: dict[str, int] = field(default_factory=dict)
    quantizations: list[str] = field(default_factory=lambda: ["Q4_K_M", "Q5_K_M", "Q8_0"])
    url: str | None = None
    latency_profile: str = "interactive"
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    model_family: str = "default"
    hf_repo: str | None = None


def _make(
    name: str,
    display: str,
    desc: str,
    arch: str,
    params: str,
    ctx: int,
    category: str = "general",
    tags: list[str] = None,
    caps: dict[str, bool] = None,
    source: str = "local",
    provider: str = None,
    ram: str = None,
    sizes: dict[str, int] = None,
    quants: list[str] = None,
    url: str = None,
    latency: str = "interactive",
    strengths: list[str] = None,
    weaknesses: list[str] = None,
    family: str = "",
    hf_repo: str = None,
) -> ModelCard:
    if tags is None:
        tags = []
    if caps is None:
        caps = {
            "chat": False,
            "code": False,
            "reasoning": False,
            "embeddings": False,
            "vision": False,
            "audio": False,
            "agent": False,
        }
    if sizes is None:
        sizes = {}
    if quants is None:
        quants = ["Q4_K_M", "Q5_K_M", "Q8_0"]
    if strengths is None:
        strengths = []
    if weaknesses is None:
        weaknesses = []
    return ModelCard(
        name=name,
        display_name=display,
        description=desc,
        architecture=arch,
        parameter_count=params,
        context_length=ctx,
        category=category,
        tags=tags,
        capabilities=caps,
        source=source,
        provider=provider,
        recommended_ram=ram,
        size_estimates=sizes,
        quantizations=quants,
        url=url,
        latency_profile=latency,
        strengths=strengths,
        weaknesses=weaknesses,
        model_family=family or category,
        hf_repo=hf_repo,
    )


BUILTIN_LIBRARY: dict[str, ModelCard] = {}

# ============================================================
# VERIFIED MODELS (confirmed working download URLs)
# ============================================================

# --- Qwen 2.5 ---
for _n, _d, _a, _p, _c, _cat, _tags, _caps, _ram, _sizes, _u in [
    (
        "qwen2.5-0.5b",
        "Qwen 2.5 0.5B",
        "qwen2",
        "0.49B",
        32768,
        "chat",
        ["chat", "lightweight", "fast", "low-ram"],
        {"chat": True},
        "1 GB",
        {"Q4_K_M": 380_000_000, "Q8_0": 620_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
    ),
    (
        "qwen2.5-1.5b",
        "Qwen 2.5 1.5B",
        "qwen2",
        "1.54B",
        32768,
        "chat",
        ["chat", "lightweight", "fast"],
        {"chat": True, "code": True},
        "2 GB",
        {"Q4_K_M": 930_000_000, "Q8_0": 1_600_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
    ),
    (
        "qwen2.5-3b",
        "Qwen 2.5 3B",
        "qwen2",
        "3.0B",
        32768,
        "general",
        ["chat", "lightweight"],
        {"chat": True, "code": True},
        "4 GB",
        {"Q4_K_M": 1_800_000_000, "Q8_0": 3_200_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
    ),
    (
        "qwen2.5-7b",
        "Qwen 2.5 7B",
        "qwen2",
        "7.61B",
        32768,
        "general",
        ["chat", "code", "reasoning"],
        {"chat": True, "code": True, "reasoning": True},
        "8 GB",
        {"Q4_K_M": 4_600_000_000, "Q5_K_M": 5_600_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    ),
    (
        "qwen2.5-14b",
        "Qwen 2.5 14B",
        "qwen2",
        "14.8B",
        32768,
        "general",
        ["chat", "code", "reasoning"],
        {"chat": True, "code": True, "reasoning": True},
        "16 GB",
        {"Q4_K_M": 8_900_000_000, "Q5_K_M": 10_800_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF/resolve/main/Qwen2.5-14B-Instruct-Q4_K_M.gguf",
    ),
    (
        "qwen2.5-32b",
        "Qwen 2.5 32B",
        "qwen2",
        "32.8B",
        32768,
        "general",
        ["chat", "code", "reasoning"],
        {"chat": True, "code": True, "reasoning": True},
        "32 GB",
        {"Q4_K_M": 19_800_000_000, "Q5_K_M": 24_000_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-32B-Instruct-GGUF/resolve/main/Qwen2.5-32B-Instruct-Q4_K_M.gguf",
    ),
    (
        "qwen2.5-72b",
        "Qwen 2.5 72B",
        "qwen2",
        "72.7B",
        32768,
        "general",
        ["chat", "code", "reasoning"],
        {"chat": True, "code": True, "reasoning": True},
        "64 GB",
        {"Q4_K_M": 43_000_000_000, "Q5_K_M": 52_000_000_000},
        "https://huggingface.co/bartowski/Qwen2.5-72B-Instruct-GGUF/resolve/main/Qwen2.5-72B-Instruct-Q4_K_M.gguf",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        f"Alibaba's {_d.split()[-1]}.",
        _a,
        _p,
        _c,
        _cat,
        _tags,
        _caps,
        ram=_ram,
        sizes=_sizes,
        url=_u,
    )

# --- Llama 3.1 ---
for _n, _d, _p, _sizes, _u in [
    (
        "llama3.1-8b",
        "Llama 3.1 8B",
        "8.03B",
        {"Q4_K_M": 4_900_000_000, "Q5_K_M": 6_000_000_000},
        "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    ),
    (
        "llama3.1-70b",
        "Llama 3.1 70B",
        "70.6B",
        {"Q4_K_M": 42_000_000_000, "Q5_K_M": 51_000_000_000},
        "https://huggingface.co/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        f"Meta's {_d.split()[-1]}.",
        "llama",
        _p,
        131072,
        "general",
        ["chat", "code", "reasoning"],
        {"chat": True, "code": True, "reasoning": True},
        ram="64 GB" if "70" in _n else "8 GB",
        sizes=_sizes,
        url=_u,
    )

# --- Llama 3.2 ---
for _n, _d, _p, _c, _ram, _sizes, _u in [
    (
        "llama3.2-1b",
        "Llama 3.2 1B",
        "1.24B",
        8192,
        "1 GB",
        {"Q4_K_M": 780_000_000, "Q8_0": 1_300_000_000},
        "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    ),
    (
        "llama3.2-3b",
        "Llama 3.2 3B",
        "3.21B",
        8192,
        "4 GB",
        {"Q4_K_M": 1_900_000_000, "Q8_0": 3_400_000_000},
        "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        f"Meta's tiny {_d.split()[-1]}.",
        "llama",
        _p,
        _c,
        "chat" if "1b" in _n else "general",
        ["chat", "lightweight", "fast"],
        {"chat": True},
        ram=_ram,
        sizes=_sizes,
        url=_u,
    )

# --- Llama 3 ---
for _n, _d, _p, _sizes, _u in [
    (
        "llama-3-8b",
        "Llama 3 8B",
        "8.03B",
        {"Q4_K_M": 4_900_000_000, "Q5_K_M": 6_000_000_000},
        "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
    ),
    (
        "llama-3-70b",
        "Llama 3 70B",
        "70.6B",
        {"Q4_K_M": 42_000_000_000, "Q5_K_M": 51_000_000_000},
        "https://huggingface.co/bartowski/Meta-Llama-3-70B-Instruct-GGUF/resolve/main/Meta-Llama-3-70B-Instruct-Q4_K_M.gguf",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        f"Meta's {_d.split()[-1]}.",
        "llama",
        _p,
        8192,
        "general",
        ["chat", "code", "reasoning"],
        {"chat": True, "code": True, "reasoning": True},
        ram="64 GB" if "70" in _n else "8 GB",
        sizes=_sizes,
        url=_u,
    )

# --- Mistral ---
BUILTIN_LIBRARY["mistral-7b"] = _make(
    "mistral-7b",
    "Mistral 7B",
    "Mistral AI's powerful 7B.",
    "mistral",
    "7.3B",
    32768,
    "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True},
    ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000},
    url="https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
)

BUILTIN_LIBRARY["mixtral-8x7b"] = _make(
    "mixtral-8x7b",
    "Mixtral 8x7B",
    "Mistral AI's MoE model.",
    "mixtral",
    "46.7B",
    32768,
    "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True},
    ram="32 GB",
    sizes={"Q4_K_M": 26_000_000_000, "Q5_K_M": 32_000_000_000},
    url="https://huggingface.co/bartowski/Mixtral-8x7B-Instruct-v0.1-GGUF/resolve/main/Mixtral-8x7B-Instruct-v0.1-Q4_K_M.gguf",
)

# --- Phi-3 ---
BUILTIN_LIBRARY["phi-3-mini"] = _make(
    "phi-3-mini",
    "Phi-3 Mini",
    "Microsoft's 3.8B model.",
    "phi",
    "3.8B",
    4096,
    "general",
    ["chat", "reasoning"],
    {"chat": True, "reasoning": True},
    ram="4 GB",
    sizes={"Q4_K_M": 2_300_000_000, "Q8_0": 4_000_000_000},
    url="https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf",
)

BUILTIN_LIBRARY["phi-3-medium"] = _make(
    "phi-3-medium",
    "Phi-3 Medium",
    "Microsoft's 14B model.",
    "phi",
    "14B",
    4096,
    "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True},
    ram="16 GB",
    sizes={"Q4_K_M": 8_400_000_000, "Q5_K_M": 10_200_000_000},
    url="https://huggingface.co/bartowski/Phi-3-medium-4k-instruct-GGUF/resolve/main/Phi-3-medium-4k-instruct-Q4_K_M.gguf",
)

# --- TinyLlama ---
BUILTIN_LIBRARY["tinyllama-1.1b"] = _make(
    "tinyllama-1.1b",
    "TinyLlama 1.1B",
    "Compact 1.1B model.",
    "tinyllama",
    "1.1B",
    2048,
    "chat",
    ["chat", "lightweight", "fast"],
    {"chat": True},
    ram="1 GB",
    sizes={"Q4_K_M": 660_000_000, "Q8_0": 1_200_000_000},
    url="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
)

# --- Audio Models ---
for _n, _d, _desc, _u in [
    (
        "whisper-large-v3",
        "Whisper Large v3",
        "OpenAI's speech-to-text.",
        "https://huggingface.co/ggerganov/whisper.cpp",
    ),
    (
        "whisper-small",
        "Whisper Small",
        "OpenAI's compact STT.",
        "https://huggingface.co/ggerganov/whisper.cpp",
    ),
    (
        "faster-whisper",
        "Faster Whisper",
        "Fast Whisper reimplementation.",
        "https://huggingface.co/guillaumeklf/faster-whisper-large-v3",
    ),
    ("bark", "Bark", "Suno's text-to-speech.", "https://huggingface.co/suno/bark"),
    ("xtts-v2", "XTTS v2", "Coqui's voice cloning TTS.", "https://huggingface.co/coqui/XTTS-v2"),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        _desc,
        _n.split("-")[0],
        "1.5B",
        224,
        "audio",
        ["audio", "speech"],
        {"audio": True},
        ram="4 GB",
        url=_u,
    )

# --- Agent Models ---
for _n, _d, _desc, _u in [
    (
        "hermes-2-pro",
        "Hermes 2 Pro",
        "Nous Research's function-calling model.",
        "https://huggingface.co/NousResearch/Hermes-2-Pro-Mistral-7B-GGUF",
    ),
    (
        "openchat-3.5",
        "OpenChat 3.5",
        "OpenChat's 7B.",
        "https://huggingface.co/openchat/openchat_3.5",
    ),
    (
        "openchat-3.6",
        "OpenChat 3.6",
        "OpenChat's 8B.",
        "https://huggingface.co/openchat/openchat-3.6-8B-20240522",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        _desc,
        "hermes" if "hermes" in _n else "openchat",
        "7B",
        32768,
        "agent",
        ["agent", "chat"],
        {"chat": True, "code": True, "agent": True},
        ram="8 GB",
        url=_u,
    )

# --- Vision Models (legacy) ---
for _n, _d, _p, _u in [
    ("llava-1.6", "LLaVA 1.6", "7B", "https://huggingface.co/liuhaotian/llava-v1.6-mistral-7b"),
    ("cogvlm", "CogVLM", "19B", "https://huggingface.co/THUDM/cogvlm2-llama3-chat-19B"),
    ("idefics2", "Idefics2", "8B", "https://huggingface.co/HuggingFaceM4/idefics2-8b"),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        f"Multimodal {_d}.",
        _n.split("-")[0],
        _p,
        8192,
        "vision",
        ["vision", "multimodal"],
        {"chat": True, "vision": True},
        ram="8 GB",
        url=_u,
    )

# --- Specialized ---
for _n, _d, _desc, _u in [
    (
        "sqlcoder",
        "SQLCoder",
        "Defog's text-to-SQL model.",
        "https://huggingface.co/defog/sqlcoder-7b-2",
    ),
    (
        "meditron-7b",
        "Meditron 7B",
        "EPFL's medical domain model.",
        "https://huggingface.co/epfl-llm/meditron-7b",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        _desc,
        _n.split("-")[0],
        "7B",
        4096,
        "specialized",
        ["specialized"],
        {"chat": True},
        ram="8 GB",
        url=_u,
    )

# ============================================================
# CLOUD MODELS
# ============================================================

for _n, _d, _desc, _provider in [
    ("qwen2.5-72b:cloud", "Qwen 2.5 72B (Cloud)", "Alibaba's 72B via cloud.", "together"),
    ("llama3.1-405b:cloud", "Llama 3.1 405B (Cloud)", "Meta's 405B via cloud.", "together"),
    ("gpt-4o:cloud", "GPT-4o (Cloud)", "OpenAI's flagship.", "openai"),
    ("gpt-4o-mini:cloud", "GPT-4o Mini (Cloud)", "OpenAI's cost-efficient.", "openai"),
    (
        "claude-3.5-sonnet:cloud",
        "Claude 3.5 Sonnet (Cloud)",
        "Anthropic's balanced model.",
        "anthropic",
    ),
    ("claude-3.5-haiku:cloud", "Claude 3.5 Haiku (Cloud)", "Anthropic's fast model.", "anthropic"),
    ("gemini-2.0-flash:cloud", "Gemini 2.0 Flash (Cloud)", "Google's fast multimodal.", "google"),
    ("deepseek-v3:cloud", "DeepSeek V3 (Cloud)", "DeepSeek's 671B MoE.", "together"),
    (
        "deepseek-r1-671b:cloud",
        "DeepSeek R1 671B (Cloud)",
        "DeepSeek's reasoning model.",
        "together",
    ),
    (
        "qwen3-thinking-max:cloud",
        "Qwen 3 Thinking Max (Cloud)",
        "Alibaba's thinking model.",
        "together",
    ),
]:
    BUILTIN_LIBRARY[_n] = _make(
        _n,
        _d,
        _desc,
        _n.split(":")[0],
        "unknown",
        131072,
        "general",
        ["chat", "code", "reasoning", "cloud"],
        {"chat": True, "code": True, "reasoning": True},
        source="cloud",
        provider=_provider,
        ram="Cloud",
    )

LITELLM_MODEL_MAP: dict[str, str] = {
    "gpt-4o:cloud": "openai/gpt-4o",
    "gpt-4o-mini:cloud": "openai/gpt-4o-mini",
    "claude-3.5-sonnet:cloud": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3.5-haiku:cloud": "anthropic/claude-3-5-haiku-20241022",
    "gemini-2.0-flash:cloud": "gemini/gemini-2.0-flash",
    "gemini-2.0-pro:cloud": "gemini/gemini-2.0-pro-exp-02-05",
    "deepseek-v3:cloud": "together_ai/deepseek-ai/DeepSeek-V3-0324",
    "deepseek-r1-671b:cloud": "together_ai/deepseek-ai/DeepSeek-R1",
    "qwen2.5-72b:cloud": "together_ai/Qwen/Qwen2.5-72B-Instruct-Turbo",
    "qwen3-thinking-max:cloud": "together_ai/Qwen/Qwen3-235B-A3B-Thinking-Max",
    "llama3.1-405b:cloud": "together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "mixtral-8x22b:cloud": "together_ai/mistralai/Mixtral-8x22B-Instruct-v0.1",
    "command-r-plus:cloud": "together_ai/CohereForAI/c4ai-command-r-plus",
    "gpt-4-turbo:cloud": "openai/gpt-4-turbo",
    "gpt-3.5-turbo:cloud": "openai/gpt-3.5-turbo",
    "claude-3-opus:cloud": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet:cloud": "anthropic/claude-3-sonnet-20240229",
    "claude-3-haiku:cloud": "anthropic/claude-3-haiku-20240307",
    "gemini-1.5-pro:cloud": "gemini/gemini-1.5-pro",
    "gemini-1.5-flash:cloud": "gemini/gemini-1.5-flash",
    "gemini-2.0-flash-lite:cloud": "gemini/gemini-2.0-flash-lite-preview-02-05",
    "mistral-large:cloud": "mistral/mistral-large-latest",
    "mistral-small:cloud": "mistral/mistral-small-latest",
    "codestral:cloud": "mistral/codestral-latest",
    "llama-3.1-8b:cloud": "together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "llama-3.1-70b:cloud": "together_ai/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "deepseek-v2:cloud": "together_ai/deepseek-ai/DeepSeek-V2",
    "qwen-2.5-coder-32b:cloud": "together_ai/Qwen/Qwen2.5-Coder-32B-Instruct",
    "qwen-2.5-vl-72b:cloud": "together_ai/Qwen/Qwen2.5-VL-72B-Instruct",
    "llama-3.2-11b-vision:cloud": "together_ai/meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
    "llama-3.2-90b-vision:cloud": "together_ai/meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
}


class ModelLibrary:
    """Curated library of verified models + dynamic HF Hub resolution."""

    @staticmethod
    def search(query: str = "") -> list[ModelCard]:
        if not query:
            return list(BUILTIN_LIBRARY.values())
        q = query.lower()
        results = []
        for card in BUILTIN_LIBRARY.values():
            if (
                q in card.name.lower()
                or q in card.display_name.lower()
                or q in card.description.lower()
            ):
                results.append(card)
                continue
            if any(q in t.lower() for t in card.tags):
                results.append(card)
        return results

    @staticmethod
    def get_model(name: str) -> ModelCard | None:
        return BUILTIN_LIBRARY.get(name)

    @staticmethod
    def filter(category: str = None, tags: list[str] = None) -> list[ModelCard]:
        results = list(BUILTIN_LIBRARY.values())
        if category:
            results = [m for m in results if m.category == category]
        if tags:
            for tag in tags:
                results = [m for m in results if tag in m.tags]
        return results

    @staticmethod
    def categories() -> list[str]:
        return sorted({m.category for m in BUILTIN_LIBRARY.values()})

    @staticmethod
    def all_tags() -> list[str]:
        tags = set()
        for m in BUILTIN_LIBRARY.values():
            tags.update(m.tags)
        return sorted(tags)

    @staticmethod
    def get_cloud_models() -> list[ModelCard]:
        return [m for m in BUILTIN_LIBRARY.values() if m.source == "cloud"]

    @staticmethod
    def get_local_models() -> list[ModelCard]:
        return [m for m in BUILTIN_LIBRARY.values() if m.source == "local"]

    @staticmethod
    def by_capability(cap: str) -> list[ModelCard]:
        return [m for m in BUILTIN_LIBRARY.values() if m.capabilities.get(cap, False)]

    @staticmethod
    def recommend_for_hardware(ram_gb: float) -> list[ModelCard]:
        def parse_ram(ram: str) -> float:
            if not ram:
                return float("inf")
            try:
                return float(ram.replace("GB", "").strip())
            except ValueError:
                return float("inf")

        r = [
            m
            for m in BUILTIN_LIBRARY.values()
            if parse_ram(m.recommended_ram) <= ram_gb and m.source == "local"
        ]
        return sorted(r, key=lambda x: parse_ram(x.recommended_ram))

    @staticmethod
    def recommend_for_task(task: str, ram_gb: float = 8.0) -> list[ModelCard]:
        cap_map = {
            "chat": "chat",
            "code": "code",
            "reasoning": "reasoning",
            "vision": "vision",
            "audio": "audio",
            "agent": "agent",
        }
        cap = cap_map.get(task)
        candidates = [m for m in BUILTIN_LIBRARY.values() if m.source == "local"]
        if cap:
            candidates = [m for m in candidates if m.capabilities.get(cap, False)]
        return sorted(candidates, key=lambda x: x.parameter_count)

    @staticmethod
    def resolve_download_url(name: str, quant: str = "Q4_K_M") -> str | None:
        """Resolve download URL. Checks built-in library first, then HF Hub dynamically."""
        card = BUILTIN_LIBRARY.get(name)
        if card and card.url:
            if "resolve/main" in card.url:
                if quant.upper() != "Q4_K_M":
                    parts = card.url.rsplit("/", 1)
                    if len(parts) == 2:
                        stem = parts[1].rsplit("-", 1)[0]
                        return f"{parts[0]}/{stem}-{quant.upper()}.gguf"
                return card.url

        try:
            from superllm.hub.hf_client import HFClient

            client = HFClient()
            name_clean = name.replace(":cloud", "").replace(":local", "")
            url = client.resolve_gguf_url(name_clean, quant)
            if url:
                return url
        except PermissionError:
            return None
        except Exception:
            pass

        return None

    @staticmethod
    def search_hub(query: str, pipeline_tag: str = None, limit: int = 30) -> list[dict]:
        """Search HuggingFace Hub for models with GGUF files."""
        from superllm.hub.hf_client import HFClient

        client = HFClient()
        results = client.search_models(query=query, pipeline_tag=pipeline_tag, limit=limit)
        return [
            {
                "id": m.id,
                "downloads": m.downloads,
                "likes": m.likes,
                "pipeline_tag": m.pipeline_tag or "",
                "gguf_count": -1,
                "is_gated": m.is_gated,
            }
            for m in results
        ]

    @staticmethod
    def summarize() -> dict:
        total = len(BUILTIN_LIBRARY)
        by_category = {}
        by_source = {"local": 0, "cloud": 0}
        caps_count = {}
        for card in BUILTIN_LIBRARY.values():
            by_category[card.category] = by_category.get(card.category, 0) + 1
            by_source[card.source] = by_source.get(card.source, 0) + 1
            for cap, val in card.capabilities.items():
                if val:
                    caps_count[cap] = caps_count.get(cap, 0) + 1
        return {
            "total_models": total,
            "by_category": by_category,
            "by_source": by_source,
            "capabilities": caps_count,
        }
