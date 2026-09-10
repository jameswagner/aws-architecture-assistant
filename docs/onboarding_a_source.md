# Onboarding a new source

Run through this every time a source is added (Phase 1: Well-Architected +
Prescriptive Guidance; Phase 2+: Builders' Library, case studies, Solutions
Library, whitepapers; stretch: re:Invent video).

1. **License/access posture.** Open, Site-Terms-restricted, or
   robots.txt-blocked? Add a row to [sources.md](sources.md) before writing
   any code.
2. **Access method.** `requests` + BS4 for static HTML, Firecrawl for
   dynamic listing pages, direct download for PDFs. Restricted sources
   (case studies, Solutions Library, TIMA) stay modest in volume — this is
   a portfolio project, not a crawler.
3. **Write `ingest/sources/<name>.py`.** Implement `fetch() -> list[RawDocument]`
   per the contract in [`ingest/base.py`](../ingest/base.py). Every
   `RawDocument` needs a real `fetched_on` — "most recent guidance" is
   resolved from that timestamp, never inferred by the model.
4. **Decide chunking for this source type.** Structure-aware (split on real
   headings) or token-based fallback? Record the decision and the
   reasoning in [chunking_strategy.md](chunking_strategy.md) — don't just
   pick a chunk size and move on.
5. **Metadata schema.** What fields does this source attach to every chunk
   (WA pillar, AWS service, pattern name, source type, URL, fetched_on)?
   Service/pillar mappings are real lookup tables, not prompt-inferred —
   see the standing risks note in the top-level plan.
6. **Register it.** Add the source to the ingestion entrypoint/registry so
   it runs as part of the standard data collection script.
7. **Extend the eval set.** Add a few questions to `eval/` that specifically
   target this source, then re-run the eval set against the expanded
   corpus.
8. **Update `sources.md` and the README's source table** to reflect what's
   actually ingested, not just planned.
