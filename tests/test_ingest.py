from datetime import date

from ingest.base import RawDocument
from ingest.sources import prescriptive_guidance, well_architected


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


def test_source_stubs_still_phase_1_todo():
    for module in (well_architected, prescriptive_guidance):
        try:
            module.fetch()
        except NotImplementedError:
            continue
        raise AssertionError(f"{module.__name__}.fetch() is implemented — update this test")
