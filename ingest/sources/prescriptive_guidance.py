"""Prescriptive Guidance ingester.

Unlike the Well-Architected Framework, this guide's toc-contents.json is a
flat catalog under category listings, not one hierarchical document: only
leaf nodes (no children) are real pattern pages — every node with children
(e.g. "compute-pattern-list.html") is a pure navigation/topic-listing page
with no guidance content, confirmed against a live sample. Category path
is preserved as metadata since there's no single "pillar" equivalent here.
License: CC-BY-SA-4.0.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from datetime import date

from .. import aws_docs
from ..base import RawDocument

BASE_URL = "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/"


def _iter_pages(toc: dict) -> Iterator[tuple[str, str, tuple[str, ...]]]:
    """Yield (title, href, category_path) for every leaf (real content) page."""

    def walk(nodes: list[dict], path: tuple[str, ...]) -> Iterator[tuple[str, str, tuple[str, ...]]]:
        for node in nodes:
            children = node.get("contents", [])
            if not children:
                yield node["title"], node["href"], path
            else:
                yield from walk(children, path + (node["title"],))

    yield from walk(toc["contents"], ())


def fetch() -> list[RawDocument]:
    session = aws_docs.new_session()
    toc = aws_docs.fetch_toc(session, BASE_URL)
    today = date.today()
    documents = []

    for _, href, category_path in _iter_pages(toc):
        url = BASE_URL + href
        response = aws_docs.get_page(session, url)
        parsed = aws_docs.parse_page(response.text)
        content, metadata = aws_docs.page_to_raw_fields(parsed)
        if category_path:
            metadata["category_path"] = list(category_path)
        documents.append(
            RawDocument(
                source="prescriptive_guidance",
                title=parsed.title,
                url=url,
                content=content,
                fetched_on=today,
                metadata=metadata,
            )
        )
        time.sleep(aws_docs.REQUEST_DELAY_SECONDS)

    return documents
