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

import requests
from bs4 import BeautifulSoup

USER_AGENT = "aws-architecture-precedent-assistant/0.1 (+https://github.com/jameswagner/aws-architecture-precedent-assistant)"
REQUEST_DELAY_SECONDS = 0.3


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch_toc(session: requests.Session, base_url: str) -> dict:
    return session.get(base_url + "toc-contents.json", timeout=30).json()


def parse_page(html: str) -> tuple[str, str]:
    """Extract (title, text) from a page's main content region."""
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(id="main-col-body")
    if body is None:
        raise ValueError("page is missing #main-col-body — site structure may have changed")
    title_el = body.find(class_="topictitle")
    title = title_el.get_text(strip=True) if title_el else ""
    return title, body.get_text(" ", strip=True)
