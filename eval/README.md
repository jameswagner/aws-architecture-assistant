# Eval set

Populated in Phase 1, once Well-Architected + Prescriptive Guidance are
ingested — build it alongside retrieval, not after. Target: 10-20 real
questions with known correct source sections.

Format: `questions.jsonl`, one JSON object per line —

```json
{"id": "wa-001", "question": "...", "expected_source": "well_architected", "expected_url": "https://docs.aws.amazon.com/...", "notes": "..."}
```

- `expected_source` / `expected_url` are the ground truth a retrieval hit
  is checked against — not what the LLM should say, since Phase 1 has no
  synthesis yet.
- Add a few source-specific questions every time a new source is onboarded
  (step 7 of [onboarding_a_source.md](../docs/onboarding_a_source.md)) and
  re-run the full set against the expanded corpus.
