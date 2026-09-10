from ingest.sources.prescriptive_guidance import _iter_pages

SAMPLE_TOC = {
    "contents": [
        {"title": "AWS Prescriptive Guidance patterns", "href": "welcome.html"},
        {
            "title": "Compute",
            "href": "compute-pattern-list.html",
            "contents": [
                {
                    "title": "Containers & microservices",
                    "href": "containersandmicroservices-pattern-list.html",
                    "contents": [
                        {"title": "Deploy Lambda functions with container images", "href": "deploy-lambda.html"},
                    ],
                },
            ],
        },
    ]
}


def test_iter_pages_yields_only_leaf_pattern_pages():
    pages = list(_iter_pages(SAMPLE_TOC))
    hrefs = {href for _, href, _ in pages}

    assert "welcome.html" in hrefs
    assert "deploy-lambda.html" in hrefs
    # category/list pages have children — navigational only, not real content
    assert "compute-pattern-list.html" not in hrefs
    assert "containersandmicroservices-pattern-list.html" not in hrefs


def test_iter_pages_tags_category_path_from_ancestors():
    pages = list(_iter_pages(SAMPLE_TOC))
    by_href = {href: path for _, href, path in pages}

    assert by_href["welcome.html"] == ()
    assert by_href["deploy-lambda.html"] == ("Compute", "Containers & microservices")
