import streamlit as st

# --------------------------------------------------------------------------
# Pipeline import
# --------------------------------------------------------------------------
# Wrapped in try/except so the UI still loads (and shows a clear message)
# if the FAISS index / pipeline module isn't available in this environment,
# e.g. when someone clones the repo without running build_index.py first.
try:
    from Rag_Pipeline import answer_question
    PIPELINE_READY = True
    PIPELINE_ERROR = None
except Exception as e:  # noqa: BLE001
    PIPELINE_READY = False
    PIPELINE_ERROR = str(e)

    def answer_question(_question: str) -> str:  # type: ignore
        return (
            "⚠️ The retrieval pipeline could not be loaded, so this is a placeholder "
            "response. Run `python build_index.py` to build the FAISS index, then "
            "restart the app."
        )

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Bacteremia Guideline Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling — a calm, clinical "medtech" palette instead of default Streamlit
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --clinical-teal: #0F6D6A;
            --clinical-teal-dark: #0A4F4C;
            --clinical-bg: #F4F8F8;
            --clinical-card: #FFFFFF;
            --clinical-border: #DCE7E6;
            --clinical-text: #1F3A38;
            --clinical-text-muted: #4B6664;
            --clinical-amber: #B45309;
            --clinical-amber-bg: #FFF7ED;
        }

        /* Force every text-bearing element to the light-theme palette.
           This is the fix for the dark/black rendering — without it,
           Streamlit falls back to the visitor's OS/browser dark-mode
           colors for anything this stylesheet doesn't explicitly own. */
        html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, li {
            font-family: 'Inter', sans-serif;
            color: var(--clinical-text) !important;
        }

        .stApp {
            background-color: var(--clinical-bg) !important;
        }

        /* Hide default Streamlit chrome for a cleaner product feel */
        #MainMenu, footer {visibility: hidden;}

        /* ---------- Header ---------- */
        .app-header {
            background: linear-gradient(135deg, var(--clinical-teal) 0%, var(--clinical-teal-dark) 100%);
            padding: 1.3rem 1.6rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 0.7rem;
            box-shadow: 0 4px 14px rgba(15, 109, 106, 0.18);
        }
        .app-header h1, .app-header p {
            color: white !important;
        }
        .app-header h1 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .app-header p {
            margin: 0.3rem 0 0 0;
            font-size: 0.88rem;
            opacity: 0.9;
        }

        /* Disclaimer as a slim inline strip, not a second big card */
        .disclaimer-strip {
            font-size: 0.78rem;
            color: var(--clinical-amber) !important;
            background: var(--clinical-amber-bg);
            border-radius: 8px;
            padding: 0.5rem 0.9rem;
            margin-bottom: 1rem;
            line-height: 1.45;
        }
        .disclaimer-strip strong { color: #7C3E0D !important; }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid var(--clinical-border);
        }
        section[data-testid="stSidebar"] * {
            color: var(--clinical-text) !important;
        }
        section[data-testid="stSidebar"] h3 {
            color: var(--clinical-teal-dark) !important;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin: 1.1rem 0 0.3rem 0;
        }
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] small {
            font-size: 0.83rem;
            color: var(--clinical-text-muted) !important;
        }
        section[data-testid="stSidebar"] a {
            color: var(--clinical-teal) !important;
        }
        section[data-testid="stSidebar"] hr {
            margin: 1rem 0;
            border-color: var(--clinical-border);
        }

        /* Sample question chips */
        div[data-testid="stButton"] > button {
            background-color: #FFFFFF !important;
            border: 1px solid var(--clinical-border) !important;
            color: var(--clinical-text) !important;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            font-size: 0.8rem;
            text-align: left;
            width: 100%;
            margin-bottom: 0.35rem;
            transition: all 0.15s ease;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: var(--clinical-teal) !important;
            color: var(--clinical-teal-dark) !important;
            background-color: #EEF6F5 !important;
        }

        /* ---------- Chat area ---------- */
        div[data-testid="stChatMessage"] {
            background-color: var(--clinical-card) !important;
            border: 1px solid var(--clinical-border);
            border-radius: 12px;
        }
        div[data-testid="stChatMessage"] p {
            color: var(--clinical-text) !important;
        }
        .stChatInput textarea {
            color: var(--clinical-text) !important;
        }

        /* Status pill */
        .status-pill {
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 600;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            margin-left: 0.3rem;
            vertical-align: middle;
        }
        .status-ready { background: #DFF4E8; color: #146C43 !important; }
        .status-error { background: #FCE4E4; color: #B02A2A !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Sample questions — anchored to what the loaded guidelines can actually
# answer, since the RAG system only knows what's in the source PDFs
# --------------------------------------------------------------------------
SAMPLE_QUESTIONS = [
    "What is the recommended treatment duration for uncomplicated Staphylococcus aureus bacteremia?",
    "When is source control indicated in bloodstream infections?",
    "What criteria support de-escalating empiric antibiotic therapy?",
    "How should catheter-related bloodstream infections be managed?",
    "What follow-up blood cultures are recommended to confirm clearance of bacteremia?",
    "What distinguishes complicated from uncomplicated bacteremia?",
]

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# --------------------------------------------------------------------------
# Sidebar — product context, not just code plumbing
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### About this tool")
    st.markdown(
        "This assistant retrieves answers **only** from hospital antibiotic "
        "stewardship guideline PDFs loaded into its index. Every answer is "
        "grounded in a specific document and page - nothing is generated "
        "from general knowledge."
    )

    st.markdown("### How it works")
    with st.expander("See the retrieval pipeline", expanded=False):
        st.markdown(
            "1. Guideline PDFs are split into meaningful chunks and embedded "
            "into a FAISS vector index.\n"
            "2. Your question is rewritten into a few clinical phrasings to "
            "catch synonym mismatches (e.g. *complicated* vs *source "
            "control*).\n"
            "3. The best-matching chunks are retrieved and reranked.\n"
            "4. The model answers **only** from those chunks, citing the "
            "source filename and page."
        )

    st.markdown("### Sample questions")
    st.caption("Tap a question to try the assistant - answers depend entirely on what's in the loaded guidelines.")
    for q in SAMPLE_QUESTIONS:
        if st.button(q, key=f"sample_{hash(q)}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("### Limitations")
    st.markdown(
        "- Prototyping tool, not for clinical decision-making\n"
        "- Only answers from the PDFs that were loaded in\n"
        "- Page numbers come from PDF metadata and may not match the "
        "printed page exactly\n"
        "- Always verify the cited source before acting on an answer"
    )

    st.markdown("---")
    st.caption("Built by Sunil Kumar Nallani")
    st.caption("[LinkedIn](https://www.linkedin.com/in/nallani-sunil-kumar-67227a243/) · [GitHub](https://github.com/sunilkumar-nallani/Bacteremia_Clinical_Guideline_Assistant)")

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
status_html = (
    '<span class="status-pill status-ready">Pipeline ready</span>'
    if PIPELINE_READY
    else '<span class="status-pill status-error">Pipeline not loaded</span>'
)
st.markdown(
    f"""
    <div class="app-header">
        <h1>🩺 Bacteremia Clinical Guideline Assistant {status_html}</h1>
        <p>Grounded, citation-first answers pulled directly from hospital antibiotic stewardship guidelines.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="disclaimer-strip">
        <strong>Research and prototyping tool</strong> - not a substitute for clinical judgment or an ID consult.
        Verify every answer against its cited source before clinical use.
    </div>
    """,
    unsafe_allow_html=True,
)

if not PIPELINE_READY:
    st.error(
        f"The RAG pipeline failed to import: `{PIPELINE_ERROR}`. "
        "Make sure `build_index.py` has been run and the pipeline module is on the path."
    )

# --------------------------------------------------------------------------
# Chat history
# --------------------------------------------------------------------------
for message in st.session_state.messages:
    avatar = "🧑‍⚕️" if message["role"] == "user" else "🩺"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --------------------------------------------------------------------------
# Input — either typed, or triggered by a sample-question chip
# --------------------------------------------------------------------------
typed_question = st.chat_input("Ask a question about the loaded guidelines...")

question = st.session_state.pending_question or typed_question
st.session_state.pending_question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍⚕️"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("Searching guidelines..."):
            answer = answer_question(question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# Gentle nudge when the conversation is empty
if not st.session_state.messages:
    st.info("👋 New here? Try one of the sample questions in the sidebar to see how the assistant cites its sources.")
