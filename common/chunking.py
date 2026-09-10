"""Converts a RawDocument into LlamaIndex TextNodes per docs/chunking_strategy.md.

Structure-aware first: split on the sections a source's ingester already
identified (see ingest/aws_docs.py — heading=None for sources with no
internal structure, like Well-Architected), token-based splitting only as
a fallback within a section still too long.

Chroma requires flat scalar metadata — no nested lists or dicts — so
anything list-shaped (category_path, image URLs) gets JSON-serialized
here. This is the one place that constraint needs handling, not scattered
across every source ingester.
"""

from __future__ import annotations

import json

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from ingest.base import RawDocument

CHUNK_SIZE = 768
CHUNK_OVERLAP = 64


def _base_metadata(doc: RawDocument, heading: str | None, images: list[dict]) -> dict:
    metadata: dict = {
        "source": doc.source,
        "title": doc.title,
        "url": doc.url,
        "fetched_on": doc.fetched_on.isoformat(),
    }
    if heading:
        metadata["section"] = heading
    for key, value in doc.metadata.items():
        if key in ("sections", "images"):
            continue  # sections is consumed below, per-section images handled separately
        metadata[key] = json.dumps(value) if isinstance(value, (list, dict)) else value
    if images:
        metadata["image_urls"] = json.dumps([img["url"] for img in images])
    return metadata


def chunk_document(doc: RawDocument) -> list[TextNode]:
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    sections = doc.metadata.get("sections") or [
        {"heading": None, "text": doc.content, "images": doc.metadata.get("images", [])}
    ]

    nodes = []
    for section in sections:
        text = section.get("text", "")
        if not text:
            continue
        metadata = _base_metadata(doc, section.get("heading"), section.get("images") or [])
        for piece in splitter.split_text(text):
            nodes.append(TextNode(text=piece, metadata=metadata.copy()))

    return nodes
