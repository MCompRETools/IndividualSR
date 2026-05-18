import streamlit as st
import pandas as pd
import json

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="ISR Elicitation Framework",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================

st.title("Individual Sustainability Requirement Framework")

st.markdown("""
Interactive framework for:
- sustainability concern analysis
- SuSAF alignment
- ISR generation
- NFR-aware reasoning
""")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Configuration")

uploaded_csv = st.sidebar.file_uploader(
    "Upload Concern CSV",
    type=["csv"]
)

uploaded_scope = st.sidebar.file_uploader(
    "Upload System Scope",
    type=["txt"]
)

uploaded_summary = st.sidebar.file_uploader(
    "Upload Sustainability Summary",
    type=["txt"]
)

model_name = st.sidebar.selectbox(
    "Select LLM",
    [
        "gemini-2.5-flash",
        "gpt-4.1",
        "claude-sonnet"
    ]
)

generate_button = st.sidebar.button(
    "Generate ISR"
)

# =====================================================
# LOAD FILES
# =====================================================

if uploaded_csv:

    df = pd.read_csv(uploaded_csv)

    st.success("CSV Loaded")

    # ================================================
    # MAIN LAYOUT
    # ================================================

    left, right = st.columns([1, 2])

    # ================================================
    # LEFT PANEL
    # ================================================

    with left:

        st.subheader("Concerns")

        selected_index = st.selectbox(
            "Select Concern",
            range(len(df)),
            format_func=lambda x: df.iloc[x]["Concern"][:80]
        )

        selected_row = df.iloc[selected_index]

        st.markdown("### Human Values")
        st.write(selected_row["Targeted Human Values"])

        st.markdown("### NFR Properties")
        st.write(selected_row["System Properties"])

        st.markdown("### Score")
        st.write(selected_row["Score"])

    # ================================================
    # RIGHT PANEL
    # ================================================

    with right:

        st.subheader("Concern Analysis")

        st.markdown("### Concern")
        st.info(selected_row["Concern"])

        st.markdown("### Retrieved Question")
        st.warning(selected_row["Question"])

        st.markdown("### Analysis / Reasoning")
        st.write(selected_row["Analysis or Reasoning"])

        # ============================================
        # ISR GENERATION
        # ============================================

        if generate_button:

            with st.spinner("Generating ISR..."):

                # ------------------------------------
                # PLACEHOLDER ISR
                # Replace with LLM call
                # ------------------------------------

                generated_output = {
                    "requirement_id": "ISR-1",
                    "requirement":
                        "The system shall provide configurable "
                        "patient data filtering and prioritization "
                        "mechanisms to reduce cognitive overload "
                        "among healthcare professionals.",
                    "supported_nfrs": [
                        "Usability",
                        "Reliability",
                        "Safety"
                    ],
                    "reasoning":
                        "The requirement mitigates cognitive "
                        "overload by reducing unnecessary "
                        "information density."
                }

                st.markdown("## Generated ISR")

                st.json(generated_output)

# =====================================================
# SYSTEM SCOPE DISPLAY
# =====================================================

if uploaded_scope:

    scope_text = uploaded_scope.read().decode("utf-8")

    with st.expander("System Scope"):

        st.text(scope_text)

# =====================================================
# KNOWLEDGE DISPLAY
# =====================================================

if uploaded_summary:

    summary_text = uploaded_summary.read().decode("utf-8")

    with st.expander("Sustainability Knowledge Summary"):

        st.text(summary_text)
