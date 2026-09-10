# Data sources

Living doc — update whenever a source is added or its status changes (see
[onboarding checklist](onboarding_a_source.md)).

| Source | Status | License/access posture | Access method |
|---|---|---|---|
| Well-Architected Framework | Planned — Phase 1 | Open (docs.aws.amazon.com, CC-BY-SA-4.0) | `requests` + BS4, static HTML |
| Prescriptive Guidance | Planned — Phase 1 | Open (docs.aws.amazon.com, CC-BY-SA-4.0) | `requests` + BS4, static HTML |
| Amazon Builders' Library | Planned — Phase 2 | Public, no login | `requests` + BS4, static HTML |
| AWS Solutions Library | Planned — Phase 2 | Site Terms restricted, modest use | Firecrawl (dynamic listing pages) |
| Customer case studies | Planned — Phase 2 | Site Terms restricted, modest use | Firecrawl (dynamic listing pages) |
| Whitepapers (PDF) | Planned — Phase 2 | Public whitepaper catalog | `requests` direct PDF download |
| This Is My Architecture (video) | Stretch | Site Terms restricted | YouTube caption API |
| re:Invent sessions (video) | Stretch | robots.txt-blocked path for case studies; YouTube ToS applies | YouTube caption API |

v1 scope (Phase 1) is deliberately narrow: Well-Architected + Prescriptive
Guidance only, both cleanly open-licensed. Site-Terms-restricted sources
(case studies, Solutions Library, TIMA) are deferred until Phase 2, once
it's clear whether the optional-functionality target (5 of 9, aiming for
9) is already met without them.
