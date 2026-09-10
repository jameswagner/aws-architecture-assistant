"""HF Space entrypoint. Placeholder until Phase 3 wires up synthesis."""

import gradio as gr

with gr.Blocks(title="AWS Architecture Precedent Assistant") as demo:
    gr.Markdown(
        "# AWS Architecture Precedent Assistant\n\n"
        "Under construction — see the [project plan](docs/sources.md) for phase status."
    )

if __name__ == "__main__":
    demo.launch()
