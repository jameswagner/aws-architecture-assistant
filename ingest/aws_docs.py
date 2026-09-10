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

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

USER_AGENT = "aws-architecture-precedent-assistant/0.1 (+https://github.com/jameswagner/aws-architecture-precedent-assistant)"
REQUEST_DELAY_SECONDS = 0.3
DOCS_DOMAIN = "https://docs.aws.amazon.com"


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch_toc(session: requests.Session, base_url: str) -> dict:
    return session.get(base_url + "toc-contents.json", timeout=30).json()


def parse_page(html: str) -> tuple[str, str, list[dict[str, str]]]:
    """Extract (title, text, images) from a page's main content region.

    Diagrams embedded in AWS docs pages (e.g. a pattern's "Architecture"
    section) would otherwise be silently dropped — get_text() ignores
    <img> tags entirely, alt text included. Alt text is folded into the
    returned text so retrieval can match on it; image URLs are returned
    separately so they can be surfaced as supporting precedent even when
    alt text is missing or unhelpful.
    """
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(id="main-col-body")
    if body is None:
        raise ValueError("page is missing #main-col-body — site structure may have changed")
    title_el = body.find(class_="topictitle")
    title = title_el.get_text(strip=True) if title_el else ""

    images = []
    for img in body.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        images.append({"url": urljoin(DOCS_DOMAIN, src), "alt": img.get("alt", "").strip()})

    text = body.get_text(" ", strip=True)
    alt_descriptions = " ".join(f"[Diagram: {img['alt']}]" for img in images if img["alt"])
    if alt_descriptions:
        text = f"{text} {alt_descriptions}"

    return title, text, images
