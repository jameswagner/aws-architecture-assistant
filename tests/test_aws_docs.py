from ingest.aws_docs import parse_page

SAMPLE_PAGE_HTML = """
<html><body><div id="main-content"><div id="main-col-body">
<h1 class="topictitle" id="welcome">Sample Best Practice</h1>
<p>Some guidance text.</p>
<img src="/images/pattern-img/diagram.png" alt="Four-step deployment process." />
<p>More guidance text.</p>
</div></div></body></html>
"""

SAMPLE_PAGE_NO_IMAGES_HTML = """
<html><body><div id="main-content"><div id="main-col-body">
<h1 class="topictitle" id="welcome">Sample Best Practice</h1>
<p>Some guidance text.</p>
</div></div></body></html>
"""


def test_parse_page_extracts_title_and_text():
    title, text, images = parse_page(SAMPLE_PAGE_NO_IMAGES_HTML)

    assert title == "Sample Best Practice"
    assert "Some guidance text." in text
    assert images == []


def test_parse_page_folds_image_alt_text_into_content():
    _, text, images = parse_page(SAMPLE_PAGE_HTML)

    assert "[Diagram: Four-step deployment process.]" in text
    assert images == [
        {"url": "https://docs.aws.amazon.com/images/pattern-img/diagram.png", "alt": "Four-step deployment process."}
    ]


def test_parse_page_keeps_image_url_even_without_alt_text():
    html = SAMPLE_PAGE_NO_IMAGES_HTML.replace(
        "<p>Some guidance text.</p>",
        '<p>Some guidance text.</p><img src="diagram.png" />',
    )
    _, text, images = parse_page(html)

    assert images == [{"url": "https://docs.aws.amazon.com/diagram.png", "alt": ""}]
    assert "[Diagram:" not in text


def test_parse_page_raises_when_main_col_body_missing():
    try:
        parse_page("<html><body>no expected structure here</body></html>")
    except ValueError:
        return
    raise AssertionError("expected ValueError when #main-col-body is missing")
