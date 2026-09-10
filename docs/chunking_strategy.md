# Chunking strategy

Default: **structure-aware first, token-based fallback second, per source.**
Checked against real pages before committing to this per source (see table)
rather than assuming heading structure exists — it doesn't always.

Well-Architected's consolidated "framework" guide (what we actually ingest)
turned out to have **mixed structure depending on page depth** — checked
against real pages at each level before assuming either way:

- Pillar-summary pages (e.g. "Organization" under Operational Excellence,
  reached via "The pillars of the framework") and per-question pages
  (e.g. "PERF 2. How do you select compute resources?") are flat: `<h1>`
  title, then plain `<p>` paragraphs, nothing else.
- The deepest level — individual per-best-practice pages (e.g. "PERF02-BP01
  Select the best compute options"), reached via a *separate* top-level
  section, "Appendix: Questions and best practices" — genuinely do have
  real `<h2>` structure: Implementation guidance / Implementation steps /
  Resources, the standard AWS best-practice page format. This is also
  where the "OE 1: How do you..." per-question breakdown WA is known for
  actually lives — an earlier version of this doc claimed it lived in
  separate per-pillar guides we don't ingest, which was wrong; it's right
  here in the same framework guide, just one section over.

No source-specific code is needed for this: `parse_page()` already splits
generically on whatever `<h2>`s exist and produces a single section when
there are none, so flat pages and structured pages both flow through the
same chunking path correctly.

One real bug this surfaced: pillar tagging originally only recognized
"The pillars of the framework" by name, so everything under "Appendix:
Questions and best practices" — the majority of WA's ~470 pages — was
silently getting no pillar at all. Fixed by detecting *any* section whose
children are exactly the six pillar names, not hardcoding a specific
section title (caught by the eval set in issue #6, not by inspection).

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
| Well-Architected Framework | Structure-aware where `<h2>`s exist (deepest best-practice pages), token-based fallback elsewhere (summary/question pages) — same code path either way | Decided, Phase 1 (issue #3) |
| Prescriptive Guidance | Structure-aware on real `<h2>` sections, token fallback within an oversized section | Decided, Phase 1 (issue #3) |
| Builders' Library | Long-form prose, no reliable heading structure — plain token-based (~768/64, matches lesson 4) | Deferred to Phase 2 |
| Whitepapers (PDF) | TBD — likely page- or section-based with overlap; depends on how consistently whitepapers use headings | Deferred to Phase 2 |
| Case studies / Solutions Library | TBD — likely short enough per page to need little to no splitting | Deferred to Phase 2 |

Update this table as part of the [onboarding checklist](onboarding_a_source.md)
whenever a new source is added — don't leave the decision undocumented.
