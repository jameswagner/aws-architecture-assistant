"""Shared client for AWS's docs.aws.amazon.com doc-viewer platform.

Well-Architected Framework and Prescriptive Guidance patterns both run on
this platform — confirmed independently against live pages: same
toc-contents.json manifest per guide, same #main-col-body / h1.topictitle
content structure, both server-rendered (no headless browser needed).
This is the common client; per-source page selection (which nodes are
real content vs. navigation, how to derive metadata) stays in
ingest/sources/<name>.py since that varies by source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

USER_AGENT = "aws-architecture-precedent-assistant/0.1 (+https://github.com/jameswagner/aws-architecture-precedent-assistant)"
REQUEST_DELAY_SECONDS = 0.3
DOCS_DOMAIN = "https://docs.aws.amazon.com"


@dataclass
class Section:
    heading: str | None  # None for content before the first <h2>, or a page with none at all
    text: str
    images: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ParsedPage:
    title: str
    sections: list[Section]


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch_toc(session: requests.Session, base_url: str) -> dict:
    return session.get(base_url + "toc-contents.json", timeout=30).json()


def get_page(session: requests.Session, url: str) -> requests.Response:
    """GET a page with the encoding bug worked around.

    These pages omit charset from their Content-Type header (confirmed
    live), so requests falls back to ISO-8859-1 per the HTTP spec even
    though the actual content is UTF-8 (also confirmed live) — without
    this, non-ASCII characters like non-breaking spaces come through as
    mojibake, degrading both embedding quality and citation display.
    """
    response = session.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response


def parse_page(html: str) -> ParsedPage:
    """Split a page's main content region into sections on <h2> boundaries.

    Headings and their content are flat siblings under #main-col-body on
    this platform (confirmed against live pages), not nested per-section
    wrappers, which is what makes this walk straightforward. Pages with no
    <h2> at all (confirmed true of Well-Architected's framework guide —
    see docs/chunking_strategy.md) produce a single heading=None section
    holding the whole page, so downstream chunking doesn't need to special-
    case sourceless structure.

    Diagrams (<img>) would otherwise be silently dropped — get_text()
    ignores them entirely, alt text included. Alt text is folded into the
    section's text so retrieval can match on it; image URLs are kept
    per-section so a diagram can be surfaced as supporting precedent even
    when alt text is missing or unhelpful.
    """
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(id="main-col-body")
    if body is None:
        raise ValueError("page is missing #main-col-body — site structure may have changed")
    title_el = body.find(class_="topictitle")
    title = title_el.get_text(strip=True) if title_el else ""

    sections: list[Section] = []
    heading: str | None = None
    texts: list[str] = []
    images: list[dict[str, str]] = []

    def flush() -> None:
        text = " ".join(t for t in texts if t)
        alt_descriptions = " ".join(f"[Diagram: {img['alt']}]" for img in images if img["alt"])
        if alt_descriptions:
            text = f"{text} {alt_descriptions}" if text else alt_descriptions
        if text or images:
            sections.append(Section(heading=heading, text=text, images=list(images)))

    for child in body.find_all(recursive=False):
        if child.name in ("h1", "awsdocs-copyright", "awsdocs-thumb-feedback"):
            continue
        if child.name == "h2":
            flush()
            heading = child.get_text(strip=True)
            texts = []
            images = []
            continue
        text = child.get_text(" ", strip=True)
        if text:
            texts.append(text)
        for img in child.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            images.append({"url": urljoin(DOCS_DOMAIN, src), "alt": img.get("alt", "").strip()})

    flush()
    return ParsedPage(title=title, sections=sections)


def page_to_raw_fields(parsed: ParsedPage) -> tuple[str, dict]:
    """Flatten a ParsedPage into (content, metadata) for a RawDocument.

    content is all sections' text concatenated, for simple full-text use.
    metadata["sections"] preserves the per-section breakdown so a later
    chunking step (see common/chunking.py) can split structure-aware
    instead of only on a fixed token window; metadata["images"] is the
    flattened list across all sections, for surfacing diagrams regardless
    of how a page ends up chunked.
    """
    content = " ".join(s.text for s in parsed.sections if s.text)
    all_images = [img for s in parsed.sections for img in s.images]
    metadata: dict = {
        "sections": [{"heading": s.heading, "text": s.text, "images": s.images} for s in parsed.sections],
    }
    if all_images:
        metadata["images"] = all_images
    return content, metadata
