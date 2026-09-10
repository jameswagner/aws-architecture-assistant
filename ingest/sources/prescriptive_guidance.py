"""Prescriptive Guidance ingester.

Access: requests + BS4 over static HTML on docs.aws.amazon.com.
License: CC-BY-SA-4.0.
Structure to preserve as metadata: pattern name, services involved
(drives metadata filtering in Phase 2 — see docs/chunking_strategy.md).
"""

from __future__ import annotations

from ..base import RawDocument


def fetch() -> list[RawDocument]:
    raise NotImplementedError("Phase 1")
