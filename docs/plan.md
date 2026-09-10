# Project: AWS Architecture Assistant

## One-line pitch

Given a problem description, retrieve grounded AWS guidance (Well-
Architected best practices, Prescriptive Guidance patterns, real customer
case studies) and propose a specific architecture — with citations
back to the source material, and a generated diagram — rather than just
answering questions about AWS.

## Target user

Solutions architects and cloud consultants who want "here's grounded
guidance for a problem like mine, here's a proposed architecture, here's
why" — not generic exam-prep Q&A (too commoditized) and not enterprise
proprietary data (not accessible). The value is in synthesis +
citation + diagram, not in having unique data.

## Course requirements this must satisfy (recap)

**Necessary (all required):**
- Python RAG project, ≥1 LLM (user-supplied API key: OpenAI/Gemini/Claude)
- Deployed on a public Hugging Face Space
- Data collection/curation scripts included in repo
- README explaining the project, listing required API keys
- No hardcoded keys; no costly pipelines run on the user's key
- README cost estimate showing full functionality under $0.50

**Optional (need ≥5, targeting ~9 — see Phase mapping below):**
Domain-specific app · 2+ data sources beyond course · PDFs in data
collection · metadata filtering · query routing · hybrid search ·
reranker · streaming responses · context/prompt caching

---

## Data sources (by license/access posture)

See [sources.md](sources.md) for the live, up-to-date version of this
table — it gets updated as sources are actually onboarded.

| Source | Status | Access method |
|---|---|---|
| Well-Architected Framework | Open (docs.aws.amazon.com, CC-BY-SA-4.0) | `requests` + BS4, static HTML |
| Prescriptive Guidance | Open (docs.aws.amazon.com, CC-BY-SA-4.0) | `requests` + BS4, static HTML |
| Amazon Builders' Library | Public, no login | `requests` + BS4, static HTML |
| AWS Solutions Library | Site Terms restricted, modest use | Firecrawl (dynamic listing pages) |
| Customer case studies | Site Terms restricted, modest use | Firecrawl (dynamic listing pages) |
| Whitepapers (PDF) | Public whitepaper catalog | `requests` direct PDF download |
| This Is My Architecture (video) | Site Terms restricted | Stretch goal — YouTube caption API |
| re:Invent sessions (video) | robots.txt-blocked path for case studies; YouTube ToS applies | Stretch goal — YouTube caption API |

Keep scraping volume modest on anything under Site Terms restriction
(case studies, Solutions Library, TIMA) — this is a course/portfolio
project, not a production crawler.

---

## Phased build plan

Each phase should produce a working, demoable thing before starting
the next one — don't build all retrieval, synthesis, and diagramming
in parallel.

### Phase 0 — Scoping
- Confirm which sources are in v1 (recommend: Well-Architected +
  Prescriptive Guidance only) vs. later phases
- Decide chunking strategy per source type
- Stand up repo skeleton, README stub, HF Space shell (empty is fine)

### Phase 1 — Retrieval core (no synthesis yet)
- Ingest Well-Architected Framework + Prescriptive Guidance
- Build retrieval (justify hybrid search vs. plain semantic before
  building it — don't assume infra is needed)
- Return raw retrieved passages with citations, no LLM synthesis
- Build a small labeled eval set (10-20 real questions with known
  correct source sections) — do this now, not later
- **Demo-able output:** ask a question, get back cited guidance

### Phase 2 — Expand sources + structure
- Add Builders' Library, case studies, Solutions Library, whitepaper PDFs
- Add metadata filtering (by WA pillar, service, source type)
- Add query routing (pattern-lookup vs. framework-guidance questions)
- Re-run eval set against expanded corpus

### Phase 3 — Architecture synthesis
- LLM proposes a specific architecture from retrieved guidance,
  every claim traceable to a citation
- Add streaming responses
- Add reranker on top of hybrid retrieval
- Eval: is the proposed architecture reasonable and well-supported
  (harder eval than retrieval accuracy — worth the design time)

### Phase 4 — Diagram generation
- LLM emits structured diagram spec (Mermaid or Python `diagrams`
  library with real AWS icons) from the same structured output used
  for the write-up — not a separate freeform image-gen call
- Render server-side, validate output before showing to user
- Add a retry/validation loop for malformed diagram code

### Phase 5 — Ship
- Deploy to public HF Space
- Write README: project explanation, required API keys, cost
  estimate (test actual token costs, don't guess), optional
  functionality checklist, eval results
- Add prompt/context caching for the stable framework text
- Add a .txt submission file per course instructions (HF Space link
  + GitHub link + optional techniques used)

---

## Optional functionality checklist (target: 9 of these)

- [x] Domain-specific app (Phase 1)
- [x] 2+ data sources beyond course (Phase 1-2)
- [x] PDFs in data collection (Phase 2, whitepapers)
- [x] Metadata filtering (Phase 2)
- [x] Query routing (Phase 2)
- [x] Hybrid search (Phase 1, if justified)
- [x] Reranker (Phase 3)
- [x] Streaming responses (Phase 3)
- [x] Context/prompt caching (Phase 5)

---

## Stretch goals (roughly in order of value/effort)

1. **RAG evaluation harness + published results** — build past the
   informal eval set into a real scored benchmark, write results and
   methodology into the README. High portfolio value.
2. **re:Invent video transcription ingestion** — YouTube caption API
   → chunk → embed. Highest-effort source, lowest structure; only
   worth it once Phases 1-4 are solid.
3. **Structured JSON outputs** — return case studies as structured
   fields (service, problem, outcome) rather than prose.
4. **Live search integration** — Perplexity/Bing API for "has
   anything changed since my corpus was built" queries. Requires
   user to supply another API key.
5. **Function calling** — e.g., a tool that checks current AWS
   service pricing or docs live, rather than relying only on the
   static corpus.
6. **Fine-tuned embedding model** — lower value for this use case;
   only pursue if the other stretch goals are done and there's time
   left.

Do **not** attempt image-generation-model diagrams (freeform
diffusion output) — Phase 4's structured-DSL approach is the
correct one; a diffusion model drawing AWS diagrams will produce
garbled, architecturally meaningless output.

---

## Standing risks to watch

- Don't let "RAG project" mean building retrieval infra for sources
  small enough to just live in context (Well-Architected Framework
  text may be one of these — check before building).
- Service/category mappings (WA pillar, AWS service type) should be
  real lookup tables, not prompt-inferred.
- "Most recent" AWS guidance must be resolved from ingestion
  timestamps, never inferred by the model.
- Keep case-study/Solutions-Library scraping modest given Site Terms.
- Retrieved content is untrusted external input once fed into a
  synthesis prompt — apply the trusted/untrusted boundary pattern
  from lesson 1 (explicit data tags, a system prompt hardened
  against instruction-following from retrieved passages) rather than
  treating RAG context as implicitly safe.
