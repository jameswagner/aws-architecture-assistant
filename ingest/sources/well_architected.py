"""Well-Architected Framework ingester.

Access: requests + BS4 over static HTML on docs.aws.amazon.com.
License: CC-BY-SA-4.0.
Structure to preserve as metadata: pillar, question ID (drives metadata
filtering in Phase 2 — see docs/chunking_strategy.md).
"""

from __future__ import annotations

from ..base import RawDocument


def fetch() -> list[RawDocument]:
    raise NotImplementedError("Phase 1")
