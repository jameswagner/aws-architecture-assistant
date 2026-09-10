from datetime import date

from ingest.base import RawDocument
from ingest.sources import prescriptive_guidance


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


def test_prescriptive_guidance_still_phase_1_todo():
    try:
        prescriptive_guidance.fetch()
    except NotImplementedError:
        return
    raise AssertionError("prescriptive_guidance.fetch() is implemented — update this test")
