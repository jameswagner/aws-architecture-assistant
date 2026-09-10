from llama_index.core.schema import TextNode

from common.vector_store import DEFAULT_COLLECTION_NAME, get_chroma_client, get_vector_store, reset_vector_store


def test_get_chroma_client_creates_persistent_dir(tmp_path):
    chroma_dir = tmp_path / "chroma"

    client = get_chroma_client(chroma_dir)

    assert chroma_dir.exists()
    assert client.heartbeat() is not None


def test_get_vector_store_uses_default_collection(tmp_path, monkeypatch):
    monkeypatch.delenv("CHROMA_COLLECTION", raising=False)

    get_vector_store(tmp_path / "chroma")
    client = get_chroma_client(tmp_path / "chroma")

    assert DEFAULT_COLLECTION_NAME in [c.name for c in client.list_collections()]


def test_get_vector_store_respects_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("CHROMA_COLLECTION", "custom_collection")

    get_vector_store(tmp_path / "chroma")
    client = get_chroma_client(tmp_path / "chroma")

    assert "custom_collection" in [c.name for c in client.list_collections()]


def test_reset_vector_store_clears_existing_data(tmp_path):
    chroma_dir = tmp_path / "chroma"
    vector_store = get_vector_store(chroma_dir)
    vector_store.add([TextNode(text="stale data", embedding=[0.0] * 8)])
    assert vector_store.client.count() == 1

    reset_vector_store(chroma_dir)

    client = get_chroma_client(chroma_dir)
    assert client.get_collection(DEFAULT_COLLECTION_NAME).count() == 0


def test_reset_vector_store_is_safe_when_collection_does_not_exist_yet(tmp_path):
    reset_vector_store(tmp_path / "chroma")  # should not raise
