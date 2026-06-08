from __future__ import annotations

import re
from collections.abc import AsyncGenerator
from enum import Enum

from superllm.config.settings import Mode, settings
from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)
from superllm.inference.cloud import CloudInferenceEngine
from superllm.inference.local import LocalInferenceEngine
from superllm.models.library import ModelLibrary


class TaskType(str, Enum):
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDINGS = "embeddings"
    AGENT = "agent"
    RAG = "rag"
    MATH = "math"
    WRITING = "writing"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    GENERAL = "general"


class TaskClassifier:
    CODE_PATTERNS = [
        r"\b(write|implement|create|generate|code|program|build)\s+(a\s+)?(function|class|script|program|code|app|api)\b",
        r"\b(python|javascript|typescript|rust|golang|java)\s+(function|class|script|code)\b",
        r"\b(implement|code|program|script|function)\b.*\bin\b.*(python|js|ts|rust|go|java|c\+\+|ruby|php)",
        r"\b(refactor|debug|fix|optimize|review).*(code|function|class|performance|file)",
        r"\b(generate|create|build).*(api|endpoint|route|server|cli)",
        r"\b(explain|review)\s+(this\s+)?code\b",
        r"```\w*\n",
        r"\b(def |function |class |import |from |const |let |var |fn )",
    ]

    REASONING_PATTERNS = [
        r"\b(explain|reason|why|how does|analyze|compare|contrast)\b.*\b(concept|theory|principle|relativity|quantum|evolution|consciousness)\b",  # noqa: E501
        r"\b(explain|describe|what is)\s+(the\s+)?(relativity|quantum|evolution|consciousness|string theory|dark matter|black hole)\b",  # noqa: E501
        r"\b(solve|calculate|compute|evaluate|derive)\b",
        r"\b(what is|explain)\s+(the\s+)?(difference|relationship|connection)\b",
        r"\b(step[-\s]by[-\s]step|chain[-\s]of[-\s]thought)\b",
        r"\b(logical|deductive|inductive|abductive)\s+reasoning\b",
    ]

    MATH_PATTERNS = [
        r"\b(solve|calculate|compute|evaluate|integrate|differentiate|derive)\b.*\b(equation|formula|expression|integral|derivative|value|result)\b",
        r"\b\d+\s*[+\-*/^]\s*\d+(\s*[+\-*/^]\s*\d+)*(\s*=|\s*\?)",
        r"\b(solve|calculate|compute)\s+\d+",
        r"\b(algebra|calculus|geometry|trigonometry|statistics|probability)\s+(problem|equation|proof|theorem|formula)\b",
        r"\b(math|mathematical)\s+(problem|equation|proof|theorem|calculation)\b",
        r"\bquadratic|differential|linear\s+algebra|fourier|laplace\b",
    ]

    VISION_PATTERNS = [
        r"\b(describe|analyze|explain)\s+(this\s+)?(image|picture|photo|screenshot|diagram|chart)\b",
        r"\bwhat.*(see|show|display|depict|illustrate)\b.*\b(image|picture)\b",
        r"\b(image|visual|vision|multimodal)\s*(understanding|analysis|recognition)\b",
        r"\b(OCR|optical|text.*image|document.*scan)\b",
    ]

    AUDIO_PATTERNS = [
        r"\b(transcribe|speech|audio|voice|listen|recording)\b",
        r"\b(text[-\s]to[-\s]speech|speech[-\s]to[-\s]text|TTS|STT)\b",
        r"\b(whisper|bark|xtts)\b",
    ]

    AGENT_PATTERNS = [
        r"\b(use|call|invoke|execute)\s+(tool|function|api|command)\b",
        r"\b(search|lookup|find|query)\s+(the\s+)?(web|database|internet|api)\b",
        r"\b(autonomous|agent|multi[-\s]step|workflow)\b",
        r"\b(function\s*calling|tool\s*use)\b",
    ]

    CODE_PATTERNS_COMPILED = []

    @classmethod
    def classify(cls, messages: list[dict]) -> TaskType:
        if not messages:
            return TaskType.GENERAL
        text = " ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str))
        return cls._classify_text(text)

    @classmethod
    def _classify_text(cls, text: str) -> TaskType:
        if not text:
            return TaskType.GENERAL
        scores = {task: 0 for task in TaskType}
        for pattern in cls.CODE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[TaskType.CODE] += 2
                break
        for pattern in cls.REASONING_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[TaskType.REASONING] += 2
                break
        for pattern in cls.MATH_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[TaskType.MATH] += 3
                scores[TaskType.REASONING] += 1
                break
        for pattern in cls.VISION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[TaskType.VISION] += 3
                break
        for pattern in cls.AUDIO_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[TaskType.AUDIO] += 3
                break
        for pattern in cls.AGENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[TaskType.AGENT] += 3
                break

        summarize_words = ["summarize", "summary", "tl;dr", "gist", "key points", "brief"]
        if any(w in text.lower() for w in summarize_words):
            scores[TaskType.SUMMARIZATION] += 2

        translate_words = ["translate", "translation", "convert to"]
        if any(w in text.lower() for w in translate_words):
            scores[TaskType.TRANSLATION] += 2

        if "embed" in text.lower() or "vector" in text.lower() or "semantic search" in text.lower():
            scores[TaskType.EMBEDDINGS] += 3

        rag_words = [
            "rag",
            "retrieval augmented",
            "knowledge base",
            "document search",
            "hybrid search",
        ]
        if any(w in text.lower() for w in rag_words):
            scores[TaskType.RAG] += 3

        max_score = max(scores.values())
        if max_score == 0:
            return TaskType.CHAT
        if scores[TaskType.AUDIO] > 0:
            return TaskType.AUDIO
        if scores[TaskType.VISION] > 0:
            return TaskType.VISION
        if scores[TaskType.EMBEDDINGS] > 0:
            return TaskType.EMBEDDINGS
        if scores[TaskType.RAG] > 0 and scores[TaskType.RAG] >= scores[TaskType.EMBEDDINGS]:
            return TaskType.RAG
        if scores[TaskType.AGENT] > 0:
            return TaskType.AGENT
        if scores[TaskType.MATH] > 0 and scores[TaskType.MATH] >= max(
            scores[TaskType.CODE], scores[TaskType.REASONING]
        ):
            return TaskType.MATH
        if scores[TaskType.CODE] >= 2:
            return TaskType.CODE
        if scores[TaskType.REASONING] >= 2:
            return TaskType.REASONING
        if scores[TaskType.SUMMARIZATION] > 0:
            return TaskType.SUMMARIZATION
        if scores[TaskType.TRANSLATION] > 0:
            return TaskType.TRANSLATION
        return TaskType.CHAT

    @classmethod
    def score_model_for_task(cls, task: TaskType, model) -> float:
        score = 0.0
        task_cap_map = {
            TaskType.CHAT: "chat",
            TaskType.CODE: "code",
            TaskType.REASONING: "reasoning",
            TaskType.MATH: "reasoning",
            TaskType.VISION: "vision",
            TaskType.AUDIO: "audio",
            TaskType.EMBEDDINGS: "embeddings",
            TaskType.AGENT: "agent",
            TaskType.RAG: "reasoning",
            TaskType.WRITING: "chat",
            TaskType.SUMMARIZATION: "chat",
            TaskType.TRANSLATION: "chat",
            TaskType.GENERAL: "chat",
        }
        cap = task_cap_map.get(task, "chat")
        if model.capabilities.get(cap, False):
            score += 10

        if task == TaskType.CODE and model.capabilities.get("code", False):
            if "code" in model.tags:
                score += 5
            if "reasoning" in model.tags:
                score += 3

        if task == TaskType.REASONING or task == TaskType.MATH:
            if model.capabilities.get("reasoning", False):
                score += 5
            if model.category == "reasoning":
                score += 3

        if task == TaskType.AGENT and model.capabilities.get("agent", False):
            score += 5

        latency_scores = {"real-time": 3, "interactive": 2, "batch": 0}
        score += latency_scores.get(model.latency_profile, 1)

        if task in (TaskType.AGENT, TaskType.CODE, TaskType.REASONING):
            if model.parameter_count.endswith("B"):
                try:
                    params = float(model.parameter_count.rstrip("B"))
                    if params >= 7:
                        score += 2
                    if params >= 30:
                        score += 1
                except ValueError:
                    pass

        return score

    @classmethod
    def best_model_for_task(cls, task: TaskType, max_ram: float = 32.0) -> str | None:
        candidates = ModelLibrary.recommend_for_task(task.value, max_ram)
        if not candidates:
            return None
        scored = [(cls.score_model_for_task(task, m), m) for m in candidates]
        scored.sort(key=lambda x: (-x[0], x[1].name))
        return scored[0][1].name if scored else None


class SmartRouter(InferenceEngine):
    def __init__(self, strategy: str = "task"):
        self._local: LocalInferenceEngine | None = None
        self._cloud: CloudInferenceEngine | None = None
        self.strategy = strategy
        self.classifier = TaskClassifier()

    @property
    def name(self) -> str:
        return "smart_router"

    async def _get_local(self) -> LocalInferenceEngine:
        if self._local is None:
            self._local = LocalInferenceEngine()
        return self._local

    async def _get_cloud(self) -> CloudInferenceEngine:
        if self._cloud is None:
            self._cloud = CloudInferenceEngine()
        return self._cloud

    async def _is_model_installed(self, model_name: str) -> bool:
        try:
            from superllm.models.registry import ModelRegistry

            registry = ModelRegistry.get_instance()
            installed = await registry.get_model(model_name)
            return installed is not None
        except Exception:
            return False

    async def _select_model(self, request: InferenceRequest) -> tuple[str, str]:
        model_name = request.model

        if model_name and model_name != "auto":
            if ":cloud" in model_name:
                return model_name, "cloud"
            is_installed = await self._is_model_installed(model_name)
            if is_installed:
                return model_name, "local"
            from superllm.models.library import ModelLibrary

            card = ModelLibrary.get_model(model_name)
            if card and card.source != "cloud":
                return model_name, "local"
            return model_name, "local"

        if settings.mode == Mode.cloud:
            return "qwen2.5-72b:cloud", "cloud"

        task = self.classifier.classify(request.messages)

        local_candidates = ModelLibrary.recommend_for_task(task.value, max_ram=32.0)
        local_candidates = [m for m in local_candidates if m.source != "cloud"]

        installed_local = []
        for m in local_candidates:
            if await self._is_model_installed(m.name):
                installed_local.append(m)

        candidates = installed_local or local_candidates

        if candidates:
            scored = [(self.classifier.score_model_for_task(task, m), m) for m in candidates]
            scored.sort(key=lambda x: (-x[0], x[1].name))
            best_local = scored[0][1]

            if settings.cloud_fallback and not installed_local:
                cloud_candidates = ModelLibrary.recommend_for_task(task.value, max_ram=999)
                cloud_candidates = [m for m in cloud_candidates if m.source == "cloud"]
                if cloud_candidates:
                    cloud_scored = [
                        (self.classifier.score_model_for_task(task, m), m) for m in cloud_candidates
                    ]
                    cloud_scored.sort(key=lambda x: (-x[0], x[1].name))
                    best_cloud = cloud_scored[0][1]
                    if cloud_scored[0][0] > scored[0][0] * 1.5:
                        return best_cloud.name, "cloud"

            return best_local.name, "local"

        fallback = ModelLibrary.search("qwen2.5-0.5b")
        if fallback:
            return fallback[0].name, "local"
        return "llama3.2-1b", "local"

    async def _cloud_fallback_model(self, original: str) -> str:
        if ":cloud" in original or "/" in original:
            return original
        cloud_candidates = [
            m for m in ModelLibrary.get_cloud_models() if m.capabilities.get("chat", False)
        ]
        if cloud_candidates:
            return cloud_candidates[0].name
        return "qwen2.5-72b:cloud"

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        model_name, engine_type = await self._select_model(request)
        request.model = model_name

        if engine_type == "cloud":
            engine = await self._get_cloud()
        else:
            engine = await self._get_local()

        try:
            return await engine.chat(request)
        except Exception as local_err:
            if settings.cloud_fallback and engine_type == "local":
                try:
                    cloud = await self._get_cloud()
                    request.model = await self._cloud_fallback_model(model_name)
                    return await cloud.chat(request)
                except Exception as cloud_err:
                    raise RuntimeError(
                        f"Local failed: {local_err}; Cloud fallback failed: {cloud_err}"
                    )
            raise

    async def chat_stream(self, request: InferenceRequest) -> AsyncGenerator[str, None]:
        model_name, engine_type = await self._select_model(request)
        request.model = model_name

        if engine_type == "cloud":
            engine = await self._get_cloud()
        else:
            engine = await self._get_local()

        try:
            async for chunk in engine.chat_stream(request):
                yield chunk
        except Exception as local_err:
            if settings.cloud_fallback and engine_type == "local":
                try:
                    cloud = await self._get_cloud()
                    request.model = await self._cloud_fallback_model(model_name)
                    async for chunk in cloud.chat_stream(request):
                        yield chunk
                except Exception as cloud_err:
                    raise RuntimeError(
                        f"Local stream failed: {local_err}; Cloud fallback failed: {cloud_err}"
                    )
            raise

    async def list_models(self) -> list[ModelInfo]:
        local_models = []
        cloud_models = []
        if settings.mode in (Mode.local, Mode.hybrid):
            try:
                engine = await self._get_local()
                local_models = await engine.list_models()
            except Exception:
                pass
        if settings.mode in (Mode.cloud, Mode.hybrid):
            try:
                engine = await self._get_cloud()
                cloud_models = await engine.list_models()
            except Exception:
                pass
        return local_models + cloud_models

    async def health(self) -> ProviderHealth:
        try:
            await self._get_cloud()
            await self._get_local()
            return ProviderHealth(
                name="smart_router",
                healthy=True,
                latency_ms=0,
            )
        except Exception as e:
            return ProviderHealth(
                name="smart_router",
                healthy=False,
                latency_ms=0,
                error=str(e),
            )

    async def close(self):
        if self._local:
            await self._local.close()
        if self._cloud:
            await self._cloud.close()
