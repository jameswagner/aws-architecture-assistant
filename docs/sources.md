# Data sources

Living doc — update whenever a source is added or its status changes (see
[onboarding checklist](onboarding_a_source.md)).

| Source | Status | License/access posture | Access method |
|---|---|---|---|
| Well-Architected Framework | Planned — Phase 1 | Open (docs.aws.amazon.com, CC-BY-SA-4.0) | `requests` + BS4, static HTML |
| Prescriptive Guidance | Planned — Phase 1 | Open (docs.aws.amazon.com, CC-BY-SA-4.0) | `requests` + BS4, static HTML |
| Amazon Builders' Library | Planned — Phase 2 | Public, no login | `requests` + BS4, static HTML |
| AWS Solutions Library | Implemented — Phase 2 | Open (docs.aws.amazon.com, same platform as WA/PG) | `requests` + BS4, static HTML; slugs discovered from `sitemap_index.xml` |
| Customer case studies | Planned — Phase 2 | Site Terms restricted, modest use | Firecrawl (dynamic listing pages) |
| Whitepapers (PDF) | Planned — Phase 2 | Public whitepaper catalog | `requests` direct PDF download |
| This Is My Architecture (video) | Stretch | Site Terms restricted | YouTube caption API |
| re:Invent sessions (video) | Stretch | robots.txt-blocked path for case studies; YouTube ToS applies | YouTube caption API |

v1 scope (Phase 1) is deliberately narrow: Well-Architected + Prescriptive
Guidance only, both cleanly open-licensed. Site-Terms-restricted sources
(case studies, TIMA) are deferred until Phase 2, once it's clear whether
the optional-functionality target (5 of 9, aiming for 9) is already met
without them.

AWS Solutions Library turned out not to need that deferral: live
verification found its implementation guides run on the same open
docs.aws.amazon.com platform as WA/PG (not Site-Terms-restricted, no
Firecrawl needed) — only page *discovery* differs, since each solution is
an independent guide rather than one guide to point at (see
`ingest/sources/solutions_library.py`). Scoped to the 62-guide "AWS
Solution"/technical-guide set found via `sitemap_index.xml`; the larger
562-item single-page "Guidance" library is a separate, lower-priority
source (issue #44).
