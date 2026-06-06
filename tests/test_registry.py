from superllm.providers.base import Provider
from superllm.providers.registry import registry


def test_provider_creation():
    p = Provider(
        name="test-provider",
        provider_type="openai",
        base_url="https://api.openai.com",
    )
    assert p.name == "test-provider"
    assert p.provider_type == "openai"
    assert p.is_enabled is True
    assert p.priority == 0
