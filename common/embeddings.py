"""Config-driven embedding model selection.

Provider is fixed to OpenAI for now — no evidence yet another provider is
needed (see docs/plan.md's "plug-and-play" discussion). Model name is
env-driven so swapping it later is a config change, not a code change,
since re-embedding the whole corpus is the expensive part of changing
this — unlike the vector store, which LlamaIndex already makes swappable.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def get_embed_model() -> OpenAIEmbedding:
    model = os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    return OpenAIEmbedding(model=model)
