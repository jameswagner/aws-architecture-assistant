# Chunking strategy

Default: **structure-aware first, token-based fallback second, per source.**
Checked against real pages before committing to this per source (see table)
rather than assuming heading structure exists — it doesn't always.

Well-Architected's consolidated "framework" guide (what we actually ingest)
turned out to have **no internal heading structure** — checked a real page
("Organization" under Operational Excellence): `<h1>` title, then plain
`<p>` paragraphs, nothing else. The per-question breakdown ("OE 1: How do
you determine priorities?") that WA is known for lives in AWS's separate
per-pillar guides (`reliability-pillar`, `security-pillar`, etc.), which
we don't ingest. So each fetched WA page (already one best-practice-category
per page, e.g. "Organization") is the smallest structural unit available —
it just gets token-based splitting when too long, no structural split first.

Prescriptive Guidance patterns, checked the same way, do have real `<h2>`
sections (Summary, Prerequisites, Architecture, Tools, Best practices,
Epics, Troubleshooting...) — genuinely worth splitting on, since a query
about a pattern's architecture shouldn't retrieve its Troubleshooting
section. Token-based splitting (`SentenceSplitter`-style, ~700-800 tokens,
~64 token overlap — the 300-1000 range from lesson 4 holds here too)
applies only as a fallback within a section still too long after that split.

Every chunk keeps its section-level metadata (pillar, category path,
pattern name, source, url, fetched_on) regardless of how it was split —
this is what Phase 2 metadata filtering and query routing key off of.

| Source | Chunking approach | Status |
|---|---|---|
| Well-Architected Framework | Token-based only — no internal heading structure to split on (confirmed against live pages) | Decided, Phase 1 (issue #3) |
| Prescriptive Guidance | Structure-aware on real `<h2>` sections, token fallback within an oversized section | Decided, Phase 1 (issue #3) |
| Builders' Library | Long-form prose, no reliable heading structure — plain token-based (~768/64, matches lesson 4) | Deferred to Phase 2 |
| Whitepapers (PDF) | TBD — likely page- or section-based with overlap; depends on how consistently whitepapers use headings | Deferred to Phase 2 |
| Case studies / Solutions Library | TBD — likely short enough per page to need little to no splitting | Deferred to Phase 2 |

Update this table as part of the [onboarding checklist](onboarding_a_source.md)
whenever a new source is added — don't leave the decision undocumented.
