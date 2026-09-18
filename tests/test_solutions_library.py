from ingest.sources.solutions_library import _iter_pages, _parse_solution_slugs

SAMPLE_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/sitemap.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://docs.aws.amazon.com/solutions/latest/qnabot-on-aws/sitemap.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://docs.aws.amazon.com/de_de/solutions/latest/qnabot-on-aws/sitemap.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://docs.aws.amazon.com/solutions/qnabot-on-aws/site_map/sitemap.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://docs.aws.amazon.com/wellarchitected/latest/framework/sitemap.xml</loc>
  </sitemap>
</sitemapindex>
"""

SAMPLE_TOC = {
    "contents": [
        {"title": "Solution overview", "href": "solution-overview.html", "contents": [
            {"title": "Features", "href": "features.html"},
        ]},
        {"title": "Deploy the solution", "href": "deploy-the-solution.html", "contents": [
            {"title": "Deploy using AWS CloudFormation", "href": "deploy-using-cfn.html"},
        ]},
        {"title": "Glossary", "href": "glossary.html"},
        {"title": "Revisions", "href": "revisions.html"},
        {"title": "Notices", "href": "notices.html"},
    ]
}


def test_parse_solution_slugs_matches_english_locale_only():
    slugs = _parse_solution_slugs(SAMPLE_SITEMAP_XML)

    assert slugs == ["distributed-load-testing-on-aws", "qnabot-on-aws"]


def test_parse_solution_slugs_excludes_guidance_site_map_and_other_guides():
    slugs = _parse_solution_slugs(SAMPLE_SITEMAP_XML)

    assert "qnabot-on-aws" in slugs  # from solutions/latest/, not solutions/.../site_map/
    assert len(slugs) == 2  # site_map and wellarchitected entries excluded


def test_parse_solution_slugs_dedupes():
    xml = SAMPLE_SITEMAP_XML + """
    <sitemap><loc>https://docs.aws.amazon.com/solutions/latest/qnabot-on-aws/sitemap.xml</loc></sitemap>
    """
    slugs = _parse_solution_slugs(xml)

    assert slugs.count("qnabot-on-aws") == 1


def test_iter_pages_yields_parent_and_child_pages():
    """Unlike Prescriptive Guidance, parent nodes here are real content too."""
    pages = list(_iter_pages(SAMPLE_TOC))
    hrefs = {href for _, href, _ in pages}

    assert "solution-overview.html" in hrefs
    assert "features.html" in hrefs
    assert "deploy-the-solution.html" in hrefs
    assert "deploy-using-cfn.html" in hrefs


def test_iter_pages_skips_boilerplate_sections():
    pages = list(_iter_pages(SAMPLE_TOC))
    hrefs = {href for _, href, _ in pages}

    assert "glossary.html" not in hrefs
    assert "revisions.html" not in hrefs
    assert "notices.html" not in hrefs
