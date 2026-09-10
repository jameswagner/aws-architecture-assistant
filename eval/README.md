# Eval set

Populated: 13 questions (8 Well-Architected, 5 Prescriptive Guidance),
each verified against the real live page before being added — not
guessed. Covers all 6 WA pillars and 4 PG categories.

Run it against the real corpus (requires `python build_index.py` to have
been run first) with:

```
python -m eval.run_eval
```

Reports a hit/miss per question (was `expected_url` in the top-k
retrieved results?) and an overall hit rate — a real, if informal, signal
on retrieval quality, not just "it ran."

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
