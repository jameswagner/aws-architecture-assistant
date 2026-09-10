# Chunking strategy

Default: **structure-aware first, token-based fallback second.** Sources
like Well-Architected and Prescriptive Guidance have real headings (pillar
→ question → best practice; pattern → problem → solution) — split on those
boundaries before ever falling back to a fixed token window, since the
heading structure is a stronger signal of a coherent unit than any token
count. Only apply token-based splitting (`SentenceSplitter`-style, ~700-800
tokens, ~64 token overlap — the 300-1000 range from lesson 4 holds here
too) within a section that's still too long after the structural split.

Every chunk keeps its section-level metadata (pillar, question ID, pattern
name, source, url, fetched_on) regardless of how it was split — this is
what Phase 2 metadata filtering and query routing key off of.

| Source | Chunking approach | Status |
|---|---|---|
| Well-Architected Framework | Structure-aware (pillar/question/best-practice), token fallback within sections | Decided, not yet implemented (Phase 1) |
| Prescriptive Guidance | Structure-aware (problem/solution/considerations per pattern) | Decided, not yet implemented (Phase 1) |
| Builders' Library | Long-form prose, no reliable heading structure — plain token-based (~768/64, matches lesson 4) | Deferred to Phase 2 |
| Whitepapers (PDF) | TBD — likely page- or section-based with overlap; depends on how consistently whitepapers use headings | Deferred to Phase 2 |
| Case studies / Solutions Library | TBD — likely short enough per page to need little to no splitting | Deferred to Phase 2 |

Update this table as part of the [onboarding checklist](onboarding_a_source.md)
whenever a new source is added — don't leave the decision undocumented.
