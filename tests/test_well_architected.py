from ingest.sources.well_architected import _iter_pages

SAMPLE_TOC = {
    "contents": [
        {
            "title": "Abstract and introduction",
            "href": "welcome.html",
            "contents": [
                {"title": "Definitions", "href": "definitions.html"},
            ],
        },
        {
            "title": "The pillars of the framework",
            "href": "the-pillars-of-the-framework.html",
            "contents": [
                {
                    "title": "Operational excellence",
                    "href": "operational-excellence.html",
                    "contents": [
                        {"title": "Design principles", "href": "oe-design-principles.html"},
                    ],
                },
                {
                    "title": "Security",
                    "href": "security.html",
                    "contents": [
                        {"title": "Design principles", "href": "sec-design.html"},
                    ],
                },
            ],
        },
        {
            "title": "Appendix: Questions and best practices",
            "href": "appendix.html",
            "contents": [
                {
                    "title": "Performance efficiency",
                    "href": "a-performance-efficiency.html",
                    "contents": [
                        {"title": "PERF 2. How do you select compute resources?", "href": "perf-02.html"},
                    ],
                },
            ],
        },
        {"title": "Contributors", "href": "contributors.html"},
    ]
}


def test_iter_pages_tags_pillar_from_toc_position():
    pages = list(_iter_pages(SAMPLE_TOC))
    by_href = {href: pillar for _, href, pillar in pages}

    assert by_href["definitions.html"] is None
    assert by_href["operational-excellence.html"] == "Operational excellence"
    assert by_href["oe-design-principles.html"] == "Operational excellence"
    assert by_href["sec-design.html"] == "Security"


def test_iter_pages_tags_pillar_in_any_pillar_organized_section():
    """Not just "The pillars of the framework" — any section whose children
    are exactly the pillar names, e.g. the deeper "Appendix" section, which
    also holds real per-best-practice pages.
    """
    pages = list(_iter_pages(SAMPLE_TOC))
    by_href = {href: pillar for _, href, pillar in pages}

    assert by_href["a-performance-efficiency.html"] == "Performance efficiency"
    assert by_href["perf-02.html"] == "Performance efficiency"


def test_iter_pages_skips_boilerplate_sections():
    pages = list(_iter_pages(SAMPLE_TOC))
    hrefs = {href for _, href, _ in pages}

    assert "contributors.html" not in hrefs
