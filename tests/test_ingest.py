from datetime import date

from ingest.base import RawDocument


def test_raw_document_holds_fields():
    doc = RawDocument(
        source="well_architected",
        title="Reliability Pillar",
        url="https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/",
        content="...",
        fetched_on=date.today(),
        metadata={"pillar": "Reliability"},
    )
    assert doc.source == "well_architected"
    assert doc.metadata["pillar"] == "Reliability"
