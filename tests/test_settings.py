from superllm.config.settings import Settings, Mode


def test_default_mode_is_local():
    s = Settings()
    assert s.mode == Mode.local


def test_default_port():
    s = Settings()
    assert s.port == 8080


def test_default_host():
    s = Settings()
    assert s.host == "127.0.0.1"


def test_local_inference_enabled_by_default():
    s = Settings()
    assert s.local_inference is True


def test_ui_enabled_by_default():
    s = Settings()
    assert s.ui_enabled is True


def test_auth_disabled_by_default():
    s = Settings()
    assert s.auth_enabled is False


def test_all_modes():
    assert Mode.local.value == "local"
    assert Mode.cloud.value == "cloud"
    assert Mode.hybrid.value == "hybrid"
