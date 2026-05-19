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
# WORKFLOW TRACKER
# ==========================================================

def workflow_step(title, completed):

    color = "#22c55e" if completed else "#facc15"

    icon = "✅" if completed else "🟡"

    return f"""
    <div style="
        flex:1;
        background:white;
        border-radius:16px;
        padding:20px;
        border:2px solid {color};
        text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,0.04);
    ">

        <div style="
            font-size:32px;
            margin-bottom:10px;
        ">
            {icon}
        </div>

        <div style="
            font-size:15px;
            font-weight:700;
            color:#0f172a;
        ">
            {title}
        </div>

    </div>
    """

workflow_html = f"""
<div style="
    display:flex;
    gap:18px;
    margin-top:20px;
    margin-bottom:35px;
">

    {workflow_step(
        "System Scope Elicitation",
        st.session_state.scope_uploaded
    )}

    {workflow_step(
        "Knowledge Summarization",
        st.session_state.knowledge_summarized
    )}

    {workflow_step(
        "Generate Sustainability Concerns",
        st.session_state.concerns_generated
    )}

    {workflow_step(
        "Produce ISR",
        st.session_state.isr_generated
    )}

</div>
"""

st.markdown(
    workflow_html,
    unsafe_allow_html=True
)

# ==========================================================
# PAGE NAVIGATION
# ==========================================================

selected_page = st.session_state.selected_page

# ==========================================================
# DASHBOARD
# ==========================================================

if selected_page == "Dashboard":

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown("""
        <div class='metric-card'>
            <h3>Total Concerns</h3>
            <h1>12</h1>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class='metric-card'>
            <h3>Total Questions</h3>
            <h1>24</h1>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class='metric-card'>
            <h3>NFR Categories</h3>
            <h1>6</h1>
        </div>
        """, unsafe_allow_html=True)

    with c4:

        st.markdown("""
        <div class='metric-card'>
            <h3>Generated ISRs</h3>
            <h1>21</h1>
        </div>
        """, unsafe_allow_html=True)

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

    st.markdown("""
    <div class='content-card'>
    <h2>Sustainability Knowledge</h2>
    </div>
    """, unsafe_allow_html=True)

    knowledge = st.text_area(
        "Knowledge Content",
        value="Sustainability knowledge appears here...",
        height=500
    )

    if st.button("Generate Summary"):

        st.session_state.knowledge_summarized = True

        st.success("Knowledge summarized.")

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
