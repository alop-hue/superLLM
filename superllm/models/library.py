from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelCard:
    name: str
    display_name: str
    description: str
    architecture: str
    parameter_count: str
    context_length: int
    source: str = "local"  # "local", "cloud", or "both"
    provider: Optional[str] = None
    size_estimates: dict[str, int] = field(default_factory=dict)
    quantizations: list[str] = field(default_factory=lambda: ["Q4_K_M", "Q5_K_M", "Q8_0"])
    tags: list[str] = field(default_factory=list)
    capabilities: dict = field(default_factory=dict)
    category: str = "general"
    url: Optional[str] = None
    license: Optional[str] = None
    recommended_ram: Optional[str] = None
    benchmark: Optional[dict] = None


def _make(name: str, display: str, desc: str, arch: str, params: str, ctx: int,
          category: str = "general", tags: list[str] = None, caps: dict[str, bool] = None,
          source: str = "local", provider: str = None, ram: str = None,
          sizes: dict[str, int] = None, quants: list[str] = None,
          url: str = None) -> ModelCard:
    if tags is None:
        tags = []
    if caps is None:
        caps = {"chat": False, "code": False, "reasoning": False, "embeddings": False, "vision": False}
    if sizes is None:
        sizes = {}
    if quants is None:
        quants = ["Q4_K_M", "Q5_K_M", "Q8_0"]
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
    )


BUILTIN_LIBRARY: dict[str, ModelCard] = {}

# ============================================================
# CHAT MODELS
# ============================================================

# --- Qwen 2.5 ---
BUILTIN_LIBRARY["qwen2.5-0.5b"] = _make("qwen2.5-0.5b", "Qwen 2.5 0.5B",
    "Alibaba's tiny 0.5B model. Extremely lightweight, runs on any hardware.",
    "qwen2", "0.49B", 32768, "chat",
    ["chat", "lightweight", "fast", "low-ram", "multilingual"],
    {"chat": True}, ram="1 GB",
    sizes={"Q4_K_M": 350_000_000, "Q8_0": 550_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-1.5b"] = _make("qwen2.5-1.5b", "Qwen 2.5 1.5B",
    "Alibaba's capable 1.5B model. Strong multilingual support.",
    "qwen2", "1.54B", 32768, "chat",
    ["chat", "lightweight", "fast", "multilingual"],
    {"chat": True, "code": True}, ram="2 GB",
    sizes={"Q4_K_M": 960_000_000, "Q8_0": 1_600_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-3b"] = _make("qwen2.5-3b", "Qwen 2.5 3B",
    "Alibaba's efficient 3B model. Great balance of speed and quality.",
    "qwen2", "3.0B", 32768, "chat",
    ["chat", "lightweight", "multilingual"],
    {"chat": True, "code": True}, ram="4 GB",
    sizes={"Q4_K_M": 1_800_000_000, "Q8_0": 3_200_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-7b"] = _make("qwen2.5-7b", "Qwen 2.5 7B",
    "Alibaba's strong 7B model. Excellent for coding, reasoning, and general tasks.",
    "qwen2", "7.61B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_600_000_000, "Q5_K_M": 5_600_000_000, "Q8_0": 8_100_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-14b"] = _make("qwen2.5-14b", "Qwen 2.5 14B",
    "Alibaba's powerful 14B model. Strong general intelligence and reasoning.",
    "qwen2", "14.8B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_900_000_000, "Q5_K_M": 10_800_000_000, "Q8_0": 15_600_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-32b"] = _make("qwen2.5-32b", "Qwen 2.5 32B",
    "Alibaba's large 32B model. Near-frontier performance for complex tasks.",
    "qwen2", "32.8B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_800_000_000, "Q5_K_M": 24_000_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-32B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-72b"] = _make("qwen2.5-72b", "Qwen 2.5 72B",
    "Alibaba's massive 72B model. Frontier-level capabilities for demanding workloads.",
    "qwen2", "72.7B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="64 GB",
    sizes={"Q4_K_M": 43_000_000_000, "Q5_K_M": 52_000_000_000},
    url="https://huggingface.co/bartowski/Qwen2.5-72B-Instruct-GGUF")

BUILTIN_LIBRARY["qwen2.5-72b:cloud"] = _make("qwen2.5-72b:cloud", "Qwen 2.5 72B (Cloud)",
    "Alibaba's massive 72B model via cloud API. Frontier-level without local hardware needs.",
    "qwen2", "72.7B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- Qwen 3 ---
BUILTIN_LIBRARY["qwen3-0.6b"] = _make("qwen3-0.6b", "Qwen 3 0.6B",
    "Alibaba's latest tiny 0.6B model. Extremely fast and efficient.",
    "qwen3", "0.6B", 32768, "chat",
    ["chat", "lightweight", "fast", "low-ram"],
    {"chat": True}, ram="1 GB",
    sizes={"Q4_K_M": 380_000_000, "Q8_0": 620_000_000})

BUILTIN_LIBRARY["qwen3-1.7b"] = _make("qwen3-1.7b", "Qwen 3 1.7B",
    "Alibaba's latest 1.7B model. Efficient and capable.",
    "qwen3", "1.7B", 32768, "chat",
    ["chat", "lightweight", "fast"],
    {"chat": True, "code": True}, ram="2 GB",
    sizes={"Q4_K_M": 1_000_000_000, "Q8_0": 1_800_000_000})

BUILTIN_LIBRARY["qwen3-4b"] = _make("qwen3-4b", "Qwen 3 4B",
    "Alibaba's latest 4B model. Strong performance for its size.",
    "qwen3", "4.0B", 32768, "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_400_000_000, "Q8_0": 4_200_000_000})

BUILTIN_LIBRARY["qwen3-8b"] = _make("qwen3-8b", "Qwen 3 8B",
    "Alibaba's latest 8B model. Excellent general-purpose capabilities.",
    "qwen3", "8.0B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_800_000_000, "Q5_K_M": 5_800_000_000, "Q8_0": 8_500_000_000})

BUILTIN_LIBRARY["qwen3-14b"] = _make("qwen3-14b", "Qwen 3 14B",
    "Alibaba's latest 14B model. Strong reasoning and generation.",
    "qwen3", "14.0B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_500_000_000, "Q5_K_M": 10_300_000_000})

BUILTIN_LIBRARY["qwen3-30b"] = _make("qwen3-30b", "Qwen 3 30B",
    "Alibaba's latest 30B model. High-end performance for complex tasks.",
    "qwen3", "30.0B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 18_000_000_000, "Q5_K_M": 22_000_000_000})

BUILTIN_LIBRARY["qwen3-32b"] = _make("qwen3-32b", "Qwen 3 32B",
    "Alibaba's latest 32B model. Near-frontier performance.",
    "qwen3", "32.0B", 65536, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_200_000_000, "Q5_K_M": 23_500_000_000})

BUILTIN_LIBRARY["qwen3-235b:cloud"] = _make("qwen3-235b:cloud", "Qwen 3 235B (Cloud)",
    "Alibaba's massive 235B model via cloud API. Frontier AI capabilities.",
    "qwen3", "235B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- Llama 3.1 ---
BUILTIN_LIBRARY["llama3.1-8b"] = _make("llama3.1-8b", "Llama 3.1 8B",
    "Meta's powerful 8B model. Excellent general-purpose model for most tasks.",
    "llama", "8.03B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_900_000_000, "Q5_K_M": 5_900_000_000, "Q8_0": 8_500_000_000},
    url="https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF")

BUILTIN_LIBRARY["llama3.1-70b"] = _make("llama3.1-70b", "Llama 3.1 70B",
    "Meta's large 70B model. Frontier-level performance for complex reasoning.",
    "llama", "70.6B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="64 GB",
    sizes={"Q4_K_M": 42_000_000_000, "Q5_K_M": 51_000_000_000},
    url="https://huggingface.co/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF")

BUILTIN_LIBRARY["llama3.1-405b:cloud"] = _make("llama3.1-405b:cloud", "Llama 3.1 405B (Cloud)",
    "Meta's flagship 405B model via cloud API. Frontier intelligence.",
    "llama", "405B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- Llama 3.2 ---
BUILTIN_LIBRARY["llama3.2-1b"] = _make("llama3.2-1b", "Llama 3.2 1B",
    "Meta's smallest Llama 3.2 model. Fast, efficient, great for testing and low-resource environments.",
    "llama", "1.24B", 8192, "chat",
    ["chat", "lightweight", "fast", "low-ram", "multilingual"],
    {"chat": True}, ram="2 GB",
    sizes={"Q4_K_M": 780_000_000, "Q8_0": 1_300_000_000},
    url="https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF")

BUILTIN_LIBRARY["llama3.2-3b"] = _make("llama3.2-3b", "Llama 3.2 3B",
    "Meta's efficient 3B model. Strong balance of speed and capability for local use.",
    "llama", "3.21B", 8192, "chat",
    ["chat", "lightweight", "fast", "multilingual"],
    {"chat": True, "code": True}, ram="4 GB",
    sizes={"Q4_K_M": 1_900_000_000, "Q5_K_M": 2_300_000_000, "Q8_0": 3_400_000_000},
    url="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF")

# --- Llama 4 ---
BUILTIN_LIBRARY["llama4-scout:cloud"] = _make("llama4-scout:cloud", "Llama 4 Scout (Cloud)",
    "Meta's efficient Llama 4 Scout model via cloud API. Strong general performance.",
    "llama", "17B", 262144, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True, "vision": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

BUILTIN_LIBRARY["llama4-maverick:cloud"] = _make("llama4-maverick:cloud", "Llama 4 Maverick (Cloud)",
    "Meta's powerful Llama 4 Maverick model via cloud API. Frontier capabilities.",
    "llama", "400B", 262144, "general",
    ["chat", "code", "reasoning", "multilingual", "vision", "cloud"],
    {"chat": True, "code": True, "reasoning": True, "vision": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- Gemma 3 ---
BUILTIN_LIBRARY["gemma3-1b"] = _make("gemma3-1b", "Gemma 3 1B",
    "Google's tiny 1B model. Efficient and fast for basic tasks.",
    "gemma", "1.0B", 8192, "chat",
    ["chat", "lightweight", "fast", "low-ram"],
    {"chat": True}, ram="1 GB",
    sizes={"Q4_K_M": 640_000_000, "Q8_0": 1_100_000_000})

BUILTIN_LIBRARY["gemma3-4b"] = _make("gemma3-4b", "Gemma 3 4B",
    "Google's efficient 4B model. Strong performance for its class.",
    "gemma", "4.0B", 8192, "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_500_000_000, "Q8_0": 4_300_000_000})

BUILTIN_LIBRARY["gemma3-12b"] = _make("gemma3-12b", "Gemma 3 12B",
    "Google's capable 12B model. Strong reasoning and coding abilities.",
    "gemma", "12.0B", 8192, "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="12 GB",
    sizes={"Q4_K_M": 7_200_000_000, "Q5_K_M": 8_800_000_000})

BUILTIN_LIBRARY["gemma3-27b"] = _make("gemma3-27b", "Gemma 3 27B",
    "Google's large 27B model. Near-frontier performance.",
    "gemma", "27.0B", 8192, "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 16_200_000_000, "Q5_K_M": 19_800_000_000})

# --- Mistral ---
BUILTIN_LIBRARY["mistral-7b"] = _make("mistral-7b", "Mistral 7B",
    "Mistral AI's powerful 7B model. Strong across all general tasks.",
    "mistral", "7.3B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_400_000_000, "Q8_0": 7_800_000_000},
    url="https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF")

BUILTIN_LIBRARY["mistral-small"] = _make("mistral-small", "Mistral Small",
    "Mistral AI's small cloud model. Fast and efficient for most tasks.",
    "mistral", "22B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 13_000_000_000, "Q5_K_M": 15_800_000_000})

BUILTIN_LIBRARY["mistral-medium:cloud"] = _make("mistral-medium:cloud", "Mistral Medium (Cloud)",
    "Mistral AI's medium cloud model. Strong performance via API.",
    "mistral", "40B", 32768, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="mistral",
    ram="Cloud (no local RAM needed)")

BUILTIN_LIBRARY["mistral-large:cloud"] = _make("mistral-large:cloud", "Mistral Large (Cloud)",
    "Mistral AI's flagship cloud model. Frontier intelligence via API.",
    "mistral", "123B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="mistral",
    ram="Cloud (no local RAM needed)")

# --- Phi-4 ---
BUILTIN_LIBRARY["phi4-mini"] = _make("phi4-mini", "Phi-4 Mini",
    "Microsoft's tiny Phi-4 model. Efficient reasoning in a small package.",
    "phi4", "3.8B", 4096, "chat",
    ["chat", "reasoning", "lightweight"],
    {"chat": True, "code": True, "reasoning": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_300_000_000, "Q8_0": 4_000_000_000})

BUILTIN_LIBRARY["phi4-small"] = _make("phi4-small", "Phi-4 Small",
    "Microsoft's efficient Phi-4 variant. Good balance of size and capability.",
    "phi4", "7.0B", 8192, "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_200_000_000, "Q5_K_M": 5_100_000_000})

BUILTIN_LIBRARY["phi4"] = _make("phi4", "Phi-4",
    "Microsoft's flagship Phi-4 model. Strong reasoning and general intelligence.",
    "phi4", "14.7B", 8192, "general",
    ["chat", "code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_800_000_000, "Q5_K_M": 10_700_000_000})

# --- Command-R ---
BUILTIN_LIBRARY["command-r"] = _make("command-r", "Command R",
    "Cohere's powerful RAG-optimized model. Excellent for retrieval-augmented generation.",
    "command-r", "35B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "rag"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 21_000_000_000, "Q5_K_M": 25_000_000_000})

BUILTIN_LIBRARY["command-r-plus:cloud"] = _make("command-r-plus:cloud", "Command R+ (Cloud)",
    "Cohere's flagship RAG model via cloud API. Best-in-class for enterprise RAG.",
    "command-r", "104B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "rag", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="cohere",
    ram="Cloud (no local RAM needed)")

# --- GLM-4 ---
BUILTIN_LIBRARY["glm4-9b"] = _make("glm4-9b", "GLM-4 9B",
    "Zhipu AI's capable 9B model. Strong Chinese and English capabilities.",
    "glm4", "9.0B", 8192, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 5_400_000_000, "Q5_K_M": 6_600_000_000})

BUILTIN_LIBRARY["glm4-32b"] = _make("glm4-32b", "GLM-4 32B",
    "Zhipu AI's large 32B model. Strong general intelligence.",
    "glm4", "32.0B", 8192, "general",
    ["chat", "code", "reasoning", "multilingual"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_200_000_000, "Q5_K_M": 23_500_000_000})

BUILTIN_LIBRARY["glm4-air"] = _make("glm4-air", "GLM-4 Air",
    "Zhipu AI's efficient Air variant. Optimized for speed.",
    "glm4", "4.0B", 8192, "chat",
    ["chat", "lightweight", "multilingual"],
    {"chat": True, "code": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_400_000_000, "Q8_0": 4_300_000_000})

BUILTIN_LIBRARY["glm4-plus:cloud"] = _make("glm4-plus:cloud", "GLM-4 Plus (Cloud)",
    "Zhipu AI's flagship model via cloud API. Frontier capabilities.",
    "glm4", "130B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="zhipu",
    ram="Cloud (no local RAM needed)")

# --- Tiny / Lightweight ---
BUILTIN_LIBRARY["smollm-135m"] = _make("smollm-135m", "SmolLM 135M",
    "HuggingFace's tiny 135M model. Runs on any device, great for testing.",
    "smollm", "135M", 2048, "chat",
    ["chat", "lightweight", "fast", "low-ram", "tiny"],
    {"chat": True}, ram="512 MB",
    sizes={"Q8_0": 140_000_000, "f16": 270_000_000})

BUILTIN_LIBRARY["smollm-360m"] = _make("smollm-360m", "SmolLM 360M",
    "HuggingFace's small 360M model. Great for lightweight applications.",
    "smollm", "360M", 2048, "chat",
    ["chat", "lightweight", "fast", "low-ram"],
    {"chat": True}, ram="1 GB",
    sizes={"Q8_0": 370_000_000, "f16": 720_000_000})

BUILTIN_LIBRARY["smollm-1.7b"] = _make("smollm-1.7b", "SmolLM 1.7B",
    "HuggingFace's 1.7B model. Capable yet lightweight.",
    "smollm", "1.7B", 2048, "chat",
    ["chat", "lightweight", "fast"],
    {"chat": True, "code": True}, ram="2 GB",
    sizes={"Q4_K_M": 1_000_000_000, "Q8_0": 1_800_000_000})

BUILTIN_LIBRARY["tiny-chat-135m"] = _make("tiny-chat-135m", "TinyChat 135M",
    "Ultra-compact chat model for the most resource-constrained environments.",
    "tiny", "135M", 1024, "chat",
    ["chat", "lightweight", "fast", "low-ram", "tiny"],
    {"chat": True}, ram="512 MB",
    sizes={"Q8_0": 140_000_000, "f16": 270_000_000})

BUILTIN_LIBRARY["tiny-chat-350m"] = _make("tiny-chat-350m", "TinyChat 350M",
    "Small chat model for resource-constrained environments.",
    "tiny", "350M", 2048, "chat",
    ["chat", "lightweight", "fast", "low-ram"],
    {"chat": True}, ram="1 GB",
    sizes={"Q8_0": 360_000_000, "f16": 700_000_000})

BUILTIN_LIBRARY["tiny-chat-500m"] = _make("tiny-chat-500m", "TinyChat 500M",
    "Compact chat model balancing size and capability.",
    "tiny", "500M", 2048, "chat",
    ["chat", "lightweight", "fast", "low-ram"],
    {"chat": True}, ram="1 GB",
    sizes={"Q4_K_M": 310_000_000, "Q8_0": 520_000_000})

BUILTIN_LIBRARY["mobile-assistant-500m"] = _make("mobile-assistant-500m", "Mobile Assistant 500M",
    "Optimized mobile assistant model for on-device deployment.",
    "mobile", "500M", 2048, "chat",
    ["chat", "lightweight", "fast", "low-ram", "mobile"],
    {"chat": True}, ram="1 GB",
    sizes={"Q4_K_M": 310_000_000, "Q8_0": 520_000_000})

# ============================================================
# CODING MODELS
# ============================================================

# --- Qwen Coder ---
BUILTIN_LIBRARY["qwen-coder-1.5b"] = _make("qwen-coder-1.5b", "Qwen Coder 1.5B",
    "Alibaba's specialized coding model. Efficient code generation.",
    "qwen2", "1.54B", 32768, "code",
    ["code", "lightweight"],
    {"chat": True, "code": True}, ram="2 GB",
    sizes={"Q4_K_M": 960_000_000, "Q8_0": 1_600_000_000})

BUILTIN_LIBRARY["qwen-coder-7b"] = _make("qwen-coder-7b", "Qwen Coder 7B",
    "Alibaba's capable coding model. Strong code generation and understanding.",
    "qwen2", "7.61B", 32768, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_600_000_000, "Q5_K_M": 5_600_000_000})

BUILTIN_LIBRARY["qwen-coder-14b"] = _make("qwen-coder-14b", "Qwen Coder 14B",
    "Alibaba's powerful coding model. State-of-the-art code intelligence.",
    "qwen2", "14.8B", 32768, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_900_000_000, "Q5_K_M": 10_800_000_000})

BUILTIN_LIBRARY["qwen-coder-32b"] = _make("qwen-coder-32b", "Qwen Coder 32B",
    "Alibaba's large coding model. Expert-level code generation.",
    "qwen2", "32.8B", 32768, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_800_000_000, "Q5_K_M": 24_000_000_000})

BUILTIN_LIBRARY["qwen-coder-max:cloud"] = _make("qwen-coder-max:cloud", "Qwen Coder Max (Cloud)",
    "Alibaba's flagship coding model via cloud API. Best code intelligence.",
    "qwen2", "235B", 131072, "code",
    ["code", "reasoning", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- DeepSeek Coder ---
BUILTIN_LIBRARY["deepseek-coder-1.3b"] = _make("deepseek-coder-1.3b", "DeepSeek Coder 1.3B",
    "DeepSeek's compact coding model. Efficient code completion.",
    "deepseek", "1.3B", 16384, "code",
    ["code", "lightweight"],
    {"chat": True, "code": True}, ram="2 GB",
    sizes={"Q4_K_M": 820_000_000, "Q8_0": 1_400_000_000})

BUILTIN_LIBRARY["deepseek-coder-6.7b"] = _make("deepseek-coder-6.7b", "DeepSeek Coder 6.7B",
    "DeepSeek's specialized coding model. State-of-the-art for code generation.",
    "deepseek", "6.7B", 16384, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_100_000_000, "Q5_K_M": 5_000_000_000, "Q8_0": 7_200_000_000})

BUILTIN_LIBRARY["deepseek-coder-33b"] = _make("deepseek-coder-33b", "DeepSeek Coder 33B",
    "DeepSeek's large coding model. Expert-level code generation.",
    "deepseek", "33B", 16384, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_800_000_000, "Q5_K_M": 24_200_000_000})

BUILTIN_LIBRARY["deepseek-v3-coder:cloud"] = _make("deepseek-v3-coder:cloud", "DeepSeek V3 Coder (Cloud)",
    "DeepSeek's latest flagship coder via cloud API. Frontier code intelligence.",
    "deepseek", "671B", 131072, "code",
    ["code", "reasoning", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- CodeStral ---
BUILTIN_LIBRARY["codestral-22b"] = _make("codestral-22b", "CodeStral 22B",
    "Mistral's specialized coding model. Excellent code generation and understanding.",
    "mistral", "22B", 32768, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 13_200_000_000, "Q5_K_M": 16_100_000_000})

# --- StarCoder2 ---
BUILTIN_LIBRARY["starcoder2-3b"] = _make("starcoder2-3b", "StarCoder2 3B",
    "IBM's compact code model. Efficient for code tasks.",
    "starcoder", "3B", 16384, "code",
    ["code", "lightweight"],
    {"chat": True, "code": True}, ram="4 GB",
    sizes={"Q4_K_M": 1_800_000_000, "Q8_0": 3_200_000_000})

BUILTIN_LIBRARY["starcoder2-7b"] = _make("starcoder2-7b", "StarCoder2 7B",
    "IBM's capable code model. Strong code generation.",
    "starcoder", "7B", 16384, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_200_000_000, "Q5_K_M": 5_100_000_000})

BUILTIN_LIBRARY["starcoder2-15b"] = _make("starcoder2-15b", "StarCoder2 15B",
    "IBM's large code model. Expert-level code generation.",
    "starcoder", "15B", 16384, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 9_000_000_000, "Q5_K_M": 11_000_000_000})

# --- Granite Code ---
BUILTIN_LIBRARY["granite-code-3b"] = _make("granite-code-3b", "Granite Code 3B",
    "IBM's compact enterprise code model.",
    "granite", "3B", 8192, "code",
    ["code", "lightweight"],
    {"chat": True, "code": True}, ram="4 GB",
    sizes={"Q4_K_M": 1_800_000_000, "Q8_0": 3_200_000_000})

BUILTIN_LIBRARY["granite-code-8b"] = _make("granite-code-8b", "Granite Code 8B",
    "IBM's enterprise code model. Strong code generation for business.",
    "granite", "8B", 8192, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_800_000_000, "Q5_K_M": 5_800_000_000})

BUILTIN_LIBRARY["granite-code-20b"] = _make("granite-code-20b", "Granite Code 20B",
    "IBM's large enterprise code model. Expert code generation.",
    "granite", "20B", 8192, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 12_000_000_000, "Q5_K_M": 14_600_000_000})

# --- Phi-4 Code ---
BUILTIN_LIBRARY["phi4-code"] = _make("phi4-code", "Phi-4 Code",
    "Microsoft's code-specialized Phi-4 variant. Strong coding capabilities.",
    "phi4", "14.7B", 8192, "code",
    ["code", "reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_800_000_000, "Q5_K_M": 10_700_000_000})

# ============================================================
# REASONING MODELS
# ============================================================

# --- DeepSeek R1 ---
BUILTIN_LIBRARY["deepseek-r1-1.5b"] = _make("deepseek-r1-1.5b", "DeepSeek R1 1.5B",
    "DeepSeek's compact reasoning model. Chain-of-thought in a small package.",
    "deepseek", "1.5B", 16384, "reasoning",
    ["reasoning", "lightweight"],
    {"chat": True, "reasoning": True}, ram="2 GB",
    sizes={"Q4_K_M": 950_000_000, "Q8_0": 1_600_000_000})

BUILTIN_LIBRARY["deepseek-r1-7b"] = _make("deepseek-r1-7b", "DeepSeek R1 7B",
    "DeepSeek's capable reasoning model. Strong chain-of-thought reasoning.",
    "deepseek", "7B", 16384, "reasoning",
    ["reasoning"],
    {"chat": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000})

BUILTIN_LIBRARY["deepseek-r1-8b"] = _make("deepseek-r1-8b", "DeepSeek R1 8B",
    "DeepSeek's 8B reasoning model. Excellent mathematical reasoning.",
    "deepseek", "8B", 16384, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 5_000_000_000, "Q5_K_M": 6_100_000_000})

BUILTIN_LIBRARY["deepseek-r1-14b"] = _make("deepseek-r1-14b", "DeepSeek R1 14B",
    "DeepSeek's powerful reasoning model. Advanced chain-of-thought.",
    "deepseek", "14B", 16384, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_400_000_000, "Q5_K_M": 10_200_000_000})

BUILTIN_LIBRARY["deepseek-r1-32b"] = _make("deepseek-r1-32b", "DeepSeek R1 32B",
    "DeepSeek's large reasoning model. Expert-level reasoning capabilities.",
    "deepseek", "32B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_200_000_000, "Q5_K_M": 23_500_000_000})

BUILTIN_LIBRARY["deepseek-r1-70b"] = _make("deepseek-r1-70b", "DeepSeek R1 70B",
    "DeepSeek's very large reasoning model. Near-frontier reasoning.",
    "deepseek", "70B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="64 GB",
    sizes={"Q4_K_M": 42_000_000_000, "Q5_K_M": 51_000_000_000})

BUILTIN_LIBRARY["deepseek-r1-671b:cloud"] = _make("deepseek-r1-671b:cloud", "DeepSeek R1 671B (Cloud)",
    "DeepSeek's flagship reasoning model via cloud API. Frontier reasoning.",
    "deepseek", "671B", 131072, "reasoning",
    ["reasoning", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- Qwen3 Thinking ---
BUILTIN_LIBRARY["qwen3-thinking-4b"] = _make("qwen3-thinking-4b", "Qwen 3 Thinking 4B",
    "Alibaba's thinking-enhanced 4B model. Step-by-step reasoning.",
    "qwen3", "4B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "reasoning": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_400_000_000, "Q8_0": 4_300_000_000})

BUILTIN_LIBRARY["qwen3-thinking-8b"] = _make("qwen3-thinking-8b", "Qwen 3 Thinking 8B",
    "Alibaba's thinking-enhanced 8B model. Strong reasoning capabilities.",
    "qwen3", "8B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_800_000_000, "Q5_K_M": 5_800_000_000})

BUILTIN_LIBRARY["qwen3-thinking-32b"] = _make("qwen3-thinking-32b", "Qwen 3 Thinking 32B",
    "Alibaba's large thinking-enhanced model. Advanced reasoning.",
    "qwen3", "32B", 65536, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_200_000_000, "Q5_K_M": 23_500_000_000})

BUILTIN_LIBRARY["qwen3-thinking-max:cloud"] = _make("qwen3-thinking-max:cloud", "Qwen 3 Thinking Max (Cloud)",
    "Alibaba's flagship thinking model via cloud API. Frontier reasoning.",
    "qwen3", "235B", 131072, "reasoning",
    ["reasoning", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# --- O1-like & Reasoner ---
BUILTIN_LIBRARY["o1-like-small"] = _make("o1-like-small", "O1-like Small",
    "OpenAI-style reasoning model. Chain-of-thought in a compact size.",
    "o1", "7B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000})

BUILTIN_LIBRARY["o1-like-medium"] = _make("o1-like-medium", "O1-like Medium",
    "OpenAI-style reasoning model. Strong chain-of-thought reasoning.",
    "o1", "32B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_200_000_000, "Q5_K_M": 23_500_000_000})

BUILTIN_LIBRARY["o1-like-large:cloud"] = _make("o1-like-large:cloud", "O1-like Large (Cloud)",
    "OpenAI-style reasoning model via cloud API. Frontier reasoning capabilities.",
    "o1", "175B", 131072, "reasoning",
    ["reasoning", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

BUILTIN_LIBRARY["reasoner-7b"] = _make("reasoner-7b", "Reasoner 7B",
    "General reasoning model. Strong logical and mathematical reasoning.",
    "reasoner", "7B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "reasoning": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000})

BUILTIN_LIBRARY["reasoner-14b"] = _make("reasoner-14b", "Reasoner 14B",
    "Advanced reasoning model. Strong multi-step reasoning.",
    "reasoner", "14B", 32768, "reasoning",
    ["reasoning"],
    {"chat": True, "code": True, "reasoning": True}, ram="16 GB",
    sizes={"Q4_K_M": 8_400_000_000, "Q5_K_M": 10_200_000_000})

BUILTIN_LIBRARY["reasoner-70b:cloud"] = _make("reasoner-70b:cloud", "Reasoner 70B (Cloud)",
    "Advanced reasoning model via cloud API. Expert-level reasoning.",
    "reasoner", "70B", 65536, "reasoning",
    ["reasoning", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

# ============================================================
# VISION / MULTIMODAL MODELS
# ============================================================

BUILTIN_LIBRARY["qwen-vl-3b"] = _make("qwen-vl-3b", "Qwen VL 3B",
    "Alibaba's vision-language model. Understands and describes images.",
    "qwen2", "3B", 32768, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="4 GB",
    sizes={"Q4_K_M": 1_900_000_000, "Q8_0": 3_300_000_000})

BUILTIN_LIBRARY["qwen-vl-7b"] = _make("qwen-vl-7b", "Qwen VL 7B",
    "Alibaba's vision-language model with strong image understanding.",
    "qwen2", "7B", 32768, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000})

BUILTIN_LIBRARY["qwen-vl-32b"] = _make("qwen-vl-32b", "Qwen VL 32B",
    "Alibaba's large vision-language model. Detailed image understanding.",
    "qwen2", "32B", 32768, "vision",
    ["vision", "multimodal"],
    {"chat": True, "code": True, "vision": True}, ram="32 GB",
    sizes={"Q4_K_M": 19_200_000_000, "Q5_K_M": 23_500_000_000})

BUILTIN_LIBRARY["qwen2.5-vl-3b"] = _make("qwen2.5-vl-3b", "Qwen 2.5 VL 3B",
    "Alibaba's latest vision-language model. Improved image understanding.",
    "qwen2", "3B", 32768, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="4 GB",
    sizes={"Q4_K_M": 1_900_000_000, "Q8_0": 3_300_000_000})

BUILTIN_LIBRARY["qwen2.5-vl-7b"] = _make("qwen2.5-vl-7b", "Qwen 2.5 VL 7B",
    "Alibaba's latest 7B vision-language model. Strong multimodal capabilities.",
    "qwen2", "7B", 32768, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000})

BUILTIN_LIBRARY["qwen2.5-vl-72b:cloud"] = _make("qwen2.5-vl-72b:cloud", "Qwen 2.5 VL 72B (Cloud)",
    "Alibaba's large vision-language model via cloud API. Frontier multimodal.",
    "qwen2", "72B", 131072, "vision",
    ["vision", "multimodal", "cloud"],
    {"chat": True, "code": True, "vision": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

BUILTIN_LIBRARY["gemma3-vision-4b"] = _make("gemma3-vision-4b", "Gemma 3 Vision 4B",
    "Google's vision-language 4B model. Efficient image understanding.",
    "gemma", "4B", 8192, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_500_000_000, "Q8_0": 4_300_000_000})

BUILTIN_LIBRARY["gemma3-vision-12b"] = _make("gemma3-vision-12b", "Gemma 3 Vision 12B",
    "Google's vision-language 12B model. Strong multimodal capabilities.",
    "gemma", "12B", 8192, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="12 GB",
    sizes={"Q4_K_M": 7_200_000_000, "Q5_K_M": 8_800_000_000})

BUILTIN_LIBRARY["gemma3-vision-27b"] = _make("gemma3-vision-27b", "Gemma 3 Vision 27B",
    "Google's large vision-language model. Advanced image understanding.",
    "gemma", "27B", 8192, "vision",
    ["vision", "multimodal"],
    {"chat": True, "code": True, "vision": True}, ram="32 GB",
    sizes={"Q4_K_M": 16_200_000_000, "Q5_K_M": 19_800_000_000})

BUILTIN_LIBRARY["llama3.2-vision-11b"] = _make("llama3.2-vision-11b", "Llama 3.2 Vision 11B",
    "Meta's vision-language 11B model. Strong image understanding capabilities.",
    "llama", "11B", 131072, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="12 GB",
    sizes={"Q4_K_M": 6_600_000_000, "Q5_K_M": 8_000_000_000})

BUILTIN_LIBRARY["llama3.2-vision-90b:cloud"] = _make("llama3.2-vision-90b:cloud", "Llama 3.2 Vision 90B (Cloud)",
    "Meta's large vision-language model via cloud API. Frontier multimodal.",
    "llama", "90B", 131072, "vision",
    ["vision", "multimodal", "cloud"],
    {"chat": True, "code": True, "vision": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")

BUILTIN_LIBRARY["internvl-2b"] = _make("internvl-2b", "InternVL 2B",
    "Shanghai AI Lab's compact vision-language model.",
    "internvl", "2B", 4096, "vision",
    ["vision", "multimodal", "lightweight"],
    {"chat": True, "vision": True}, ram="2 GB",
    sizes={"Q4_K_M": 1_300_000_000, "Q8_0": 2_200_000_000})

BUILTIN_LIBRARY["internvl-8b"] = _make("internvl-8b", "InternVL 8B",
    "Shanghai AI Lab's vision-language model. Strong multimodal understanding.",
    "internvl", "8B", 4096, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="8 GB",
    sizes={"Q4_K_M": 5_000_000_000, "Q5_K_M": 6_100_000_000})

BUILTIN_LIBRARY["internvl-26b"] = _make("internvl-26b", "InternVL 26B",
    "Shanghai AI Lab's large vision-language model. Advanced multimodal.",
    "internvl", "26B", 4096, "vision",
    ["vision", "multimodal"],
    {"chat": True, "code": True, "vision": True}, ram="32 GB",
    sizes={"Q4_K_M": 15_600_000_000, "Q5_K_M": 19_000_000_000})

BUILTIN_LIBRARY["molmo-7b"] = _make("molmo-7b", "Molmo 7B",
    "Open-source vision-language model. Strong image understanding.",
    "molmo", "7B", 4096, "vision",
    ["vision", "multimodal"],
    {"chat": True, "vision": True}, ram="8 GB",
    sizes={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_300_000_000})

# ============================================================
# EMBEDDING MODELS
# ============================================================

BUILTIN_LIBRARY["bge-small"] = _make("bge-small", "BGE Small",
    "BAAI's efficient small embedding model. Great for semantic search.",
    "bert", "0.03B", 512, "embeddings",
    ["embeddings", "lightweight", "rag"],
    {"embeddings": True}, ram="512 MB",
    sizes={"Q8_0": 70_000_000, "f16": 130_000_000})

BUILTIN_LIBRARY["bge-base"] = _make("bge-base", "BGE Base",
    "BAAI's base embedding model. Strong semantic understanding.",
    "bert", "0.11B", 512, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="1 GB",
    sizes={"Q8_0": 110_000_000, "f16": 220_000_000})

BUILTIN_LIBRARY["bge-large"] = _make("bge-large", "BGE Large",
    "BAAI's large embedding model. Best-in-class semantic search.",
    "bert", "0.33B", 512, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="2 GB",
    sizes={"Q8_0": 340_000_000, "f16": 670_000_000})

BUILTIN_LIBRARY["gte-small"] = _make("gte-small", "GTE Small",
    "Alibaba's efficient small embedding model.",
    "gte", "0.03B", 8192, "embeddings",
    ["embeddings", "lightweight", "rag"],
    {"embeddings": True}, ram="512 MB",
    sizes={"Q8_0": 60_000_000, "f16": 120_000_000})

BUILTIN_LIBRARY["gte-base"] = _make("gte-base", "GTE Base",
    "Alibaba's base embedding model. Good semantic search quality.",
    "gte", "0.11B", 8192, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="1 GB",
    sizes={"Q8_0": 110_000_000, "f16": 220_000_000})

BUILTIN_LIBRARY["gte-large"] = _make("gte-large", "GTE Large",
    "Alibaba's large embedding model. Strong retrieval quality.",
    "gte", "0.33B", 8192, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="2 GB",
    sizes={"Q8_0": 340_000_000, "f16": 670_000_000})

BUILTIN_LIBRARY["e5-small"] = _make("e5-small", "E5 Small",
    "Microsoft's efficient small embedding model.",
    "e5", "0.03B", 512, "embeddings",
    ["embeddings", "lightweight", "rag"],
    {"embeddings": True}, ram="512 MB",
    sizes={"Q8_0": 70_000_000, "f16": 130_000_000})

BUILTIN_LIBRARY["e5-base"] = _make("e5-base", "E5 Base",
    "Microsoft's base embedding model. Strong multilingual search.",
    "e5", "0.11B", 512, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="1 GB",
    sizes={"Q8_0": 110_000_000, "f16": 220_000_000})

BUILTIN_LIBRARY["e5-large"] = _make("e5-large", "E5 Large",
    "Microsoft's large embedding model. Best-in-class retrieval.",
    "e5", "0.33B", 512, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="2 GB",
    sizes={"Q8_0": 340_000_000, "f16": 670_000_000})

BUILTIN_LIBRARY["nomic-embed"] = _make("nomic-embed", "Nomic Embed",
    "Nomic's text embedding model. Great for RAG and semantic search.",
    "bert", "0.14B", 8192, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="1 GB",
    sizes={"Q8_0": 90_000_000, "f16": 170_000_000})

BUILTIN_LIBRARY["nomic-embed-v2"] = _make("nomic-embed-v2", "Nomic Embed v2",
    "Nomic's latest embedding model. Improved retrieval quality.",
    "nomic", "0.14B", 8192, "embeddings",
    ["embeddings", "rag"],
    {"embeddings": True}, ram="1 GB",
    sizes={"Q8_0": 95_000_000, "f16": 180_000_000})

BUILTIN_LIBRARY["qwen-embed-0.6b"] = _make("qwen-embed-0.6b", "Qwen Embed 0.6B",
    "Alibaba's embedding model. Strong multilingual embeddings.",
    "qwen2", "0.6B", 32768, "embeddings",
    ["embeddings", "rag", "multilingual"],
    {"embeddings": True}, ram="1 GB",
    sizes={"Q4_K_M": 380_000_000, "Q8_0": 640_000_000})

BUILTIN_LIBRARY["qwen-embed-4b"] = _make("qwen-embed-4b", "Qwen Embed 4B",
    "Alibaba's large embedding model. High-quality multilingual embeddings.",
    "qwen2", "4B", 32768, "embeddings",
    ["embeddings", "rag", "multilingual"],
    {"embeddings": True}, ram="4 GB",
    sizes={"Q4_K_M": 2_400_000_000, "Q8_0": 4_300_000_000})

# ============================================================
# CLOUD FRONTIER MODELS (shortcuts)
# ============================================================

BUILTIN_LIBRARY["deepseek-v3:cloud"] = _make("deepseek-v3:cloud", "DeepSeek V3 (Cloud)",
    "DeepSeek's latest flagship model via cloud API. Frontier general intelligence.",
    "deepseek", "671B", 131072, "general",
    ["chat", "code", "reasoning", "multilingual", "cloud"],
    {"chat": True, "code": True, "reasoning": True}, source="cloud", provider="together",
    ram="Cloud (no local RAM needed)")


class ModelLibrary:
    @staticmethod
    def search(query: str = "", source: str = None) -> list[ModelCard]:
        q = query.lower().strip()
        results = []
        for name, card in BUILTIN_LIBRARY.items():
            if source and card.source != source and source != "all":
                if source == "local" and card.source == "cloud":
                    continue
                if source == "cloud" and card.source != "cloud":
                    continue
            if not q:
                results.append(card)
            elif (q in name.lower()
                  or q in card.display_name.lower()
                  or q in card.description.lower()
                  or q in " ".join(card.tags)):
                results.append(card)
        return results

    @staticmethod
    def get_model(name: str) -> Optional[ModelCard]:
        return BUILTIN_LIBRARY.get(name)

    @staticmethod
    def filter(
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        source: str = None,
    ) -> list[ModelCard]:
        results = list(BUILTIN_LIBRARY.values())
        if category:
            results = [m for m in results if m.category == category]
        if tags:
            results = [m for m in results if all(t in m.tags for t in tags)]
        if source == "local":
            results = [m for m in results if m.source != "cloud"]
        elif source == "cloud":
            results = [m for m in results if m.source == "cloud"]
        return results

    @staticmethod
    def categories() -> list[str]:
        cats = set()
        for card in BUILTIN_LIBRARY.values():
            cats.add(card.category)
        return sorted(cats)

    @staticmethod
    def all_tags() -> list[str]:
        tags = set()
        for card in BUILTIN_LIBRARY.values():
            tags.update(card.tags)
        return sorted(tags)

    @staticmethod
    def recommend_for_hardware(ram_gb: float) -> list[ModelCard]:
        recommendations = []
        for card in BUILTIN_LIBRARY.values():
            if card.source == "cloud":
                recommendations.append(card)
                continue
            if card.recommended_ram:
                try:
                    needed = float(card.recommended_ram.split()[0])
                    if needed <= ram_gb:
                        recommendations.append(card)
                except (ValueError, IndexError):
                    recommendations.append(card)
        return sorted(recommendations, key=lambda x: x.parameter_count)

    @staticmethod
    def get_local_models() -> list[ModelCard]:
        return [m for m in BUILTIN_LIBRARY.values() if m.source != "cloud"]

    @staticmethod
    def get_cloud_models() -> list[ModelCard]:
        return [m for m in BUILTIN_LIBRARY.values() if m.source == "cloud"]
