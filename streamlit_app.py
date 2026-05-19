import streamlit as st
import streamlit.components.v1 as components
import os

from pypdf import PdfReader

import google.generativeai as genai
from openai import OpenAI
# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

PDF_FILE = os.path.join(
    BASE_DIR,
    "SusGRL.pdf"
)

REVISED_FILE = os.path.join(
    BASE_DIR,
    "revised.txt"
)

SUMMARY_FILE = os.path.join(
    BASE_DIR,
    "summary_output.txt"
)

# ==========================================================
# PDF LOADER
# ==========================================================

@st.cache_data(show_spinner=False)
def load_pdf_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    return text

# ==========================================================
# SAVE TEXT
# ==========================================================

def save_text(text, filename):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)

# ==========================================================
# BUILD PROMPT
# ==========================================================

def build_prompt(document_text):

    prompt = f"""
You are an cross-domain analyst that have knowledge of human sustainabability and software engineering. You will be given with a document that contain information on individual sustainability and human values that needs to be perceived in software engineering.

Your task is to read the provided document and produce a structured, faithful, and reusable knowledge summary of its content. Summarize contents such that might be useful for sustainable software design. The goal is NOT just summarization, but extracting knowledge that can be reliably reused in subsequent reasoning tasks.

DOCUMENT:
\"\"\"
{document_text}
\"\"\"

Follow these instructions strictly:

1. Preserve Semantic Integrity
- Do NOT omit critical concepts, definitions, or relationships.
- Avoid simplification that changes meaning.
- Do NOT introduce external knowledge.

2. Structure the Output into the Following Sections:

A. Core Definitions
- Summarize definitions of key concepts.
- Maintain original meaning but you may rephrase for your own clarity.

B. Key Models and Theories
- Extract all theoretical constructs (e.g., value hierarchies, levels, frameworks).
- Represent them in structured form.

C. Taxonomies / Value Systems
- Extract relevant categories, classifications, or value systems for software design.
- Summarize mapping relationships (e.g., value → system implication).

D. Operationalization Logic
- Explain how abstract concepts (e.g., human values) are translated into system-level requirements.

E. Actionable Knowledge Units
- Convert insights into reusable rules or patterns:
  Format:
  - IF [context]
  - THEN [design implication]

3. Output Style
- Use clear, structured formatting.
- Avoid verbosity but ensure completeness.
- Use precise terminology (no vague summaries).

4. Final Step: Knowledge Compression
- Provide a concise "Model Memory Summary"
- This should be a concise representation suitable for reuse in prompts.

"""

    return prompt

# ==========================================================
# GEMINI
# ==========================================================

def run_gemini(
    prompt,
    api_key,
    model_name
):

    genai.configure(
        api_key=api_key
    )

    model = genai.GenerativeModel(
        model_name
    )

    response = model.generate_content(
        prompt
    )

    return response.text

# ==========================================================
# OPENAI
# ==========================================================

def run_openai(
    prompt,
    api_key,
    model_name
):

    client = OpenAI(
        api_key=api_key
    )

    response = client.chat.completions.create(

        model=model_name,

        messages=[

            {
                "role": "system",
                "content":
                "You are a sustainability knowledge analyst."
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content
# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ISR Generation Assistant",
    layout="wide"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"

# ==========================================================
# WORKFLOW STATE
# ==========================================================

if "workflow_state" not in st.session_state:

    st.session_state.workflow_state = {

        # pending
        # uploaded
        # saved
        # active
        # failed

        "scope": "pending",

        "knowledge": "pending",

        "concerns": "pending",

        "isr": "pending"
    }

# ==========================================================
# STEP CONFIG
# ==========================================================

STEP_CONFIG = {

    "scope": {

        "label": "System Scope",

        "icon": "📄"
    },

    "knowledge": {

        "label": "Knowledge Summary",

        "icon": "📘"
    },

    "concerns": {

        "label": "Generate Concerns",

        "icon": "💡"
    },

    "isr": {

        "label": "Produce ISR",

        "icon": "⚙️"
    }
}

# ==========================================================
# STEP ORDER
# ==========================================================

STEP_ORDER = [
    "scope",
    "knowledge",
    "concerns",
    "isr"
]

# ==========================================================
# STATE COLORS
# ==========================================================

STATE_COLORS = {

    "pending": "#facc15",

    "uploaded": "#86efac",

    "saved": "#22c55e",

    "active": "#2563eb",

    "failed": "#ef4444"
}

# ==========================================================
# CUSTOM CSS
# ==========================================================

CUSTOM_CSS = """
<style>

/* =====================================================
APP BACKGROUND
===================================================== */

.stApp {

    background-color: #dfe7fd;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {

    background-color: #021024;
}

/* =====================================================
SIDEBAR TEXT
===================================================== */

section[data-testid="stSidebar"] * {

    color: #06b6d4 !important;
}

/* =====================================================
SIDEBAR BUTTONS
===================================================== */

.stButton > button {

    width: 100%;

    background-color: transparent;

    border: none;

    color: #06b6d4 !important;

    font-size: 18px;

    text-align: left;

    padding: 14px 18px;

    border-radius: 12px;

    transition: 0.3s;
}

.stButton > button:hover {

    background-color: #2563eb;

    color: white !important;
}

/* =====================================================
MAIN TITLE
===================================================== */

.main-title {

    font-size: 42px;

    font-weight: 800;

    color: #0f172a;

    margin-bottom: 5px;
}

.sub-title {

    font-size: 18px;

    color: #64748b;

    margin-bottom: 25px;
}

/* =====================================================
METRIC CARD
===================================================== */

.metric-card {

    background: white;

    padding: 24px;

    border-radius: 18px;

    box-shadow: 0px 3px 12px rgba(0,0,0,0.06);

    border: 1px solid #dce3f0;
}

/* =====================================================
CONTENT CARD
===================================================== */

.content-card {

    background: white;

    padding: 24px;

    border-radius: 18px;

    box-shadow: 0px 2px 8px rgba(0,0,0,0.04);

    border: 1px solid #dce3f0;

    margin-bottom: 20px;
}

</style>
"""

st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <h1 style='
            color:#06b6d4;
            font-size:40px;
            font-weight:800;
        '>
        Navigation
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    if st.button("🏠 Dashboard"):
        st.session_state.selected_page = "Dashboard"

    if st.button("📄 System Scope"):
        st.session_state.selected_page = "System Scope"

    if st.button("📘 Sustainability Knowledge"):
        st.session_state.selected_page = "Sustainability Knowledge"

    if st.button("💡 Generate Concerns"):
        st.session_state.selected_page = "Generate Concerns"

    if st.button("⚙️ Produce ISR"):
        st.session_state.selected_page = "Produce ISR"

# ==========================================================
# MAIN TITLE
# ==========================================================

st.markdown("""
<div class='main-title'>
Concerns to ISR Generation
</div>

<div class='sub-title'>
Transform sustainability concerns into actionable
Individual Sustainability Requirements
</div>
""", unsafe_allow_html=True)

# ==========================================================
# TOP ACTION BAR
# ==========================================================

top_col1, top_col2 = st.columns([8, 1])

with top_col2:

    if st.button("🔄 Reset Workflow"):

        st.session_state.workflow_state = {

            "scope": "pending",

            "knowledge": "pending",

            "concerns": "pending",

            "isr": "pending"
        }

        # ---------------------------------------------
        # OPTIONAL: remove saved files
        # ---------------------------------------------

        if os.path.exists("saved_scope.txt"):
            os.remove("saved_scope.txt")

        if os.path.exists("revised.txt"):
            os.remove("revised.txt")

        st.rerun()
# ==========================================================
# CALCULATE PROGRESS
# ==========================================================

def calculate_progress():

    score = 0

    for step in STEP_ORDER:

        state = st.session_state.workflow_state[step]

        if state == "uploaded":

            score += 0.5

        elif state == "saved":

            score += 1

    progress_percent = (
        score / len(STEP_ORDER)
    ) * 100

    return progress_percent

# ==========================================================
# BUILD PROGRESS BAR
# ==========================================================

progress_html = """
<style>

.progress-container {

    width: 100%;

    margin-top: 10px;

    margin-bottom: 40px;
}

.progressbar {

    display: flex;

    justify-content: space-between;

    position: relative;

    margin: 50px 0;

    padding: 0;
}

.progressbar::before {

    content: '';

    position: absolute;

    top: 28px;

    left: 0;

    width: 100%;

    height: 10px;

    background: #d1d5db;

    z-index: 0;

    border-radius: 20px;
}

.progress-step {

    position: relative;

    text-align: center;

    flex: 1;

    z-index: 1;
}

.progress-step-circle {

    width: 58px;

    height: 58px;

    line-height: 58px;

    border-radius: 50%;

    color: white;

    margin: auto;

    font-size: 28px;

    font-weight: bold;

    border: 4px solid white;

    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}

.progress-step-label {

    margin-top: 14px;

    font-size: 15px;

    font-weight: 700;

    color: #334155;
}

.progress-step-status {

    margin-top: 6px;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1px;

    color: #64748b;
}

.progress-line {

    position: absolute;

    top: 28px;

    left: 0;

    height: 10px;

    background: linear-gradient(
        90deg,
        #22c55e,
        #16a34a
    );

    z-index: 0;

    border-radius: 20px;

    transition: width 0.5s ease-in-out;
}

</style>

<div class="progress-container">

    <div class="progressbar">
"""

# ==========================================================
# PROGRESS %
# ==========================================================

progress_percent = calculate_progress()

progress_html += f"""
<div class="progress-line"
     style="width:{progress_percent}%;">
</div>
"""

# ==========================================================
# STEP CIRCLES
# ==========================================================

for step in STEP_ORDER:

    config = STEP_CONFIG[step]

    label = config["label"]

    icon = config["icon"]

    state = st.session_state.workflow_state[step]

    color = STATE_COLORS[state]

    progress_html += f"""

    <div class="progress-step">

        <div
            class="progress-step-circle"
            style="background:{color};"
        >
            {icon}
        </div>

        <div class="progress-step-label">
            {label}
        </div>

        <div class="progress-step-status">
            {state.upper()}
        </div>

    </div>
    """

progress_html += """
    </div>
</div>
"""

# ==========================================================
# RENDER PROGRESS BAR
# ==========================================================

components.html(
    progress_html,
    height=220,
    scrolling=False
)

# ==========================================================
# PAGE NAVIGATION
# ==========================================================

selected_page = st.session_state.selected_page

# ==========================================================
# DASHBOARD
# ==========================================================

if selected_page == "Dashboard":

    st.markdown("## Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown("""
        <div class="metric-card">
            <h4>Total Concerns</h4>
            <h1>12</h1>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="metric-card">
            <h4>Total ISRs</h4>
            <h1>21</h1>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class="metric-card">
            <h4>Human Values</h4>
            <h1>9</h1>
        </div>
        """, unsafe_allow_html=True)

    with c4:

        st.markdown("""
        <div class="metric-card">
            <h4>NFR Categories</h4>
            <h1>6</h1>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# SYSTEM SCOPE PAGE
# ==========================================================

elif selected_page == "System Scope":

    st.markdown("""
    <div class='content-card'>
        <h2>System Scope Upload</h2>
    </div>
    """, unsafe_allow_html=True)

    scope_text = ""

    # ------------------------------------------------------
    # LOAD EXISTING FILE
    # ------------------------------------------------------

    if os.path.exists("saved_scope.txt"):

        with open(
            "saved_scope.txt",
            "r",
            encoding="utf-8"
        ) as f:

            scope_text = f.read()

        st.session_state.workflow_state[
            "scope"
        ] = "saved"

    # ------------------------------------------------------
    # FILE UPLOADER
    # ------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload System Scope File",
        type=["txt"]
    )

    if uploaded_file is not None:

        scope_text = uploaded_file.read().decode("utf-8")

        st.session_state.workflow_state[
            "scope"
        ] = "uploaded"

    # ------------------------------------------------------
    # EDITABLE AREA
    # ------------------------------------------------------

    edited_scope = st.text_area(
        "Editable System Scope",
        value=scope_text,
        height=450
    )

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    if st.button("Save System Scope"):

        with open(
            "saved_scope.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(edited_scope)

        st.session_state.workflow_state[
            "scope"
        ] = "saved"

        st.success(
            "System scope saved successfully."
        )

# ==========================================================
# SUSTAINABILITY KNOWLEDGE
# ==========================================================

elif selected_page == "Sustainability Knowledge":


# ==========================================================
# SUSTAINABILITY KNOWLEDGE
# ==========================================================

elif selected_page == "Sustainability Knowledge":

    # ------------------------------------------------------
    # INITIALIZE SESSION STATE
    # ------------------------------------------------------

    if "knowledge_text" not in st.session_state:

        st.session_state.knowledge_text = ""

    # ------------------------------------------------------
    # LOAD KNOWLEDGE SOURCE
    # ------------------------------------------------------

    if st.session_state.knowledge_text == "":

        try:

            # ----------------------------------------------
            # LOAD REVISED FILE
            # ----------------------------------------------

            if os.path.exists(REVISED_FILE):

                with open(
                    REVISED_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    st.session_state.knowledge_text = (
                        f.read()
                    )

            # ----------------------------------------------
            # LOAD PDF
            # ----------------------------------------------

            elif os.path.exists(PDF_FILE):

                loaded_text = load_pdf_text(
                    PDF_FILE
                )

                st.session_state[
                    "knowledge_text"
                ] = loaded_text

                st.session_state[
                    "knowledge_text_area"
                ] = loaded_text

            else:

                st.warning(
                    f"{PDF_FILE} not found."
                )

        except Exception as e:

            st.error(
                f"Error loading knowledge source: {e}"
            )

    # ======================================================
    # PAGE TITLE
    # ======================================================

    st.markdown("""
    <div class='content-card'>
        <h2>Sustainability Knowledge</h2>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # LAYOUT
    # ======================================================

    left, right = st.columns([1.4, 1])

    # ======================================================
    # LEFT PANEL
    # ======================================================

    with left:

        st.markdown(
            "## Sustainability Knowledge"
        )

        # --------------------------------------------------
        # INITIALIZE EDITOR STATE
        # --------------------------------------------------

        if "knowledge_text_area" not in st.session_state:

            st.session_state[
                "knowledge_text_area"
            ] = st.session_state.get(
                "knowledge_text",
                ""
            )

        # --------------------------------------------------
        # TEXT AREA
        # --------------------------------------------------

        edited_text = st.text_area(

            "Edit Sustainability Knowledge",

            key="knowledge_text_area",

            height=700
        )

        # --------------------------------------------------
        # SAVE BUTTON
        # --------------------------------------------------

        if st.button(
            "Save Revised Knowledge",
            key="save_knowledge_btn"
        ):

            try:

                save_text(
                    edited_text,
                    REVISED_FILE
                )

                st.session_state[
                    "knowledge_text"
                ] = edited_text

                if "workflow_state" in st.session_state:

                    st.session_state.workflow_state[
                        "knowledge"
                    ] = "uploaded"

                st.success(
                    f"Saved to {REVISED_FILE}"
                )

            except Exception as e:

                st.error(
                    f"Save failed: {e}"
                )

    # ======================================================
    # RIGHT PANEL
    # ======================================================

    with right:

        st.markdown(
            "## Knowledge Summarization"
        )

        # --------------------------------------------------
        # PROVIDER
        # --------------------------------------------------

        model_provider = st.selectbox(

            "Select Provider",

            [
                "Gemini",
                "OpenAI"
            ]
        )

        # --------------------------------------------------
        # MODEL
        # --------------------------------------------------

        if model_provider == "Gemini":

            model_name = st.selectbox(

                "Select Gemini Model",

                [
                    "gemini-2.5-flash",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash"
                ]
            )

        else:

            model_name = st.selectbox(

                "Select OpenAI Model",

                [
                    "gpt-4o",
                    "gpt-4.1-mini",
                    "gpt-4-turbo"
                ]
            )

        # --------------------------------------------------
        # API KEY
        # --------------------------------------------------

        api_key = st.text_input(

            "Enter API Key",

            type="password"
        )

        # --------------------------------------------------
        # GENERATE BUTTON
        # --------------------------------------------------

        if st.button(
            "Generate Knowledge Summary",
            key="generate_summary_btn"
        ):

            if not api_key:

                st.error(
                    "Please provide API key."
                )

            else:

                try:

                    if "workflow_state" in st.session_state:

                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "active"

                    with st.spinner(
                        "Generating sustainability knowledge summary..."
                    ):

                        prompt = build_prompt(
                            edited_text
                        )

                        # ------------------------------
                        # GEMINI
                        # ------------------------------

                        if model_provider == "Gemini":

                            result = run_gemini(

                                prompt,

                                api_key,

                                model_name
                            )

                        # ------------------------------
                        # OPENAI
                        # ------------------------------

                        else:

                            result = run_openai(

                                prompt,

                                api_key,

                                model_name
                            )

                        # ------------------------------
                        # SAVE SUMMARY
                        # ------------------------------

                        save_text(
                            result,
                            SUMMARY_FILE
                        )

                        if "workflow_state" in st.session_state:

                            st.session_state.workflow_state[
                                "knowledge"
                            ] = "saved"

                        st.success(
                            f"Summary saved to {SUMMARY_FILE}"
                        )

                        st.markdown(
                            "## Generated Summary"
                        )

                        st.text_area(

                            "LLM Output",

                            value=result,

                            height=500,

                            key="summary_output_area"
                        )

                except Exception as e:

                    if "workflow_state" in st.session_state:

                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "failed"

                    st.error(str(e))
# ==========================================================
# GENERATE CONCERNS
# ==========================================================

elif selected_page == "Generate Concerns":

    st.markdown("""
    <div class='content-card'>
        <h2>Generate Sustainability Concerns</h2>
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input(
        "Enter Gemini/OpenAI API Key",
        type="password"
    )

    if st.button("Generate Concerns"):

        st.session_state.workflow_state[
            "concerns"
        ] = "saved"

        st.success("Concerns generated.")

# ==========================================================
# PRODUCE ISR
# ==========================================================

elif selected_page == "Produce ISR":

    st.markdown("""
    <div class='content-card'>
        <h2>Produce ISR</h2>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate ISR"):

        st.session_state.workflow_state[
            "isr"
        ] = "saved"

        st.success(
            "ISRs generated successfully."
        )

        st.markdown("""
        <div class='content-card'>

            <h3>ISR-1</h3>

            <p>
            The system shall provide adaptive
            interfaces that minimize cognitive
            overload for healthcare professionals
            during high-pressure workflows.
            </p>

        </div>
        """, unsafe_allow_html=True)
