"""Query the index without any LLM synthesis.

Phase 1 returns raw retrieved passages with citations only — no answer
generation. That's Phase 3's job, once there's an eval set to judge
synthesis quality against, not this one.
"""

from __future__ import annotations

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.retrievers.bm25 import BM25Retriever

from common.embeddings import get_embed_model
from common.vector_store import get_vector_store

# BM25 tokenizes and scores the whole corpus at build time, so this is cached
# per loaded index rather than rebuilt on every retrieve() call.
_bm25_retriever_cache: dict[int, BM25Retriever] = {}


def load_index() -> VectorStoreIndex:
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store, embed_model=get_embed_model(), storage_context=storage_context
    )


def _get_bm25_retriever(index: VectorStoreIndex) -> BM25Retriever:
    cache_key = id(index)
    if cache_key not in _bm25_retriever_cache:
        nodes = index.vector_store.get_nodes(node_ids=None)
        _bm25_retriever_cache[cache_key] = BM25Retriever.from_defaults(nodes=nodes)
    return _bm25_retriever_cache[cache_key]


def retrieve(index: VectorStoreIndex, query: str, top_k: int = 5, hybrid: bool = True) -> list[dict]:
    if hybrid:
        # Over-fetch from each retriever before fusing, so a node that's
        # merely decent in both lists has room to outrank one that's only
        # strong in a single list.
        candidate_k = max(top_k * 4, 20)
        vector_retriever = index.as_retriever(similarity_top_k=candidate_k)

        bm25_retriever = _get_bm25_retriever(index)
        bm25_retriever.similarity_top_k = candidate_k

        fusion_retriever = QueryFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            mode=FUSION_MODES.RECIPROCAL_RANK,
            similarity_top_k=top_k,
            num_queries=1,  # fuse only these two retrievers' own results, no LLM query rewrites
            use_async=False,
        )
        nodes = fusion_retriever.retrieve(query)
    else:
        nodes = index.as_retriever(similarity_top_k=top_k).retrieve(query)

    return [
        {
            "text": node.get_content(),
            "score": node.score,
            "title": node.metadata.get("title"),
            "url": node.metadata.get("url"),
            "section": node.metadata.get("section"),
            "source": node.metadata.get("source"),
        }
        for node in nodes
    ]
