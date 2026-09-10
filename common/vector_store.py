"""Persistent Chroma vector store.

Persistent, not in-memory, since a deployed tool needs the index to
survive restarts. Collection name is env-driven for the same reason the
embedding model is: a config change, not a code change, if it ever needs
to vary (e.g. a separate collection per embedding model to avoid mixing
incompatible vector spaces).
"""

from __future__ import annotations

import os
import pathlib

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

CHROMA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "chroma"
DEFAULT_COLLECTION_NAME = "aws_precedent"


def get_chroma_client(chroma_dir: pathlib.Path = CHROMA_DIR) -> chromadb.ClientAPI:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_dir))


def get_vector_store(chroma_dir: pathlib.Path = CHROMA_DIR) -> ChromaVectorStore:
    collection_name = os.environ.get("CHROMA_COLLECTION", DEFAULT_COLLECTION_NAME)
    client = get_chroma_client(chroma_dir)
    collection = client.get_or_create_collection(collection_name)
    return ChromaVectorStore(chroma_collection=collection)


def reset_vector_store(chroma_dir: pathlib.Path = CHROMA_DIR) -> ChromaVectorStore:
    """Delete the collection first, so a re-run replaces stale data instead
    of accumulating duplicates alongside it — node IDs aren't stable across
    runs, so get_or_create_collection alone would just keep adding rows."""
    collection_name = os.environ.get("CHROMA_COLLECTION", DEFAULT_COLLECTION_NAME)
    client = get_chroma_client(chroma_dir)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass  # fine if it didn't exist yet
    return ChromaVectorStore(chroma_collection=client.get_or_create_collection(collection_name))
