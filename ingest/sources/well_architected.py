"""Well-Architected Framework ingester.

Access: requests + BS4 over static HTML on docs.aws.amazon.com — the page
markup is server-rendered (verified against the live site), no headless
browser needed. Page list comes from the guide's own toc-contents.json
manifest rather than a hardcoded/guessed URL list, so it tracks the real
site structure.
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

import requests
from bs4 import BeautifulSoup

from ..base import RawDocument

BASE_URL = "https://docs.aws.amazon.com/wellarchitected/latest/framework/"
TOC_URL = BASE_URL + "toc-contents.json"
USER_AGENT = "aws-architecture-precedent-assistant/0.1 (+https://github.com/jameswagner/aws-architecture-precedent-assistant)"
REQUEST_DELAY_SECONDS = 0.3

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


def _parse_page(html: str) -> tuple[str, str]:
    """Extract (title, text) from a page's main content region."""
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(id="main-col-body")
    if body is None:
        raise ValueError("page is missing #main-col-body — site structure may have changed")
    title_el = body.find(class_="topictitle")
    title = title_el.get_text(strip=True) if title_el else ""
    return title, body.get_text(" ", strip=True)


def fetch() -> list[RawDocument]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    toc = session.get(TOC_URL, timeout=30).json()
    today = date.today()
    documents = []

    for _, href, pillar in _iter_pages(toc):
        url = BASE_URL + href
        response = session.get(url, timeout=30)
        response.raise_for_status()
        title, text = _parse_page(response.text)
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
        time.sleep(REQUEST_DELAY_SECONDS)

    return documents
