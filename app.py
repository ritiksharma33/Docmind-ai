import gradio as gr
import hashlib
from typing import List, Dict
import os

from document_processor.file_handler import DocumentProcessor
from retriever.builder import RetrieverBuilder
from agents.workflow import AgentWorkflow
from config import constants, settings
from utils.logging import logger

def main():
    processor = DocumentProcessor()
    retriever_builder = RetrieverBuilder()
    workflow = AgentWorkflow()

    # Premium High-End SaaS Styling (Glassmorphism & Dark Luxury)
    css = """
    .gradio-container {
        max-width: 1300px !important;
        margin: auto !important;
        background-color: #0b0f19 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }

    /* Hero Banner Styling */
    .hero {
        text-align: center;
        padding: 40px 20px;
        border-radius: 24px;
        margin-bottom: 25px;
        background: radial-gradient(circle at top, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
        border: 1px solid rgba(255, 255, 255, 0.03);
    }

    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #64748b;
        font-weight: 400;
    }

    /* Glassmorphism Feature Cards */
    .feature-card {
        flex: 1;
        padding: 20px;
        border-radius: 16px;
        text-align: left;
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .feature-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }

    .feature-card h3 {
        font-size: 1.05rem;
        color: #f8fafc;
        margin-bottom: 4px;
        font-weight: 600;
    }

    .feature-card p {
        font-size: 0.875rem;
        color: #64748b;
    }

    /* Main Workspace Panels */
    .workspace-panel {
        background: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 24px !important;
    }

    /* Hide default Gradio footers */
    footer {
        display: none !important;
    }
    """

    with gr.Blocks(
        theme=gr.themes.Default(
            primary_hue="indigo",
            secondary_hue="slate"
        ),
        title="DocMind AI",
        css=css
    ) as demo:

        # Core operational context state session
        session_state = gr.State({
            "file_hashes": frozenset(),
            "retriever": None
        })

        # Header Hero Section
        gr.HTML("""
        <div class="hero">
            <div class="hero-title">DocMind AI</div>
            <div class="hero-subtitle">Multi-Agent Document Intelligence Platform</div>
        </div>
        """)

        # Platform Value Pillar Cards
        with gr.Row():
            gr.HTML("""
            <div class="feature-card">
                <h3>🔍 Hybrid Semantic Retrieval</h3>
                <p>Combines dense deep-learning vector spaces with structural keyword BM25 indexing mapping.</p>
            </div>
            """)
            gr.HTML("""
            <div class="feature-card">
                <h3>🧠 Multi-Agent Orchestration</h3>
                <p>Splits analytical workflows into collaborative research and counter-verification engine runtimes.</p>
            </div>
            """)
            gr.HTML("""
            <div class="feature-card">
                <h3>✅ Hallucination Guardrails</h3>
                <p>Runs source trace matching against context files to shield against generated misinformation.</p>
            </div>
            """)

        gr.Markdown("---")

        with gr.Row():
            # Left Functional Workspace: User Inputs
            with gr.Column(scale=1, elem_classes="workspace-panel"):
                gr.Markdown("### 📂 Document Workspace")
                
                files = gr.Files(
                    label="Upload Knowledge Sources",
                    file_types=constants.ALLOWED_TYPES
                )

                question = gr.Textbox(
                    label="Ask Your Question",
                    lines=4,
                    placeholder="What would you like to extract or analyze from your documents?..."
                )

                submit_btn = gr.Button(
                    "🚀 Analyze Documents",
                    variant="primary",
                    size="lg"
                )

            # Right Functional Console: AI Target Readout
            with gr.Column(scale=2, elem_classes="workspace-panel"):
                gr.Markdown("### 🤖 AI Response")
                
                answer_output = gr.Markdown(
                    value="*Awaiting input data. Upload document targets and supply your question in the workspace panel to initialize synthesis.*"
                )

                gr.Markdown("<br>")

                with gr.Accordion(
                    "📊 Multi-Agent Validation Trace & Audit Report",
                    open=False
                ):
                    verification_output = gr.Markdown(
                        value="*No active validation telemetry trace currently logging.*"
                    )

        # Standard processing flow logic
        def process_question(question_text: str, uploaded_files: List, state: Dict):
            try:
                if not question_text.strip():
                    raise ValueError("The question parameter cannot be empty.")
                if not uploaded_files:
                    raise ValueError("Analysis halted: No knowledge document source files provided.")

                current_hashes = _get_file_hashes(uploaded_files)
                
                # Check for cached retriever setup to prevent redundant processing overhead
                if state["retriever"] is None or current_hashes != state["file_hashes"]:
                    logger.info("Parsing and indexing new text vectors...")
                    chunks = processor.process(uploaded_files)
                    retriever = retriever_builder.build_hybrid_retriever(chunks)
                    
                    state.update({
                        "file_hashes": current_hashes,
                        "retriever": retriever
                    })
                
                # Execute full LangGraph pipeline mapping
                result = workflow.full_pipeline(
                    question=question_text,
                    retriever=state["retriever"]
                )
                
                return result["draft_answer"], result["verification_report"], state
                    
            except Exception as e:
                logger.error(f"Runtime execution trace fault: {str(e)}")
                return f"❌ **System Execution Failure:** {str(e)}", "", state

        # Event Binding Click Hook
        submit_btn.click(
            fn=process_question,
            inputs=[
                question,
                files,
                session_state
            ],
            outputs=[
                answer_output,
                verification_output,
                session_state
            ],
            show_progress="full"
        )

    demo.launch(server_name="127.0.0.1", server_port=5000, share=True)

def _get_file_hashes(uploaded_files: List) -> frozenset:
    """Generate SHA-256 signatures for tracking active structural document updates."""
    hashes = set()
    for file in uploaded_files:
        with open(file.name, "rb") as f:
            hashes.add(hashlib.sha256(f.read()).hexdigest())
    return frozenset(hashes)

if __name__ == "__main__":
    main()