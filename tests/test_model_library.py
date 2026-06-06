from superllm.models.library import ModelLibrary


def test_search_returns_results():
    results = ModelLibrary.search()
    assert len(results) > 0


def test_search_llama():
    results = ModelLibrary.search("llama")
    assert len(results) > 0
    names = [m.name for m in results]
    assert any("llama" in n for n in names)


def test_get_model_exists():
    card = ModelLibrary.get_model("llama-3.2-1b")
    assert card is not None
    assert card.parameter_count == "1.24B"
    assert card.context_length == 8192


def test_get_model_nonexistent():
    card = ModelLibrary.get_model("nonexistent-model")
    assert card is None


def test_filter_by_category():
    chat_models = ModelLibrary.filter(category="chat")
    assert all(m.category == "chat" for m in chat_models)


def test_categories():
    cats = ModelLibrary.categories()
    assert "chat" in cats
    assert "general" in cats


def test_all_tags():
    tags = ModelLibrary.all_tags()
    assert "chat" in tags
    assert "lightweight" in tags


def test_recommend_for_hardware():
    models = ModelLibrary.recommend_for_hardware(4.0)
    assert len(models) > 0
    assert any(m.parameter_count == "0.49B" for m in models)


def test_search_empty_returns_all():
    all_models = ModelLibrary.search()
    empty_search = ModelLibrary.search("")
    assert len(all_models) == len(empty_search)
