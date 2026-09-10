from common.embeddings import DEFAULT_EMBEDDING_MODEL, get_embed_model


def test_get_embed_model_defaults(monkeypatch):
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)

    model = get_embed_model()

    assert model.model_name == DEFAULT_EMBEDDING_MODEL


def test_get_embed_model_respects_env_override(monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-large")

    model = get_embed_model()

    assert model.model_name == "text-embedding-3-large"
