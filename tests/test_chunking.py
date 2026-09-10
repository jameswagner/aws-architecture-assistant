from datetime import date

from common.chunking import CHUNK_SIZE, chunk_document
from ingest.base import RawDocument


def make_doc(content: str, sections: list[dict] | None = None, **metadata) -> RawDocument:
    if sections is not None:
        metadata = {**metadata, "sections": sections}
    return RawDocument(
        source="well_architected",
        title="Sample Page",
        url="https://docs.aws.amazon.com/example.html",
        content=content,
        fetched_on=date(2026, 1, 1),
        metadata=metadata,
    )


def test_single_short_section_produces_one_node():
    doc = make_doc("Short guidance text.", pillar="Reliability")

    nodes = chunk_document(doc)

    assert len(nodes) == 1
    assert nodes[0].text == "Short guidance text."
    assert nodes[0].metadata["pillar"] == "Reliability"
    assert "section" not in nodes[0].metadata


def test_long_section_with_no_heading_splits_on_tokens():
    long_text = " ".join(f"sentence number {i}." for i in range(2000))
    doc = make_doc(long_text)

    nodes = chunk_document(doc)

    assert len(nodes) > 1
    assert all(len(n.text) > 0 for n in nodes)


def test_multiple_sections_split_independently_with_heading_metadata():
    sections = [
        {"heading": None, "text": "By Jane Doe", "images": []},
        {"heading": "Summary", "text": "This pattern deploys a thing.", "images": []},
        {"heading": "Architecture", "text": "The architecture has three tiers.", "images": []},
    ]
    doc = make_doc("unused when sections present", sections=sections, category_path=["Compute", "Serverless"])

    nodes = chunk_document(doc)

    assert len(nodes) == 3
    by_section = {n.metadata.get("section"): n for n in nodes}
    assert by_section[None].text == "By Jane Doe"
    assert by_section["Summary"].text == "This pattern deploys a thing."
    assert by_section["Architecture"].text == "The architecture has three tiers."


def test_category_path_list_is_json_serialized_for_chroma():
    doc = make_doc("some text", category_path=["Compute", "Serverless"])

    nodes = chunk_document(doc)

    assert nodes[0].metadata["category_path"] == '["Compute", "Serverless"]'
    for value in nodes[0].metadata.values():
        assert isinstance(value, (str, int, float, bool))


def test_section_images_become_json_serialized_image_urls():
    sections = [
        {
            "heading": "Architecture",
            "text": "See the diagram.",
            "images": [{"url": "https://docs.aws.amazon.com/diagram.png", "alt": "A diagram."}],
        },
    ]
    doc = make_doc("unused", sections=sections)

    nodes = chunk_document(doc)

    assert nodes[0].metadata["image_urls"] == '["https://docs.aws.amazon.com/diagram.png"]'


def test_empty_sections_are_skipped():
    sections = [
        {"heading": None, "text": "", "images": []},
        {"heading": "Summary", "text": "Real content.", "images": []},
    ]
    doc = make_doc("unused", sections=sections)

    nodes = chunk_document(doc)

    assert len(nodes) == 1
    assert nodes[0].text == "Real content."


def test_chunk_size_constant_is_within_recommended_range():
    assert 300 <= CHUNK_SIZE <= 1000
