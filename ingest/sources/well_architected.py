"""Well-Architected Framework ingester.

Page list comes from the guide's own toc-contents.json manifest rather
than a hardcoded/guessed URL list, so it tracks the real site structure.
License: CC-BY-SA-4.0.

Skips pure navigational/legal sections (contributors, notices, glossary,
document revisions) — not architecture guidance. Pillar is derived from
position in the TOC tree, not inferred, per the standing risk in
docs/plan.md that these mappings must be real lookups.

Two separate top-level sections are organized one-subtree-per-pillar:
"The pillars of the framework" (summary content) AND "Appendix: Questions
and best practices" (the deeper per-question/per-best-practice pages,
confirmed live — e.g. "PERF02-BP01 Select the best compute options").
Detected structurally (a section whose children are exactly the six
pillar names), not by hardcoding both title strings, so a third such
section wouldn't silently lose pillar tagging the way relying on a single
hardcoded title did originally.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from datetime import date

from .. import aws_docs
from ..base import RawDocument

BASE_URL = "https://docs.aws.amazon.com/wellarchitected/latest/framework/"

PILLAR_NAMES = {
    "Operational excellence",
    "Security",
    "Reliability",
    "Performance efficiency",
    "Cost optimization",
    "Sustainability",
}
SKIP_TOP_LEVEL_SECTIONS = {"Contributors", "Notices", "AWS Glossary", "Document revisions"}


def _walk(node: dict, pillar: str | None) -> Iterator[tuple[str, str, str | None]]:
    yield node["title"], node["href"], pillar
    for child in node.get("contents", []):
        yield from _walk(child, pillar)


def _is_pillar_organized(section: dict) -> bool:
    children = section.get("contents", [])
    return bool(children) and all(child["title"] in PILLAR_NAMES for child in children)


def _iter_pages(toc: dict) -> Iterator[tuple[str, str, str | None]]:
    """Yield (title, href, pillar) for every real page in the guide, pillar=None where n/a."""
    for section in toc["contents"]:
        if section["title"] in SKIP_TOP_LEVEL_SECTIONS:
            continue
        if _is_pillar_organized(section):
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
        response = aws_docs.get_page(session, url)
        parsed = aws_docs.parse_page(response.text)
        content, metadata = aws_docs.page_to_raw_fields(parsed)
        if pillar:
            metadata["pillar"] = pillar
        documents.append(
            RawDocument(
                source="well_architected",
                title=parsed.title,
                url=url,
                content=content,
                fetched_on=today,
                metadata=metadata,
            )
        )
        time.sleep(aws_docs.REQUEST_DELAY_SECONDS)

    return documents
