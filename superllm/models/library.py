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
    size_estimates: dict[str, int]
    quantizations: list[str] = field(default_factory=lambda: ["Q4_K_M", "Q5_K_M", "Q8_0"])
    tags: list[str] = field(default_factory=list)
    capabilities: dict = field(default_factory=dict)
    category: str = "general"
    url: Optional[str] = None
    license: Optional[str] = None
    recommended_ram: Optional[str] = None
    benchmark: Optional[dict] = None


BUILTIN_LIBRARY: dict[str, ModelCard] = {
    "llama-3.2-1b": ModelCard(
        name="llama-3.2-1b",
        display_name="Llama 3.2 1B",
        description="Meta's smallest Llama 3.2 model. Fast, efficient, great for testing and low-resource environments.",
        architecture="llama",
        parameter_count="1.24B",
        context_length=8192,
        size_estimates={"Q4_K_M": 780_000_000, "Q8_0": 1_300_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0"],
        tags=["chat", "lightweight", "fast", "low-ram", "multilingual"],
        capabilities={"chat": True, "code": False, "reasoning": False, "embeddings": False, "vision": False},
        category="chat",
        recommended_ram="2 GB",
        url="https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF",
    ),
    "llama-3.2-3b": ModelCard(
        name="llama-3.2-3b",
        display_name="Llama 3.2 3B",
        description="Meta's efficient 3B model. Strong balance of speed and capability for local use.",
        architecture="llama",
        parameter_count="3.21B",
        context_length=8192,
        size_estimates={"Q4_K_M": 1_900_000_000, "Q5_K_M": 2_300_000_000, "Q8_0": 3_400_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0"],
        tags=["chat", "lightweight", "fast", "multilingual"],
        capabilities={"chat": True, "code": True, "reasoning": False, "embeddings": False, "vision": False},
        category="chat",
        recommended_ram="4 GB",
        url="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF",
    ),
    "llama-3.1-8b": ModelCard(
        name="llama-3.1-8b",
        display_name="Llama 3.1 8B",
        description="Meta's powerful 8B model. Excellent general-purpose model for most tasks.",
        architecture="llama",
        parameter_count="8.03B",
        context_length=131072,
        size_estimates={"Q4_K_M": 4_900_000_000, "Q5_K_M": 5_900_000_000, "Q8_0": 8_500_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0", "Q2_K"],
        tags=["chat", "code", "reasoning", "multilingual"],
        capabilities={"chat": True, "code": True, "reasoning": True, "embeddings": False, "vision": False},
        category="general",
        recommended_ram="8 GB",
        url="https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
    ),
    "qwen2.5-0.5b": ModelCard(
        name="qwen2.5-0.5b",
        display_name="Qwen 2.5 0.5B",
        description="Alibaba's tiny 0.5B model. Extremely lightweight, runs on any hardware.",
        architecture="qwen2",
        parameter_count="0.49B",
        context_length=32768,
        size_estimates={"Q4_K_M": 350_000_000, "Q8_0": 550_000_000},
        quantizations=["Q4_K_M", "Q8_0"],
        tags=["chat", "lightweight", "fast", "low-ram", "multilingual"],
        capabilities={"chat": True, "code": False, "reasoning": False, "embeddings": False, "vision": False},
        category="chat",
        recommended_ram="1 GB",
        url="https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF",
    ),
    "qwen2.5-1.5b": ModelCard(
        name="qwen2.5-1.5b",
        display_name="Qwen 2.5 1.5B",
        description="Alibaba's capable 1.5B model. Strong multilingual support.",
        architecture="qwen2",
        parameter_count="1.54B",
        context_length=32768,
        size_estimates={"Q4_K_M": 960_000_000, "Q8_0": 1_600_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0"],
        tags=["chat", "lightweight", "fast", "multilingual"],
        capabilities={"chat": True, "code": True, "reasoning": False, "embeddings": False, "vision": False},
        category="chat",
        recommended_ram="2 GB",
        url="https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF",
    ),
    "qwen2.5-7b": ModelCard(
        name="qwen2.5-7b",
        display_name="Qwen 2.5 7B",
        description="Alibaba's strong 7B model. Excellent for coding, reasoning, and general tasks.",
        architecture="qwen2",
        parameter_count="7.61B",
        context_length=32768,
        size_estimates={"Q4_K_M": 4_600_000_000, "Q5_K_M": 5_600_000_000, "Q8_0": 8_100_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0", "Q2_K"],
        tags=["chat", "code", "reasoning", "multilingual"],
        capabilities={"chat": True, "code": True, "reasoning": True, "embeddings": False, "vision": False},
        category="general",
        recommended_ram="8 GB",
        url="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF",
    ),
    "deepseek-coder-6.7b": ModelCard(
        name="deepseek-coder-6.7b",
        display_name="DeepSeek Coder 6.7B",
        description="DeepSeek's specialized coding model. State-of-the-art for code generation.",
        architecture="deepseek",
        parameter_count="6.7B",
        context_length=16384,
        size_estimates={"Q4_K_M": 4_100_000_000, "Q5_K_M": 5_000_000_000, "Q8_0": 7_200_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0"],
        tags=["code", "reasoning"],
        capabilities={"chat": True, "code": True, "reasoning": True, "embeddings": False, "vision": False},
        category="code",
        recommended_ram="8 GB",
        url="https://huggingface.co/bartowski/deepseek-coder-6.7b-instruct-GGUF",
    ),
    "mistral-7b": ModelCard(
        name="mistral-7b",
        display_name="Mistral 7B",
        description="Mistral AI's powerful 7B model. Strong across all general tasks.",
        architecture="mistral",
        parameter_count="7.3B",
        context_length=32768,
        size_estimates={"Q4_K_M": 4_400_000_000, "Q5_K_M": 5_400_000_000, "Q8_0": 7_800_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0", "Q2_K"],
        tags=["chat", "code", "reasoning", "multilingual"],
        capabilities={"chat": True, "code": True, "reasoning": True, "embeddings": False, "vision": False},
        category="general",
        recommended_ram="8 GB",
        url="https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF",
    ),
    "phi-3-mini": ModelCard(
        name="phi-3-mini",
        display_name="Phi-3 Mini 3.8B",
        description="Microsoft's efficient 3.8B model. Strong reasoning for its size.",
        architecture="phi3",
        parameter_count="3.8B",
        context_length=4096,
        size_estimates={"Q4_K_M": 2_400_000_000, "Q5_K_M": 2_900_000_000, "Q8_0": 4_100_000_000},
        quantizations=["Q4_K_M", "Q5_K_M", "Q8_0"],
        tags=["chat", "reasoning", "lightweight"],
        capabilities={"chat": True, "code": True, "reasoning": True, "embeddings": False, "vision": False},
        category="general",
        recommended_ram="4 GB",
        url="https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF",
    ),
    "nomic-embed-text-v1.5": ModelCard(
        name="nomic-embed-text-v1.5",
        display_name="Nomic Embed Text v1.5",
        description="High-quality text embedding model. Great for RAG and semantic search.",
        architecture="bert",
        parameter_count="0.14B",
        context_length=8192,
        size_estimates={"Q8_0": 90_000_000, "f16": 170_000_000},
        quantizations=["Q8_0", "f16"],
        tags=["embeddings", "lightweight", "rag"],
        capabilities={"chat": False, "code": False, "reasoning": False, "embeddings": True, "vision": False},
        category="embeddings",
        recommended_ram="1 GB",
        url="https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF",
    ),
    "llava-v1.6-7b": ModelCard(
        name="llava-v1.6-7b",
        display_name="LLaVA 1.6 7B",
        description="Vision-language model. Can understand and describe images.",
        architecture="llava",
        parameter_count="7.3B",
        context_length=4096,
        size_estimates={"Q4_K_M": 5_200_000_000, "Q5_K_M": 6_300_000_000, "Q8_0": 9_000_000_000},
        quantizations=["Q4_K_M", "Q5_K_M"],
        tags=["vision", "multimodal"],
        capabilities={"chat": True, "code": False, "reasoning": False, "embeddings": False, "vision": True},
        category="vision",
        recommended_ram="12 GB",
        url="https://huggingface.co/bartowski/llava-v1.6-7b-GGUF",
    ),
}


class ModelLibrary:
    @staticmethod
    def search(query: str = "") -> list[ModelCard]:
        q = query.lower().strip()
        results = []
        for name, card in BUILTIN_LIBRARY.items():
            if not q:
                results.append(card)
            elif (
                q in name.lower()
                or q in card.display_name.lower()
                or q in card.description.lower()
                or q in " ".join(card.tags)
            ):
                results.append(card)
        return results

    @staticmethod
    def get_model(name: str) -> Optional[ModelCard]:
        return BUILTIN_LIBRARY.get(name)

    @staticmethod
    def filter(
        category: Optional[str] = None,
        min_params: Optional[str] = None,
        max_params: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[ModelCard]:
        results = list(BUILTIN_LIBRARY.values())
        if category:
            results = [m for m in results if m.category == category]
        if tags:
            results = [m for m in results if all(t in m.tags for t in tags)]
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
            if card.recommended_ram:
                needed = float(card.recommended_ram.split()[0])
                if needed <= ram_gb:
                    recommendations.append(card)
        return sorted(recommendations, key=lambda x: x.parameter_count)
