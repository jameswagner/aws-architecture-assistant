"""AWS Solutions Library ingester.

Solutions Library implementation guides run on the same docs.aws.amazon.com
doc-viewer platform as Well-Architected/Prescriptive Guidance (confirmed
live: toc-contents.json, #main-col-body, .topictitle all present under
docs.aws.amazon.com/solutions/latest/<slug>/) — no new parsing needed,
only ingest/aws_docs.py's existing client.

Unlike WA/PG, there's no single guide to point at: each solution is its
own independent guide under a different slug, and there's no static page
listing them all (the aws.amazon.com/solutions/ browse grid is populated
by a client-side widget). Slugs are discovered instead from AWS's site-wide
sitemap index, filtered to the English-locale solutions/latest/ entries —
a distinct, smaller set (62) from the much larger single-page "Guidance"
library, which is out of scope here.
"""

from __future__ import annotations

import re
import time
from datetime import date

import requests

from .. import aws_docs
from ..base import RawDocument

SITEMAP_URL = "https://docs.aws.amazon.com/sitemap_index.xml"
BASE_URL = "https://docs.aws.amazon.com/solutions/latest/"

_SLUG_PATTERN = re.compile(r"https://docs\.aws\.amazon\.com/solutions/latest/([a-zA-Z0-9-]+)/sitemap\.xml")

SKIP_TOP_LEVEL_SECTIONS = {"Glossary", "Revisions", "Notices"}


def _parse_solution_slugs(sitemap_xml: str) -> list[str]:
    """Extract English-locale solution slugs from the site-wide sitemap index.

    Matches only bare solutions/latest/<slug>/sitemap.xml entries — locale
    variants (de_de/solutions/latest/..., etc.) have the domain immediately
    followed by a locale segment instead of "solutions", so the pattern
    anchored on ".com/solutions/latest/" excludes them without needing to
    enumerate locales.
    """
    return sorted(set(_SLUG_PATTERN.findall(sitemap_xml)))


def _discover_slugs(session) -> list[str]:
    response = session.get(SITEMAP_URL, timeout=30)
    response.raise_for_status()
    return _parse_solution_slugs(response.text)


def fetch() -> list[RawDocument]:
    session = aws_docs.new_session()
    slugs = _discover_slugs(session)
    today = date.today()
    documents = []

    for slug in slugs:
        guide_url = f"{BASE_URL}{slug}/"
        try:
            toc = aws_docs.fetch_toc(session, guide_url)
        except (requests.RequestException, ValueError):
            print(f"  skipping {slug}: no toc-contents.json")
            continue

        for title, href, _ in _iter_pages(toc):
            url = guide_url + href
            response = aws_docs.get_page(session, url)
            parsed = aws_docs.parse_page(response.text)
            content, metadata = aws_docs.page_to_raw_fields(parsed)
            metadata["solution"] = slug
            documents.append(
                RawDocument(
                    source="solutions_library",
                    title=parsed.title,
                    url=url,
                    content=content,
                    fetched_on=today,
                    metadata=metadata,
                )
            )
            time.sleep(aws_docs.REQUEST_DELAY_SECONDS)

    return documents


def _iter_pages(toc: dict):
    """Yield (title, href, None) for every real content page in a solution's guide.

    Unlike Prescriptive Guidance, every node here is real content, not a
    pure navigation/category label — confirmed live: even parent nodes
    like "Deploy the solution" have their own real page — so every node
    below the top-level skip list is yielded, children included.
    """

    def walk(nodes: list[dict]):
        for node in nodes:
            yield node["title"], node["href"], None
            yield from walk(node.get("contents", []))

    for node in toc["contents"]:
        if node["title"] in SKIP_TOP_LEVEL_SECTIONS:
            continue
        yield from walk([node])
