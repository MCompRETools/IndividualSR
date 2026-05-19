import streamlit as st
import os

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ISR Generation Assistant",
    layout="wide"
)

# ==========================================================
# SESSION STATE FLAGS
# ==========================================================

if "scope_uploaded" not in st.session_state:
    st.session_state.scope_uploaded = False

if "knowledge_summarized" not in st.session_state:
    st.session_state.knowledge_summarized = False

if "concerns_generated" not in st.session_state:
    st.session_state.concerns_generated = False

if "isr_generated" not in st.session_state:
    st.session_state.isr_generated = False

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"

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
MAIN TITLES
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
METRIC CARDS
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

    st.sidebar.markdown(
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
# ENTERPRISE WORKFLOW STATE MANAGEMENT
# ==========================================================

# Possible states:
# - completed
# - active
# - pending
# - failed

if "workflow_state" not in st.session_state:

    st.session_state.workflow_state = {

        "scope": "active",

        "knowledge": "pending",

        "concerns": "pending",

        "isr": "pending"
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

STEP_LABELS = {

    "scope": "System Scope",

    "knowledge": "Knowledge Summary",

    "concerns": "Generate Concerns",

    "isr": "Produce ISR"
}

STEP_ICONS = {

    "scope": "📄",

    "knowledge": "📘",

    "concerns": "💡",

    "isr": "⚙️"
}

# ==========================================================
# UPDATE WORKFLOW FUNCTION
# ==========================================================

def update_workflow(step_name):

    current_index = STEP_ORDER.index(step_name)

    # ---------------------------------------------
    # Mark current step completed
    # ---------------------------------------------

    st.session_state.workflow_state[step_name] = "completed"

    # ---------------------------------------------
    # Activate next step
    # ---------------------------------------------

    if current_index + 1 < len(STEP_ORDER):

        next_step = STEP_ORDER[current_index + 1]

        if (
            st.session_state.workflow_state[next_step]
            != "completed"
        ):

            st.session_state.workflow_state[next_step] = "active"

# ==========================================================
# OPTIONAL FAILURE FUNCTION
# ==========================================================

def mark_failed(step_name):

    st.session_state.workflow_state[step_name] = "failed"

# ==========================================================
# WORKFLOW PROGRESS BAR UI
# ==========================================================

import streamlit.components.v1 as components

def render_workflow():

    workflow_state = st.session_state.workflow_state

    # ------------------------------------------------------
    # Calculate completed steps
    # ------------------------------------------------------

    completed_count = sum(

        1 for s in workflow_state.values()
        if s == "completed"
    )

    progress_percent = (
        completed_count / len(STEP_ORDER)
    ) * 100

    # ------------------------------------------------------
    # HTML + CSS
    # ------------------------------------------------------

    html = """
    <style>

    .workflow-container {

        width: 100%;
        margin-top: 20px;
        margin-bottom: 40px;
    }

    .workflow-bar {

        display: flex;
        justify-content: space-between;
        position: relative;
        margin-top: 40px;
    }

    .workflow-bar::before {

        content: '';

        position: absolute;

        top: 28px;

        left: 0;

        width: 100%;

        height: 8px;

        background: #d1d5db;

        border-radius: 10px;

        z-index: 0;
    }

    .workflow-progress {

        position: absolute;

        top: 28px;

        left: 0;

        height: 8px;

        background: #22c55e;

        border-radius: 10px;

        z-index: 1;

        transition: width 0.5s ease-in-out;
    }

    .workflow-step {

        position: relative;

        text-align: center;

        flex: 1;

        z-index: 2;
    }

    .circle {

        width: 58px;

        height: 58px;

        line-height: 58px;

        border-radius: 50%;

        margin: auto;

        font-size: 26px;

        font-weight: bold;

        color: white;

        border: 4px solid white;

        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }

    .completed {
        background: #22c55e;
    }

    .active {
        background: #2563eb;
    }

    .pending {
        background: #facc15;
    }

    .failed {
        background: #ef4444;
    }

    .step-label {

        margin-top: 14px;

        font-size: 15px;

        font-weight: 700;

        color: #334155;
    }

    </style>

    <div class="workflow-container">

        <div class="workflow-bar">
    """

    # ------------------------------------------------------
    # Progress Fill
    # ------------------------------------------------------

    html += f"""
    <div class="workflow-progress"
         style="width:{progress_percent}%;">
    </div>
    """

    # ------------------------------------------------------
    # Steps
    # ------------------------------------------------------

    for step in STEP_ORDER:

        state = workflow_state[step]

        label = STEP_LABELS[step]

        icon = STEP_ICONS[step]

        html += f"""

        <div class="workflow-step">

            <div class="circle {state}">
                {icon}
            </div>

            <div class="step-label">
                {label}
            </div>

        </div>
        """

    html += """
        </div>
    </div>
    """

    # ------------------------------------------------------
    # Render
    # ------------------------------------------------------

    components.html(
        html,
        height=180,
        scrolling=False
    )

# ==========================================================
# RENDER WORKFLOW
# ==========================================================

render_workflow()

# ==========================================================
# EXAMPLES OF STATE UPDATE
# ==========================================================

# ---------------------------------------------
# After saving system scope:
# ---------------------------------------------
#
# update_workflow("scope")
#
# ---------------------------------------------
# After summarization:
# ---------------------------------------------
#
# update_workflow("knowledge")
#
# ---------------------------------------------
# After concern generation:
# ---------------------------------------------
#
# update_workflow("concerns")
#
# ---------------------------------------------
# After ISR generation:
# ---------------------------------------------
#
# update_workflow("isr")
#
# ---------------------------------------------
# If something fails:
# ---------------------------------------------
#
# mark_failed("knowledge")
#
# ==========================================================
# SYSTEM SCOPE
# ==========================================================

elif selected_page == "System Scope":

    st.markdown("""
    <div class='content-card'>
    <h2>System Scope Upload</h2>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload System Scope File",
        type=["txt"]
    )

    scope_text = ""

    if uploaded_file is not None:

        scope_text = uploaded_file.read().decode("utf-8")

        st.session_state.scope_uploaded = True

    edited_scope = st.text_area(
        "Editable System Scope",
        value=scope_text,
        height=400
    )

    if st.button("Save System Scope"):

        with open(
            "saved_scope.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(edited_scope)

        st.success("System scope saved.")

# ==========================================================
# SUSTAINABILITY KNOWLEDGE
# ==========================================================

elif selected_page == "Sustainability Knowledge":
    import susknowledge


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

        st.session_state.concerns_generated = True

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

        st.session_state.isr_generated = True

        st.success("ISRs generated successfully.")

        st.markdown("""
        <div class='content-card'>

        <h3>ISR-1</h3>

        <p>
        The system shall provide adaptive interfaces
        that minimize cognitive overload for healthcare
        professionals during high-pressure workflows.
        </p>

        </div>
        """, unsafe_allow_html=True)
