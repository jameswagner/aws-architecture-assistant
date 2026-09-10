from eval.run_eval import _hit_rate_and_mrr


def scored(ranks: list[int | None]) -> list[tuple[dict, list[str], int | None]]:
    return [({}, [], rank) for rank in ranks]


def test_all_hits_at_rank_one_gives_perfect_scores():
    hit_rate, mrr = _hit_rate_and_mrr(scored([1, 1, 1]))

    assert hit_rate == 1.0
    assert mrr == 1.0


def test_all_misses_gives_zero_scores():
    hit_rate, mrr = _hit_rate_and_mrr(scored([None, None]))

    assert hit_rate == 0.0
    assert mrr == 0.0


def test_mrr_penalizes_lower_ranked_hits_more_than_hit_rate_does():
    hit_rate, mrr = _hit_rate_and_mrr(scored([1, 5]))

    assert hit_rate == 1.0  # both are hits, regardless of rank
    assert mrr == (1 / 1 + 1 / 5) / 2  # but MRR distinguishes rank 1 from rank 5


def test_misses_count_toward_hit_rate_denominator_but_contribute_zero_to_mrr():
    hit_rate, mrr = _hit_rate_and_mrr(scored([1, None]))

    assert hit_rate == 0.5
    assert mrr == 0.5  # (1/1 + 0) / 2
