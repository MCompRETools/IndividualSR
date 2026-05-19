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
# RESPONSIVE WORKFLOW PROGRESS BAR
# ==========================================================

import streamlit.components.v1 as components

# ----------------------------------------------------------
# STEP STATUS
# ----------------------------------------------------------

steps = [
    ("System Scope", st.session_state.scope_uploaded),
    ("Knowledge Summary", st.session_state.knowledge_summarized),
    ("Generate Concerns", st.session_state.concerns_generated),
    ("Produce ISR", st.session_state.isr_generated)
]

# ----------------------------------------------------------
# BUILD HTML
# ----------------------------------------------------------

progress_html = """
<style>

.progress-container {

    width: 100%;
    margin-top: 10px;
    margin-bottom: 40px;
}

.progressbar {

    counter-reset: step;
    display: flex;
    justify-content: space-between;
    position: relative;
    margin: 40px 0;
    padding: 0;
}

.progressbar::before {

    content: '';
    position: absolute;
    top: 28px;
    left: 0;
    width: 100%;
    height: 8px;
    background: #d1d5db;
    z-index: 0;
    border-radius: 10px;
}

.progress-step {

    position: relative;
    text-align: center;
    flex: 1;
    z-index: 1;
}

.progress-step-circle {

    width: 55px;
    height: 55px;
    line-height: 55px;
    border-radius: 50%;
    background: #facc15;
    color: white;
    margin: auto;
    font-size: 22px;
    font-weight: bold;
    border: 4px solid white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.progress-step.active .progress-step-circle {

    background: #22c55e;
}

.progress-step-label {

    margin-top: 14px;
    font-size: 15px;
    font-weight: 700;
    color: #334155;
}

.progress-line {

    position: absolute;
    top: 28px;
    left: 0;
    height: 8px;
    background: #22c55e;
    z-index: 0;
    border-radius: 10px;
}

</style>

<div class="progress-container">

    <div class="progressbar">
"""

# ----------------------------------------------------------
# PROGRESS %
# ----------------------------------------------------------

completed_steps = sum([1 for _, status in steps if status])

progress_percent = 0

if len(steps) > 1:
    progress_percent = (
        (completed_steps - 1)
        / (len(steps) - 1)
    ) * 100

progress_percent = max(0, progress_percent)

progress_html += f"""
<div class="progress-line"
     style="width:{progress_percent}%;">
</div>
"""

# ----------------------------------------------------------
# STEP CIRCLES
# ----------------------------------------------------------

for idx, (label, status) in enumerate(steps):

    active_class = "active" if status else ""

    progress_html += f"""
    <div class="progress-step {active_class}">

        <div class="progress-step-circle">
            {idx + 1}
        </div>

        <div class="progress-step-label">
            {label}
        </div>

    </div>
    """

progress_html += """
    </div>
</div>
"""

# ----------------------------------------------------------
# RENDER
# ----------------------------------------------------------

components.html(
    progress_html,
    height=180,
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
