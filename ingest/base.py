"""Contract every source ingester implements.

Adding a new source? Follow docs/onboarding_a_source.md. This module only
defines the shape source modules return — scraping/parsing logic lives in
ingest/sources/<name>.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


@dataclass
class RawDocument:
    source: str  # e.g. "well_architected", "prescriptive_guidance"
    title: str
    url: str
    content: str
    fetched_on: date  # drives "most recent guidance" resolution — never inferred by the model
    metadata: dict = field(default_factory=dict)  # e.g. {"pillar": "Reliability"}


class SourceIngester(Protocol):
    def fetch(self) -> list[RawDocument]: ...
