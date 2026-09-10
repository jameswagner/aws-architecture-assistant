"""Judge synthesized answers, not just retrieval, using an LLM as judge.

run_eval.py only checks whether the right chunk was retrieved. Nothing
checked whether the synthesized answer was faithful to what was retrieved,
relevant to the question, or correct — the gap that let the CodeBuild
over-generalization issue through until it was spotted by hand.

Runs a real synthesis call plus three judge calls per question, unlike
run_eval.py's retrieval-only checks — costs real money per run.

Usage: python -m eval.answer_quality
"""

from __future__ import annotations

from llama_index.core.evaluation import CorrectnessEvaluator, FaithfulnessEvaluator, RelevancyEvaluator

from common.llm import get_judge_llm
from common.retrieval import load_index
from common.synthesis import answer
from eval.run_eval import load_questions


def run_answer_quality_eval() -> None:
    index = load_index()
    judge = get_judge_llm()
    faithfulness_evaluator = FaithfulnessEvaluator(llm=judge)
    relevancy_evaluator = RelevancyEvaluator(llm=judge)
    correctness_evaluator = CorrectnessEvaluator(llm=judge)

    questions = load_questions()
    faithfulness_passes = 0
    relevancy_passes = 0
    correctness_scores = []

    for q in questions:
        result = answer(index, q["question"])
        response_text = result["answer"]
        contexts = result["contexts"]

        faithfulness = faithfulness_evaluator.evaluate(query=q["question"], response=response_text, contexts=contexts)
        relevancy = relevancy_evaluator.evaluate(query=q["question"], response=response_text, contexts=contexts)
        correctness = correctness_evaluator.evaluate(
            query=q["question"], response=response_text, reference=q["reference_answer"]
        )

        faithfulness_passes += faithfulness.passing
        relevancy_passes += relevancy.passing
        correctness_scores.append(correctness.score)

        print(
            f"{q['id']}: faithfulness={'PASS' if faithfulness.passing else 'FAIL'} "
            f"relevancy={'PASS' if relevancy.passing else 'FAIL'} correctness={correctness.score}/5"
        )
        if not faithfulness.passing:
            print(f"    faithfulness feedback: {faithfulness.feedback}")
        if not relevancy.passing:
            print(f"    relevancy feedback: {relevancy.feedback}")
        if correctness.score < 4:
            print(f"    correctness feedback: {correctness.feedback}")

    n = len(questions)
    print(f"\nFaithfulness: {faithfulness_passes}/{n}")
    print(f"Relevancy: {relevancy_passes}/{n}")
    print(f"Correctness: avg {sum(correctness_scores) / n:.2f}/5")


if __name__ == "__main__":
    run_answer_quality_eval()
