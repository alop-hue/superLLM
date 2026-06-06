from superllm.inference.base import InferenceRequest, InferenceResponse, ModelInfo, ProviderHealth


def test_inference_request_defaults():
    req = InferenceRequest(model="test", messages=[{"role": "user", "content": "hi"}])
    assert req.model == "test"
    assert req.temperature == 0.7
    assert req.max_tokens is None
    assert req.stream is False


def test_inference_request_custom():
    req = InferenceRequest(
        model="custom",
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.1,
        max_tokens=100,
        stream=True,
    )
    assert req.temperature == 0.1
    assert req.max_tokens == 100
    assert req.stream is True


def test_inference_response():
    resp = InferenceResponse(model="test", content="Hello!")
    assert resp.model == "test"
    assert resp.content == "Hello!"
    assert resp.finish_reason == "stop"


def test_model_info():
    info = ModelInfo(id="test-model")
    assert info.id == "test-model"
    assert info.object == "model"
    assert info.owned_by == "superllm"


def test_provider_health():
    health = ProviderHealth(name="local", healthy=True, latency_ms=10.5)
    assert health.healthy is True
    assert health.latency_ms == 10.5
    assert health.error is None
