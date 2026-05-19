# ==========================================================
# susknowledge.py
# FULLY REVISED STABLE VERSION
# ==========================================================

import streamlit as st
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
You are an cross-domain analyst that have knowledge
of human sustainability and software engineering.

You will be given a document containing
information on individual sustainability
and human values relevant to software engineering.

Your task is to produce a structured,
faithful, reusable sustainability knowledge summary.

DOCUMENT:
\"\"\"
{document_text}
\"\"\"

==================================================
TASKS
==================================================

1. Preserve semantic integrity

2. Extract:
- Core definitions
- Models and theories
- Taxonomies
- Operationalization logic
- Actionable knowledge rules

3. Create reusable knowledge representation

4. Produce concise memory summary

==================================================
OUTPUT FORMAT
==================================================

A. Core Definitions

B. Key Models and Theories

C. Taxonomies / Value Systems

D. Operationalization Logic

E. Actionable Knowledge Units

F. Model Memory Summary
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
# INITIALIZE SESSION STATE
# ==========================================================

if "knowledge_text" not in st.session_state:

    st.session_state.knowledge_text = ""

# ==========================================================
# LOAD KNOWLEDGE SOURCE
# ==========================================================

if st.session_state.knowledge_text == "":

    try:

        # --------------------------------------------------
        # LOAD REVISED FILE
        # --------------------------------------------------

        if os.path.exists(REVISED_FILE):

            with open(
                REVISED_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                st.session_state.knowledge_text = (
                    f.read()
                )

        # --------------------------------------------------
        # LOAD PDF
        # --------------------------------------------------

        elif os.path.exists(PDF_FILE):

            loaded_text = load_pdf_text(PDF_FILE)

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

# ==========================================================
# PAGE TITLE
# ==========================================================

st.markdown("""
<div class='content-card'>
    <h2>Sustainability Knowledge</h2>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# LAYOUT
# ==========================================================

left, right = st.columns([1.4, 1])
# ==========================================================
# LEFT PANEL
# ==========================================================

with left:

    st.markdown(
        "## Sustainability Knowledge"
    )

    # ------------------------------------------------------
    # INITIALIZE EDITOR STATE ONCE
    # ------------------------------------------------------

    if "knowledge_text_area" not in st.session_state:

        st.session_state[
            "knowledge_text_area"
        ] = st.session_state.get(
            "knowledge_text",
            ""
        )

    # ------------------------------------------------------
    # TEXT AREA
    # ------------------------------------------------------

    edited_text = st.text_area(

        "Edit Sustainability Knowledge",

        key="knowledge_text_area",

        height=700
    )

    # ------------------------------------------------------
    # SAVE BUTTON
    # ------------------------------------------------------

    if st.button(
        "Save Revised Knowledge",
        key="save_knowledge_btn"
    ):

        try:

            # ------------------------------------------
            # SAVE FILE
            # ------------------------------------------

            save_text(
                edited_text,
                REVISED_FILE
            )

            # ------------------------------------------
            # UPDATE MASTER STATE
            # ------------------------------------------

            st.session_state[
                "knowledge_text"
            ] = edited_text

            # ------------------------------------------
            # UPDATE WORKFLOW
            # ------------------------------------------

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

# ==========================================================
# RIGHT PANEL
# ==========================================================

with right:

    st.markdown(
        "## Knowledge Summarization"
    )

    # ------------------------------------------------------
    # PROVIDER
    # ------------------------------------------------------

    model_provider = st.selectbox(

        "Select Provider",

        [
            "Gemini",
            "OpenAI"
        ]
    )

    # ------------------------------------------------------
    # MODEL
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # API KEY
    # ------------------------------------------------------

    api_key = st.text_input(

        "Enter API Key",

        type="password"
    )

    # ------------------------------------------------------
    # GENERATE BUTTON
    # ------------------------------------------------------

    if st.button(
        "Generate Knowledge Summary",
        key="generate_summary_btn"
    ):

        if not api_key:

            st.error(
                "Please provide API key."
            )

        else:

            # ----------------------------------------------
            # ACTIVE STATE
            # ----------------------------------------------

            if "workflow_state" in st.session_state:

                st.session_state.workflow_state[
                    "knowledge"
                ] = "active"

            with st.spinner(
                "Generating sustainability knowledge summary..."
            ):

                try:

                    # --------------------------------------
                    # BUILD PROMPT
                    # --------------------------------------

                    prompt = build_prompt(
                        edited_text
                    )

                    # --------------------------------------
                    # GEMINI
                    # --------------------------------------

                    if model_provider == "Gemini":

                        result = run_gemini(

                            prompt,

                            api_key,

                            model_name
                        )

                    # --------------------------------------
                    # OPENAI
                    # --------------------------------------

                    else:

                        result = run_openai(

                            prompt,

                            api_key,

                            model_name
                        )

                    # --------------------------------------
                    # SAVE SUMMARY
                    # --------------------------------------

                    save_text(
                        result,
                        SUMMARY_FILE
                    )

                    # --------------------------------------
                    # UPDATE WORKFLOW
                    # --------------------------------------

                    if "workflow_state" in st.session_state:

                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "saved"

                    # --------------------------------------
                    # SUCCESS
                    # --------------------------------------

                    st.success(
                        f"Summary saved to {SUMMARY_FILE}"
                    )

                    # --------------------------------------
                    # OUTPUT
                    # --------------------------------------

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

                    # --------------------------------------
                    # FAILURE
                    # --------------------------------------

                    if "workflow_state" in st.session_state:

                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "failed"

                    st.error(str(e))
