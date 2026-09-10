"""Data-collection entrypoint: fetch both sources, chunk, embed, persist to Chroma.

Costs a small amount on OPENAI_API_KEY for embeddings (see README for the
estimate) — this is a one-time data-collection step, not something that
runs automatically or on a deployed user's key. Not run in CI.

Usage: python build_index.py
"""

from __future__ import annotations

from llama_index.core import StorageContext, VectorStoreIndex

from common.chunking import chunk_document
from common.embeddings import get_embed_model
from common.vector_store import get_vector_store
from ingest.sources import prescriptive_guidance, well_architected


def build_index() -> VectorStoreIndex:
    print("Fetching Well-Architected Framework...")
    documents = well_architected.fetch()
    print(f"  {len(documents)} pages")

    print("Fetching Prescriptive Guidance...")
    pg_documents = prescriptive_guidance.fetch()
    print(f"  {len(pg_documents)} pages")
    documents += pg_documents

    print("Chunking...")
    nodes = [node for doc in documents for node in chunk_document(doc)]
    print(f"  {len(nodes)} chunks from {len(documents)} pages")

    print("Embedding and persisting to Chroma...")
    storage_context = StorageContext.from_defaults(vector_store=get_vector_store())
    index = VectorStoreIndex(nodes, embed_model=get_embed_model(), storage_context=storage_context, show_progress=True)
    print("Done.")
    return index


if __name__ == "__main__":
    build_index()
