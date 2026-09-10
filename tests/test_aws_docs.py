from ingest.aws_docs import page_to_raw_fields, parse_page

NO_HEADINGS_HTML = """
<html><body><div id="main-content"><div id="main-col-body">
<h1 class="topictitle" id="welcome">Organization</h1>
<p>Some guidance text.</p>
<p>More guidance text.</p>
</div></div></body></html>
"""

WITH_SECTIONS_HTML = """
<html><body><div id="main-content"><div id="main-col-body">
<h1 class="topictitle">Deploy Lambda functions with container images</h1>
<p>By Ram Kandaswamy</p>
<h2>Summary</h2>
<p>AWS Lambda supports container images as a deployment model.</p>
<h2>Architecture</h2>
<p>The following diagram shows the deployment process.</p>
<div><img src="/images/pattern-img/diagram.png" alt="Four-step deployment process." /></div>
<h2>Troubleshooting</h2>
<p>Common issues and fixes.</p>
</div></div></body></html>
"""


def test_parse_page_with_no_headings_yields_single_section():
    parsed = parse_page(NO_HEADINGS_HTML)

    assert parsed.title == "Organization"
    assert len(parsed.sections) == 1
    assert parsed.sections[0].heading is None
    assert "Some guidance text." in parsed.sections[0].text
    assert "More guidance text." in parsed.sections[0].text


def test_parse_page_splits_on_h2_boundaries():
    parsed = parse_page(WITH_SECTIONS_HTML)

    headings = [s.heading for s in parsed.sections]
    assert headings == [None, "Summary", "Architecture", "Troubleshooting"]


def test_parse_page_attributes_content_to_correct_section():
    parsed = parse_page(WITH_SECTIONS_HTML)
    by_heading = {s.heading: s for s in parsed.sections}

    assert "container images as a deployment model" in by_heading["Summary"].text
    assert "Common issues and fixes." in by_heading["Troubleshooting"].text
    assert "container images as a deployment model" not in by_heading["Troubleshooting"].text


def test_parse_page_attaches_image_to_its_own_section_only():
    parsed = parse_page(WITH_SECTIONS_HTML)
    by_heading = {s.heading: s for s in parsed.sections}

    assert by_heading["Architecture"].images == [
        {"url": "https://docs.aws.amazon.com/images/pattern-img/diagram.png", "alt": "Four-step deployment process."}
    ]
    assert by_heading["Summary"].images == []
    assert "[Diagram: Four-step deployment process.]" in by_heading["Architecture"].text


def test_parse_page_raises_when_main_col_body_missing():
    try:
        parse_page("<html><body>no expected structure here</body></html>")
    except ValueError:
        return
    raise AssertionError("expected ValueError when #main-col-body is missing")


def test_page_to_raw_fields_flattens_content_and_preserves_sections():
    parsed = parse_page(WITH_SECTIONS_HTML)

    content, metadata = page_to_raw_fields(parsed)

    assert "container images as a deployment model" in content
    assert "Common issues and fixes." in content
    assert [s["heading"] for s in metadata["sections"]] == [None, "Summary", "Architecture", "Troubleshooting"]
    assert metadata["images"] == [
        {"url": "https://docs.aws.amazon.com/images/pattern-img/diagram.png", "alt": "Four-step deployment process."}
    ]


def test_page_to_raw_fields_omits_images_key_when_none_present():
    parsed = parse_page(NO_HEADINGS_HTML)

    _, metadata = page_to_raw_fields(parsed)

    assert "images" not in metadata
