"""Run the eval set against the real index and report retrieval accuracy.

Requires the corpus to already exist (python build_index.py) — this
checks retrieval quality against it, it doesn't build anything.

Usage:
  python -m eval.run_eval           # detailed per-question report at top_k=5
  python -m eval.run_eval sweep     # Hit Rate/MRR across a range of top_k values
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from llama_index.core import VectorStoreIndex

from common.retrieval import load_index, retrieve

QUESTIONS_PATH = Path(__file__).parent / "questions.jsonl"
SWEEP_VALUES = (2, 4, 6, 8, 10)


def load_questions() -> list[dict]:
    lines = QUESTIONS_PATH.read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _score(index: VectorStoreIndex, questions: list[dict], top_k: int) -> list[tuple[dict, list[str], int | None]]:
    """For each question, return (question, retrieved urls, rank of the hit or None)."""
    results = []
    for q in questions:
        urls = [r["url"] for r in retrieve(index, q["question"], top_k=top_k)]
        rank = urls.index(q["expected_url"]) + 1 if q["expected_url"] in urls else None
        results.append((q, urls, rank))
    return results


def _hit_rate_and_mrr(scored: list[tuple[dict, list[str], int | None]]) -> tuple[float, float]:
    ranks = [rank for _, _, rank in scored]
    hit_rate = sum(r is not None for r in ranks) / len(ranks)
    mrr = sum(1 / r for r in ranks if r is not None) / len(ranks)
    return hit_rate, mrr


def run_eval(top_k: int = 5) -> None:
    index = load_index()
    scored = _score(index, load_questions(), top_k)

    for q, urls, rank in scored:
        status = f"HIT (rank {rank})" if rank else "MISS"
        print(f"[{status:12s}] {q['id']}: {q['question']}")
        if not rank:
            print(f"    expected: {q['expected_url']}")
            print(f"    got: {urls}")

    hit_rate, mrr = _hit_rate_and_mrr(scored)
    print(f"\ntop_{top_k}: hit rate {hit_rate:.2f}, MRR {mrr:.3f}")


def sweep(values: tuple[int, ...] = SWEEP_VALUES) -> None:
    index = load_index()
    questions = load_questions()

    for k in values:
        hit_rate, mrr = _hit_rate_and_mrr(_score(index, questions, k))
        print(f"top_{k:<3} hit rate {hit_rate:.2f}  MRR {mrr:.3f}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sweep":
        sweep()
    else:
        run_eval()
