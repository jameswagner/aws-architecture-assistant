# AWS Architecture Precedent Assistant

**Status: Phase 0 (scaffolding) — not yet functional.**

Given a problem description, retrieves grounded AWS precedent
(Well-Architected guidance, Prescriptive Guidance patterns, and later
real customer case studies) and proposes a specific architecture — with
citations back to the precedent and a generated diagram — rather than
just answering questions about AWS.

## Target user

Solutions architects and cloud consultants who want precedent for a
problem like theirs, a proposed architecture, and the reasoning behind
it — not generic exam-prep Q&A.

## Required API keys

At least one LLM key, user-supplied (never hardcoded): `OPENAI_API_KEY`,
`GOOGLE_API_KEY`, or `ANTHROPIC_API_KEY`. See `.env.example`.

## Cost estimate

TBD — measured against real token usage once Phase 1 retrieval is
working, not guessed. Target: full functionality under $0.50.

## Data sources

See [docs/sources.md](docs/sources.md) for the full table and license
posture per source. v1 (Phase 1): Well-Architected Framework +
Prescriptive Guidance only.

## Project structure

- `ingest/` — one module per source (`ingest/sources/<name>.py`), all
  implementing the contract in `ingest/base.py`. See
  [docs/onboarding_a_source.md](docs/onboarding_a_source.md) before
  adding a new one.
- `docs/` — chunking strategy, source table, onboarding checklist.
- `eval/` — labeled eval set, built alongside retrieval starting Phase 1.
- `data/` — gitignored; raw/processed data lands here.
- `app.py` — HF Space entrypoint.

## Phase plan

See [docs/plan.md](docs/plan.md) for the full phased build-out (Phase 1:
retrieval core → Phase 2: expand sources → Phase 3: synthesis → Phase 4:
diagrams → Phase 5: ship).

## Optional functionality (course requirement: ≥5, targeting 9)

- [ ] Domain-specific app
- [ ] 2+ data sources beyond course
- [ ] PDFs in data collection
- [ ] Metadata filtering
- [ ] Query routing
- [ ] Hybrid search
- [ ] Reranker
- [ ] Streaming responses
- [ ] Context/prompt caching
