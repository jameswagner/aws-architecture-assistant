from eval.run_eval import load_questions

VALID_SOURCES = {"well_architected", "prescriptive_guidance", "solutions_library"}
URL_PREFIXES = {
    "well_architected": "https://docs.aws.amazon.com/wellarchitected/latest/framework/",
    "prescriptive_guidance": "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/",
    "solutions_library": "https://docs.aws.amazon.com/solutions/latest/",
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
        assert q["reference_answer"].strip()


def test_all_sources_represented():
    questions = load_questions()
    sources = {q["expected_source"] for q in questions}
    assert sources == VALID_SOURCES
