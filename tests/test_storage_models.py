from superllm.storage.models import Conversation, InstalledModel, Message


def test_installed_model_to_dict():
    model = InstalledModel(
        name="test-model",
        path="/tmp/test.gguf",
        architecture="llama",
        parameter_count="7B",
        context_length=4096,
        size_bytes=4_000_000_000,
        quant="Q4_K_M",
        tags=["chat", "code"],
        capabilities={"chat": True, "code": True},
    )
    d = model.to_dict()
    assert d["name"] == "test-model"
    assert d["size_display"] == "3.73 GB"
    assert d["architecture"] == "llama"
    assert d["quant"] == "Q4_K_M"
    assert d["tags"] == ["chat", "code"]


def test_conversation_to_dict():
    conv = Conversation(id=1, title="Test Chat", model="llama-3.2-1b")
    d = conv.to_dict()
    assert d["title"] == "Test Chat"
    assert d["model"] == "llama-3.2-1b"
    assert d["message_count"] == 0


def test_message_to_dict():
    msg = Message(
        id=1,
        conversation_id=1,
        role="user",
        content="Hello!",
        tokens_in=10,
        tokens_out=0,
    )
    d = msg.to_dict()
    assert d["role"] == "user"
    assert d["content"] == "Hello!"
    assert d["tokens_in"] == 10


def test_size_format():
    assert InstalledModel._format_size(500) == "500 B"
    assert InstalledModel._format_size(2048) == "2.0 KB"
    assert InstalledModel._format_size(2_500_000) == "2.4 MB"
    assert "GB" in InstalledModel._format_size(4_000_000_000)
