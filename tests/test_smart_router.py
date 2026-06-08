from superllm.inference.smart_router import TaskClassifier, SmartRouter
from superllm.models.library import ModelLibrary, LITELLM_MODEL_MAP


def test_task_classifier_chat():
    tc = TaskClassifier()
    assert tc.classify([{"role": "user", "content": "hello how are you?"}]).value == "chat"
    assert tc.classify([{"role": "user", "content": "what is the weather like?"}]).value == "chat"
    assert tc.classify([{"role": "user", "content": "tell me a fun fact"}]).value == "chat"


def test_task_classifier_code():
    tc = TaskClassifier()
    assert tc.classify([{"role": "user", "content": "write a python function to sort a list"}]).value == "code"
    assert tc.classify([{"role": "user", "content": "implement a binary search in rust"}]).value == "code"
    assert tc.classify([{"role": "user", "content": "debug this function"}]).value == "code"


def test_task_classifier_reasoning():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "explain the concept of relativity"}])
    assert result.value == "reasoning"


def test_task_classifier_math():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "solve the equation 2x + 5 = 15"}])
    assert result.value == "math"


def test_task_classifier_vision():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "analyze this image for me"}])
    assert result.value == "vision"


def test_task_classifier_embeddings():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "generate embedding for this text"}])
    assert result.value == "embeddings"


def test_task_classifier_agent():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "search the web for climate news"}])
    assert result.value == "agent"


def test_task_classifier_summarization():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "summarize this article for me"}])
    assert result.value == "summarization"


def test_task_classifier_translation():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "translate hello to spanish"}])
    assert result.value == "translation"


def test_task_classifier_rag():
    tc = TaskClassifier()
    result = tc.classify([{"role": "user", "content": "rag search for climate data"}])
    assert result.value == "rag"


def test_task_classifier_defaults_to_chat():
    tc = TaskClassifier()
    assert tc.classify([{"role": "user", "content": "what do you think about ai?"}]).value == "chat"


def test_litellm_map_count():
    assert len(LITELLM_MODEL_MAP) >= 30


def test_litellm_map_keys():
    expected_keys = {"gpt-4o:cloud", "claude-3.5-sonnet:cloud", "gemini-2.0-flash:cloud",
                     "deepseek-v3:cloud", "qwen2.5-72b:cloud"}
    assert expected_keys.issubset(LITELLM_MODEL_MAP.keys())


def test_cloud_fallback_resolution():
    from superllm.inference.cloud import CloudInferenceEngine
    ce = CloudInferenceEngine()
    assert ce._resolve_model("qwen2-0.5b") == "together_ai/Qwen/Qwen2.5-72B-Instruct-Turbo"
    assert ce._resolve_model("deepseek-coder-33b") == "together_ai/deepseek-ai/DeepSeek-V3-0324"
    assert ce._resolve_model("gpt-4o:cloud") == "openai/gpt-4o"
    assert "/" in ce._resolve_model("llama3.2-1b")


import pytest


@pytest.mark.asyncio
async def test_smart_router_cloud_fallback():
    router = SmartRouter()
    result = await router._cloud_fallback_model("qwen2-0.5b")
    assert result is not None


def test_resolve_download_url_all_local_models():
    from superllm.models.library import BUILTIN_LIBRARY
    urls_found = 0
    urls_missing = []
    for name, card in BUILTIN_LIBRARY.items():
        if card.source == "local":
            url = card.url or ModelLibrary.resolve_download_url(name)
            if url:
                urls_found += 1
                assert url.startswith("https://huggingface.co/"), f"Model '{name}' URL is not a HuggingFace URL: {url}"
            else:
                urls_missing.append(name)
    assert urls_found >= 25, f"Only {urls_found} models have URLs; missing: {urls_missing[:10]}..."
    assert len(urls_missing) <= 120, f"Too many models without URLs: {len(urls_missing)}"
