"""Query the index without any LLM synthesis.

Phase 1 returns raw retrieved passages with citations only — no answer
generation. That's Phase 3's job, once there's an eval set to judge
synthesis quality against, not this one.
"""

from __future__ import annotations

from llama_index.core import StorageContext, VectorStoreIndex

from common.embeddings import get_embed_model
from common.vector_store import get_vector_store


def load_index() -> VectorStoreIndex:
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store, embed_model=get_embed_model(), storage_context=storage_context
    )


def retrieve(index: VectorStoreIndex, query: str, top_k: int = 5) -> list[dict]:
    retriever = index.as_retriever(similarity_top_k=top_k)
    return [
        {
            "text": node.get_content(),
            "score": node.score,
            "title": node.metadata.get("title"),
            "url": node.metadata.get("url"),
            "section": node.metadata.get("section"),
        }
        for node in retriever.retrieve(query)
    ]
