"""Run the eval set against the real index and report retrieval accuracy.

Requires the corpus to already exist (python build_index.py) — this
checks retrieval quality against it, it doesn't build anything.

Usage: python -m eval.run_eval
"""

from __future__ import annotations

import json
from pathlib import Path

from common.retrieval import load_index, retrieve

QUESTIONS_PATH = Path(__file__).parent / "questions.jsonl"


def run_eval(top_k: int = 5) -> None:
    index = load_index()
    questions = [json.loads(line) for line in QUESTIONS_PATH.read_text().splitlines() if line.strip()]

    hits = 0
    for q in questions:
        results = retrieve(index, q["question"], top_k=top_k)
        urls = [r["url"] for r in results]
        found = q["expected_url"] in urls
        hits += found
        rank = urls.index(q["expected_url"]) + 1 if found else None
        status = f"HIT (rank {rank})" if found else "MISS"
        print(f"[{status:12s}] {q['id']}: {q['question']}")
        if not found:
            print(f"    expected: {q['expected_url']}")
            print(f"    got: {urls}")

    print(f"\n{hits}/{len(questions)} retrieved within top-{top_k}")


if __name__ == "__main__":
    run_eval()
