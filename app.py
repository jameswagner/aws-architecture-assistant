"""HF Space entrypoint.

Loads the index lazily on first question, not at import time, so
`import app` (used by tests/test_app.py) stays cheap and network-free.
"""

import gradio as gr

from common.retrieval import load_index
from common.synthesis import answer

_index = None


def _get_index():
    global _index
    if _index is None:
        _index = load_index()
    return _index


def respond(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Ask a question about AWS architecture.", ""

    result = answer(_get_index(), question)
    citations = "\n".join(f"- [{c['title']}]({c['url']})" for c in result["citations"])
    return result["answer"], citations


with gr.Blocks(title="AWS Architecture Assistant") as demo:
    gr.Markdown("# AWS Architecture Assistant")
    gr.Markdown(
        "Ask a question about AWS architecture and get an answer grounded in "
        "Well-Architected Framework guidance and Prescriptive Guidance patterns, "
        "with citations back to the source."
    )
    question = gr.Textbox(label="Your question", placeholder="How do I deploy a Lambda function with a container image?")
    submit = gr.Button("Ask")
    answer_box = gr.Markdown(label="Answer")
    citations_box = gr.Markdown(label="Sources")
    submit.click(respond, inputs=question, outputs=[answer_box, citations_box])
    question.submit(respond, inputs=question, outputs=[answer_box, citations_box])

if __name__ == "__main__":
    demo.launch()
