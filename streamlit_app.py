# ==========================================================
# ISR GENERATION ASSISTANT
# Multi-Page Interactive Streamlit Application
# ==========================================================

import os
import fitz
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
# ==========================================================
# WORKFLOW STATUS FLAGS
# ==========================================================

if "scope_uploaded" not in st.session_state:
    st.session_state.scope_uploaded = False

if "knowledge_summarized" not in st.session_state:
    st.session_state.knowledge_summarized = False

if "concerns_generated" not in st.session_state:
    st.session_state.concerns_generated = False

if "isr_generated" not in st.session_state:
    st.session_state.isr_generated = False
# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ISR Generation Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==========================================================
# WORKFLOW PROGRESS TRACKER
# ==========================================================

def workflow_step(title, completed):

    color = "#22c55e" if completed else "#facc15"

    icon = "✅" if completed else "🟡"

    return f"""
    <div style="
        flex:1;
        background:white;
        border-radius:16px;
        padding:18px;
        border:2px solid {color};
        text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,0.04);
    ">

        <div style="
            font-size:30px;
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
""", unsafe_allow_html=True)
# ==========================================================
# FILE PATHS
# ==========================================================

UPDATED_KNOWLEDGE_FILE = "updatedSRknowledge.txt"

# ==========================================================
# CUSTOM CSS
# ==========================================================

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* =====================================================
APP BACKGROUND
===================================================== */

.stApp {
    background-color: #e0e7ff;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #021024 0%,
        #021024 100%
    );
}

/* =====================================================
SIDEBAR TEXT
===================================================== */

section[data-testid="stSidebar"] * {
    color: #06b6d4;
}

/* =====================================================
METRIC CARDS
===================================================== */

.metric-card {

    background: white;

    padding: 22px;

    border-radius: 16px;

    box-shadow: 0px 2px 10px rgba(0,0,0,0.06);

    border: 1px solid #e6e9f0;
}

/* =====================================================
TITLES
===================================================== */

.main-title {

    font-size: 36px;

    font-weight: 800;

    color: #0f172a;
}

.sub-title {

    color: #06b6d4;
}

/* =====================================================
CONTENT CARDS
===================================================== */

.card {

    background: white;

    padding: 20px;

    border-radius: 14px;

    border: 1px solid #dce3f0;

    margin-bottom: 15px;
}

/* =====================================================
TEXTAREA
===================================================== */

textarea {
    font-size: 15px !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SYSTEM SCOPE PAGE
# ==========================================================

elif selected_page == "System Scope":

    st.markdown("## System Scope")

    SYSTEM_SCOPE_FILE = "saved_system_scope.txt"

    # ------------------------------------------------------
    # INITIALIZE SESSION STATE
    # ------------------------------------------------------

    if "system_scope_text" not in st.session_state:
        st.session_state.system_scope_text = ""

    # ------------------------------------------------------
    # LOAD EXISTING SAVED FILE
    # ------------------------------------------------------

    if (
        st.session_state.system_scope_text == ""
        and os.path.exists(SYSTEM_SCOPE_FILE)
    ):

        with open(
            SYSTEM_SCOPE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            st.session_state.system_scope_text = f.read()
            st.session_state.scope_uploaded = True
    # ------------------------------------------------------
    # FILE UPLOAD
    # ------------------------------------------------------

    uploaded_scope = st.file_uploader(
        "Upload System Scope Document",
        type=["txt"]
    )

    # ------------------------------------------------------
    # LOAD UPLOADED FILE
    # ------------------------------------------------------

    if uploaded_scope is not None:

        uploaded_text = uploaded_scope.read().decode("utf-8")

        st.session_state.system_scope_text = uploaded_text

    # ------------------------------------------------------
    # DISPLAY EDITABLE AREA
    # ------------------------------------------------------

    edited_scope = st.text_area(
        "Edit System Scope",
        value=st.session_state.system_scope_text,
        height=600
    )

    # ------------------------------------------------------
    # UPDATE SESSION STATE LIVE
    # ------------------------------------------------------

    st.session_state.system_scope_text = edited_scope

    # ------------------------------------------------------
    # SAVE BUTTON
    # ------------------------------------------------------

    if st.button("Save System Scope"):

        with open(
            SYSTEM_SCOPE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(edited_scope)

        st.success(
            "System scope saved successfully."
        )

    # ------------------------------------------------------
    # SHOW SAVE STATUS
    # ------------------------------------------------------

    if os.path.exists(SYSTEM_SCOPE_FILE):

        st.info(
            f"Current persisted file: {SYSTEM_SCOPE_FILE}"
        )

# ==========================================================
# SUSTAINABILITY KNOWLEDGE PAGE
# ==========================================================

elif selected_page == "Sustainability Knowledge":

    import susknowledge

# ==========================================================
# GENERATE CONCERNS PAGE
# ==========================================================

elif selected_page == "Generate Concerns":

    st.markdown("## Generate Sustainability Concerns")

    gemini_key = st.text_input(
        "Enter Gemini API Key",
        type="password"
    )

    concern_scope = st.text_area(
        "Enter System Scope",
        height=250
    )

    if st.button("Generate Concerns"):

        if not gemini_key:

            st.error("Please enter Gemini API Key.")

        else:

            st.success("Generating concerns...")
            st.session_state.concerns_generated = True
            # ----------------------------------------------
            # PLACEHOLDER RESPONSE
            # Replace with Gemini API call
            # ----------------------------------------------

            generated_response = """
1. Cognitive overload among healthcare professionals
2. Over-reliance on AI-generated recommendations
3. Reduced patient autonomy due to opaque consent handling
4. Privacy risks from sensitive biometric data collection
"""

            st.markdown("### Generated Concerns")

            st.text_area(
                "Model Response",
                value=generated_response,
                height=300
            )

# ==========================================================
# PRODUCE ISR PAGE
# ==========================================================

elif selected_page == "Produce ISR":

    st.markdown("## Produce Individual Sustainability Requirements")

    uploaded_concern_csv = st.file_uploader(
        "Upload Concern CSV",
        type=["csv"]
    )

    if uploaded_concern_csv:

        df = pd.read_csv(uploaded_concern_csv)

        st.success("Concern CSV Loaded")

        selected_concern = st.selectbox(
            "Select Concern",
            df["Concern"]
        )

        row = df[df["Concern"] == selected_concern].iloc[0]

        st.markdown("### Concern")

        st.info(row["Concern"])

        st.markdown("### Human Values")

        st.write(row["Targeted Human Values"])

        st.markdown("### Question")

        st.warning(row["Question"])

        st.markdown("### NFR Properties")

        st.write(row["System Properties"])

        st.markdown("### Analysis")

        st.write(row["Analysis or Reasoning"])
        st.session_state.isr_generated = True
        if st.button("Generate ISR"):

            generated_isr = """
{
  "requirement_id": "ISR-1",
  "requirement": "The system shall provide configurable patient information prioritization mechanisms to reduce cognitive overload among healthcare professionals.",
  "targeted_values": [
      "Health",
      "Achievement"
  ],
  "supported_nfrs": [
      "Usability",
      "Efficiency"
  ],
  "reasoning": "Reducing information overload improves usability and reduces stress."
}
"""

            st.markdown("## Generated ISR")

            st.code(
                generated_isr,
                language="json"
            )
