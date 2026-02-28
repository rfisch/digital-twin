"""Gradio web interface for the writing assistant."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr

from app.assistant import WritingAssistant
from app.ollama_client import OllamaClient


def create_app():
    assistant = WritingAssistant()
    client = OllamaClient()

    def get_available_models():
        """List models available in Ollama."""
        if not assistant.ollama_mgr.ensure_running():
            return ["jacq:8b"]
        try:
            return client.list_models()
        except Exception:
            return ["jacq:8b"]

    def generate_writing(task_type, topic, model, temperature, max_tokens, use_rag,
                         recipient, purpose, email_type, medium, audience, message, tone):
        if not topic.strip():
            return "Please enter a topic or writing request."

        try:
            result = assistant.generate(
                task_type=task_type,
                topic=topic,
                use_rag=use_rag,
                temperature=temperature,
                max_tokens=max_tokens,
                recipient=recipient,
                purpose=purpose,
                email_type=email_type,
                medium=medium,
                audience=audience,
                message=message,
                tone=tone,
            )
            # Override model if different from default
            if model and model != assistant.model:
                assistant.model = model
            return result
        except Exception as e:
            return f"Error: {e}"

    with gr.Blocks(title="Jacq's Writing Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("# Jacq's Writing Assistant")
        gr.Markdown("Generate writing in Jacq's voice using a fine-tuned model + RAG.")

        with gr.Row():
            with gr.Column(scale=1):
                task_type = gr.Dropdown(
                    choices=WritingAssistant.TASK_TYPES,
                    value="blog",
                    label="Writing Type",
                )
                topic = gr.Textbox(
                    label="Topic / Request",
                    placeholder="Write about morning routines...",
                    lines=3,
                )

                with gr.Accordion("Model Settings", open=False):
                    model = gr.Dropdown(
                        choices=["jacq:8b", "llama3.1:8b"],
                        value="jacq:8b",
                        label="Model",
                        allow_custom_value=True,
                    )
                    temperature = gr.Slider(0.0, 1.5, value=0.7, step=0.1, label="Temperature")
                    max_tokens = gr.Slider(256, 4096, value=2048, step=256, label="Max Tokens")
                    use_rag = gr.Checkbox(value=True, label="Use RAG Context")

                with gr.Accordion("Email Options", open=False):
                    recipient = gr.Textbox(label="Recipient", placeholder="Sarah")
                    purpose = gr.Textbox(label="Purpose", placeholder="Follow up on proposal")
                    email_type = gr.Dropdown(
                        choices=["professional", "personal", "newsletter"],
                        value="professional",
                        label="Email Type",
                    )

                with gr.Accordion("Copywriting Options", open=False):
                    medium = gr.Textbox(label="Medium", placeholder="Instagram caption")
                    audience = gr.Textbox(label="Target Audience", placeholder="Women 25-45")
                    message = gr.Textbox(label="Key Message", placeholder="New product launch")
                    tone = gr.Textbox(label="Tone Notes", placeholder="Excited but grounded")

                generate_btn = gr.Button("Generate", variant="primary", size="lg")

            with gr.Column(scale=2):
                output = gr.Textbox(
                    label="Generated Writing",
                    lines=25,
                    show_copy_button=True,
                )

        generate_btn.click(
            fn=generate_writing,
            inputs=[
                task_type, topic, model, temperature, max_tokens, use_rag,
                recipient, purpose, email_type, medium, audience, message, tone,
            ],
            outputs=output,
        )

    return app


def main():
    app = create_app()
    app.launch(server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
