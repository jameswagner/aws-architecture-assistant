from eval.run_eval import load_questions

VALID_SOURCES = {"well_architected", "prescriptive_guidance"}
URL_PREFIXES = {
    "well_architected": "https://docs.aws.amazon.com/wellarchitected/latest/framework/",
    "prescriptive_guidance": "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/",
}


def test_at_least_ten_questions():
    questions = load_questions()
    assert len(questions) >= 10


def test_ids_are_unique():
    questions = load_questions()
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids))


def test_every_question_has_required_fields():
    questions = load_questions()
    for q in questions:
        assert q["question"].strip()
        assert q["expected_source"] in VALID_SOURCES
        assert q["expected_url"].startswith(URL_PREFIXES[q["expected_source"]])


def test_both_sources_represented():
    questions = load_questions()
    sources = {q["expected_source"] for q in questions}
    assert sources == VALID_SOURCES
