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

if "scope_saved" not in st.session_state:
    st.session_state.scope_saved = False

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
# ENTERPRISE WORKFLOW PROGRESS TRACKER
# FULL REVISED VERSION
# ==========================================================

import streamlit as st
import streamlit.components.v1 as components

# ==========================================================
# INITIALIZE SESSION STATE
# ==========================================================

if "workflow_state" not in st.session_state:

    st.session_state.workflow_state = {

        # possible values:
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
# STEP CONFIGURATION
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
# STEP ORDER
# ==========================================================

STEP_ORDER = [
    "scope",
    "knowledge",
    "concerns",
    "isr"
]

# ==========================================================
# UPDATE WORKFLOW STATE
# ==========================================================

def update_workflow_state(step_name, state):

    st.session_state.workflow_state[step_name] = state

# ==========================================================
# CALCULATE PROGRESS %
# ==========================================================

def calculate_progress():

    score = 0

    for step in STEP_ORDER:

        state = st.session_state.workflow_state[step]

        # ---------------------------------------------
        # Partial completion
        # ---------------------------------------------

        if state == "uploaded":

            score += 0.5

        # ---------------------------------------------
        # Full completion
        # ---------------------------------------------

        elif state == "saved":

            score += 1

    progress_percent = (
        score / len(STEP_ORDER)
    ) * 100

    return progress_percent

# ==========================================================
# RENDER PROGRESS BAR
# ==========================================================

def render_workflow():

    progress_percent = calculate_progress()

    html = """

    <style>

    .workflow-container {

        width: 100%;

        margin-top: 20px;

        margin-bottom: 40px;

        padding-left: 10px;

        padding-right: 10px;
    }

    .workflow-bar {

        display: flex;

        justify-content: space-between;

        position: relative;

        margin-top: 60px;
    }

    .workflow-bar::before {

        content: '';

        position: absolute;

        top: 28px;

        left: 0;

        width: 100%;

        height: 10px;

        background: #d1d5db;

        border-radius: 20px;

        z-index: 0;
    }

    .workflow-progress {

        position: absolute;

        top: 28px;

        left: 0;

        height: 10px;

        background: linear-gradient(
            90deg,
            #22c55e,
            #16a34a
        );

        border-radius: 20px;

        z-index: 1;

        transition: width 0.6s ease-in-out;
    }

    .workflow-step {

        position: relative;

        text-align: center;

        flex: 1;

        z-index: 2;
    }

    .circle {

        width: 60px;

        height: 60px;

        line-height: 60px;

        border-radius: 50%;

        margin: auto;

        font-size: 28px;

        font-weight: bold;

        color: white;

        border: 4px solid white;

        box-shadow: 0px 3px 12px rgba(0,0,0,0.18);

        transition: all 0.3s ease-in-out;
    }

    .step-label {

        margin-top: 14px;

        font-size: 15px;

        font-weight: 700;

        color: #0f172a;
    }

    .step-status {

        margin-top: 8px;

        font-size: 12px;

        font-weight: 700;

        color: #64748b;

        letter-spacing: 0.5px;
    }

    </style>

    <div class="workflow-container">

        <div class="workflow-bar">
    """

    # ======================================================
    # PROGRESS LINE
    # ======================================================

    html += f"""

    <div
        class="workflow-progress"
        style="width:{progress_percent}%;">
    </div>

    """

    # ======================================================
    # STEP CIRCLES
    # ======================================================

    for step in STEP_ORDER:

        state = st.session_state.workflow_state[step]

        config = STEP_CONFIG[step]

        label = config["label"]

        icon = config["icon"]

        color = STATE_COLORS[state]

        html += f"""

        <div class="workflow-step">

            <div
                class="circle"
                style="background:{color};"
            >
                {icon}
            </div>

            <div class="step-label">
                {label}
            </div>

            <div class="step-status">
                {state.upper()}
            </div>

        </div>

        """

    html += """

        </div>

    </div>

    """

    components.html(
        html,
        height=220,
        scrolling=False
    )

# ==========================================================
# RENDER WORKFLOW BAR
# ==========================================================

render_workflow()

# ==========================================================
# EXAMPLE UI ACTIONS
# ==========================================================

st.markdown("---")

st.subheader("Example Workflow Actions")

c1, c2, c3, c4 = st.columns(4)

# ==========================================================
# SYSTEM SCOPE
# ==========================================================

with c1:

    if st.button("Upload Scope"):

        update_workflow_state(
            "scope",
            "uploaded"
        )

    if st.button("Save Scope"):

        update_workflow_state(
            "scope",
            "saved"
        )

# ==========================================================
# KNOWLEDGE
# ==========================================================

with c2:

    if st.button("Summarize Knowledge"):

        update_workflow_state(
            "knowledge",
            "saved"
        )

# ==========================================================
# CONCERNS
# ==========================================================

with c3:

    if st.button("Generate Concerns"):

        update_workflow_state(
            "concerns",
            "saved"
        )

# ==========================================================
# ISR
# ==========================================================

with c4:

    if st.button("Generate ISR"):

        update_workflow_state(
            "isr",
            "saved"
        )

# ==========================================================
# FAILURE EXAMPLE
# ==========================================================

if st.button("Simulate Failure"):

    update_workflow_state(
        "knowledge",
        "failed"
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
        st.session_state.scope_saved = True


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
