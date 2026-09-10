"""Converts a RawDocument into LlamaIndex TextNodes per docs/chunking_strategy.md.

Structure-aware first: split on the sections a source's ingester already
identified (see ingest/aws_docs.py — heading=None for sources with no
internal structure, like Well-Architected), token-based splitting only as
a fallback within a section still too long.

Chroma requires flat scalar metadata — no nested lists or dicts — so
anything list-shaped (category_path, image URLs) gets JSON-serialized
here. This is the one place that constraint needs handling, not scattered
across every source ingester.

Node IDs are deterministic (hash of url + section heading + index within
section), not random, so re-chunking unchanged text reproduces the same
IDs — a prerequisite for detecting unchanged chunks on re-ingestion.
Each node also carries a content_hash: the ID proves stable addressing,
not that the text behind it is unchanged.
"""

from __future__ import annotations

import hashlib
import json

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from ingest.base import RawDocument

CHUNK_SIZE = 768
CHUNK_OVERLAP = 64


def _deterministic_id(url: str, heading: str | None, index: int) -> str:
    raw = f"{url}::{heading or ''}::{index}"
    return hashlib.sha256(raw.encode()).hexdigest()


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
        heading = section.get("heading")
        metadata = _base_metadata(doc, heading, section.get("images") or [])
        for i, piece in enumerate(splitter.split_text(text)):
            node_metadata = metadata.copy()
            node_metadata["content_hash"] = hashlib.sha256(piece.encode()).hexdigest()
            nodes.append(
                TextNode(id_=_deterministic_id(doc.url, heading, i), text=piece, metadata=node_metadata)
            )

    return nodes
