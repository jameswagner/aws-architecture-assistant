"""Config-driven synthesis LLM selection.

The pitch requires supporting a user-supplied key from OpenAI, Gemini, or
Claude — only OpenAI is wired up right now since that's the key already
configured for embeddings. Adding the other two is a config change to
this one factory, not a redesign, since it's the only place that needs
to know which provider is in use.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"


def get_llm() -> OpenAI:
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    return OpenAI(model=model)
