from ingest.aws_docs import parse_page

SAMPLE_PAGE_HTML = """
<html><body><div id="main-content"><div id="main-col-body">
<h1 class="topictitle" id="welcome">Sample Best Practice</h1>
<p>Some guidance text.</p>
<p>More guidance text.</p>
</div></div></body></html>
"""


def test_parse_page_extracts_title_and_text():
    title, text = parse_page(SAMPLE_PAGE_HTML)

    assert title == "Sample Best Practice"
    assert "Some guidance text." in text
    assert "More guidance text." in text


def test_parse_page_raises_when_main_col_body_missing():
    try:
        parse_page("<html><body>no expected structure here</body></html>")
    except ValueError:
        return
    raise AssertionError("expected ValueError when #main-col-body is missing")
