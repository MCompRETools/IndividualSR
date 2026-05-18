# ==========================================================
# ISR GENERATION ASSISTANT
# Multi-Page Interactive Streamlit Application
# ==========================================================

import os
import fitz
import streamlit as st
import pandas as pd

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
# FILE PATHS
# ==========================================================

UPDATED_KNOWLEDGE_FILE = "updatedSRknowledge.txt"

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #03122e 0%, #021024 100%);
}

section[data-testid="stSidebar"] * {
    color: white;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.06);
    border: 1px solid #e6e9f0;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #0f172a;
}

.sub-title {
    color: #64748b;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #dce3f0;
    margin-bottom: 15px;
}

textarea {
    font-size: 15px !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("# 🧠 ISR Generation Assistant")

    st.markdown("### Individual Sustainability Requirements")

    st.markdown("---")

    selected_page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "System Scope",
            "Sustainability Knowledge",
            "Generate Concerns",
            "Produce ISR"
        ]
    )

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="main-title">
ISR Generation Framework
</div>

<div class="sub-title">
Interactive Sustainability-aware Requirements Engineering Platform
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

    st.markdown("## System Scope")

    uploaded_scope = st.file_uploader(
        "Upload System Scope Document",
        type=["txt"]
    )

    if uploaded_scope:

        scope_text = uploaded_scope.read().decode("utf-8")

        edited_scope = st.text_area(
            "Edit System Scope",
            value=scope_text,
            height=500
        )

        if st.button("Save System Scope"):

            with open(
                "saved_system_scope.txt",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(edited_scope)

            st.success("System scope saved.")

# ==========================================================
# SUSTAINABILITY KNOWLEDGE PAGE
# ==========================================================

elif selected_page == "Sustainability Knowledge":

    st.markdown("## Sustainability Knowledge")

    uploaded_pdf = st.file_uploader(
        "Upload Sustainability Knowledge PDF",
        type=["pdf"]
    )

    extracted_text = ""

    # ------------------------------------------------------
    # LOAD UPDATED FILE IF EXISTS
    # ------------------------------------------------------

    if os.path.exists(UPDATED_KNOWLEDGE_FILE):

        with open(
            UPDATED_KNOWLEDGE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            extracted_text = f.read()

    # ------------------------------------------------------
    # OTHERWISE LOAD PDF
    # ------------------------------------------------------

    elif uploaded_pdf:

        pdf_doc = fitz.open(
            stream=uploaded_pdf.read(),
            filetype="pdf"
        )

        for page in pdf_doc:

            extracted_text += page.get_text()

    # ------------------------------------------------------
    # DISPLAY EDITABLE TEXT
    # ------------------------------------------------------

    if extracted_text:

        edited_knowledge = st.text_area(
            "Edit Sustainability Knowledge",
            value=extracted_text,
            height=600
        )

        if st.button("Save Sustainability Knowledge"):

            with open(
                UPDATED_KNOWLEDGE_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(edited_knowledge)

            st.success(
                "Updated sustainability knowledge saved."
            )

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
