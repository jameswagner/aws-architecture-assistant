"""Well-Architected Framework ingester.

Page list comes from the guide's own toc-contents.json manifest rather
than a hardcoded/guessed URL list, so it tracks the real site structure.
License: CC-BY-SA-4.0.

Skips pure navigational/legal sections (contributors, notices, glossary,
document revisions) — not architecture guidance. Pillar is derived from
position in the TOC tree, not inferred, per the standing risk in
docs/plan.md that these mappings must be real lookups.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from datetime import date

from .. import aws_docs
from ..base import RawDocument

BASE_URL = "https://docs.aws.amazon.com/wellarchitected/latest/framework/"

PILLARS_SECTION_TITLE = "The pillars of the framework"
SKIP_TOP_LEVEL_SECTIONS = {"Contributors", "Notices", "AWS Glossary", "Document revisions"}


def _walk(node: dict, pillar: str | None) -> Iterator[tuple[str, str, str | None]]:
    yield node["title"], node["href"], pillar
    for child in node.get("contents", []):
        yield from _walk(child, pillar)


def _iter_pages(toc: dict) -> Iterator[tuple[str, str, str | None]]:
    """Yield (title, href, pillar) for every real page in the guide, pillar=None where n/a."""
    for section in toc["contents"]:
        if section["title"] in SKIP_TOP_LEVEL_SECTIONS:
            continue
        if section["title"] == PILLARS_SECTION_TITLE:
            for pillar_node in section["contents"]:
                yield from _walk(pillar_node, pillar=pillar_node["title"])
        else:
            yield from _walk(section, pillar=None)


def fetch() -> list[RawDocument]:
    session = aws_docs.new_session()
    toc = aws_docs.fetch_toc(session, BASE_URL)
    today = date.today()
    documents = []

    for _, href, pillar in _iter_pages(toc):
        url = BASE_URL + href
        response = session.get(url, timeout=30)
        response.raise_for_status()
        title, text = aws_docs.parse_page(response.text)
        documents.append(
            RawDocument(
                source="well_architected",
                title=title,
                url=url,
                content=text,
                fetched_on=today,
                metadata={"pillar": pillar} if pillar else {},
            )
        )
        time.sleep(aws_docs.REQUEST_DELAY_SECONDS)

    return documents
