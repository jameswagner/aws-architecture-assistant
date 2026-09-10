"""Persistent Chroma vector store, following the lesson 5 pattern.

Persistent (not the in-memory SimpleVectorStore lesson 4 used) since a
deployed tool needs the index to survive restarts. Collection name is
env-driven for the same reason the embedding model is: a config change,
not a code change, if it ever needs to vary (e.g. a separate collection
per embedding model to avoid mixing incompatible vector spaces).
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
