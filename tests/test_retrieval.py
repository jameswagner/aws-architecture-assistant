from unittest.mock import MagicMock

import pytest
from llama_index.core.schema import NodeWithScore, TextNode

from common import retrieval
from common.retrieval import _get_bm25_retriever, retrieve


def _node(node_id: str, text: str, **metadata) -> NodeWithScore:
    return NodeWithScore(node=TextNode(id_=node_id, text=text, metadata=metadata), score=1.0)


class FakeRetriever:
    def __init__(self, nodes):
        self._nodes = nodes
        self.similarity_top_k = None

    def retrieve(self, query):
        return self._nodes


class FakeIndex:
    """Stands in for a VectorStoreIndex without touching real embeddings."""

    def __init__(self, vector_nodes):
        self._vector_nodes = vector_nodes
        self.as_retriever_calls: list[int] = []

    def as_retriever(self, similarity_top_k):
        self.as_retriever_calls.append(similarity_top_k)
        return FakeRetriever(self._vector_nodes[:similarity_top_k])


@pytest.fixture(autouse=True)
def clear_bm25_cache():
    retrieval._bm25_retriever_cache.clear()
    yield
    retrieval._bm25_retriever_cache.clear()


def test_retrieve_vector_only_formats_fields_and_skips_bm25(monkeypatch):
    index = FakeIndex([_node("n1", "IAM roles", url="https://x/a", title="A", section="S", source="well_architected")])
    get_bm25 = MagicMock()
    monkeypatch.setattr(retrieval, "_get_bm25_retriever", get_bm25)

    results = retrieve(index, "query", top_k=1, hybrid=False)

    assert results == [
        {
            "text": "IAM roles",
            "score": 1.0,
            "title": "A",
            "url": "https://x/a",
            "section": "S",
            "source": "well_architected",
        }
    ]
    get_bm25.assert_not_called()
    assert index.as_retriever_calls == [1]


def test_retrieve_hybrid_over_fetches_before_fusing(monkeypatch):
    vector_nodes = [_node(f"v{i}", f"vector node {i}") for i in range(3)]
    index = FakeIndex(vector_nodes)

    bm25_retriever = FakeRetriever([_node("b0", "keyword node 0")])
    monkeypatch.setattr(retrieval, "_get_bm25_retriever", lambda idx: bm25_retriever)

    retrieve(index, "query", top_k=2, hybrid=True)

    # candidate_k = max(top_k * 4, 20) = max(8, 20) = 20
    assert index.as_retriever_calls == [20]
    assert bm25_retriever.similarity_top_k == 20


def test_retrieve_hybrid_merges_ranked_lists_and_trims_to_top_k(monkeypatch):
    vector_nodes = [_node("shared", "text A"), _node("v-only", "text B")]
    bm25_nodes = [_node("shared", "text A"), _node("b-only", "text C")]
    index = FakeIndex(vector_nodes)
    monkeypatch.setattr(retrieval, "_get_bm25_retriever", lambda idx: FakeRetriever(bm25_nodes))

    results = retrieve(index, "query", top_k=2, hybrid=True)

    texts = [r["text"] for r in results]
    assert len(texts) == 2
    # ranked #1 in both lists, so RRF should place it ahead of a single-list node
    assert texts[0] == "text A"


def test_get_bm25_retriever_is_cached_per_index():
    index = MagicMock()
    index.vector_store.get_nodes.return_value = [TextNode(id_="n1", text="hello world")]

    first = _get_bm25_retriever(index)
    second = _get_bm25_retriever(index)

    assert first is second
    index.vector_store.get_nodes.assert_called_once()
