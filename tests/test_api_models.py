from pydantic import ValidationError
import pytest

from superllm.server.routes.models import PullRequest
from superllm.server.routes.chat import ChatRequest, Message


def test_pull_request_default():
    req = PullRequest(name="test", quantization="Q4_K_M")
    assert req.name == "test"
    assert req.quantization == "Q4_K_M"


def test_pull_request_default_quant():
    req = PullRequest(name="test")
    assert req.quantization == "Q4_K_M"


def test_chat_request_basic():
    req = ChatRequest(
        model="llama-3.2-1b",
        messages=[Message(role="user", content="Hello")],
    )
    assert req.model == "llama-3.2-1b"
    assert len(req.messages) == 1
    assert req.stream is False
    assert req.temperature == 0.7


def test_chat_request_stream():
    req = ChatRequest(
        model="test",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )
    assert req.stream is True


def test_chat_request_invalid_temperature():
    with pytest.raises(ValidationError):
        ChatRequest(
            model="test",
            messages=[Message(role="user", content="Hi")],
            temperature="hot",
        )


def test_chat_request_empty_messages():
    req = ChatRequest(model="test", messages=[])
    assert len(req.messages) == 0
