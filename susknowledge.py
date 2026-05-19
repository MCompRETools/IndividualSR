# ==========================================================
# SUSTAINABILITY KNOWLEDGE PAGE
# susknowledge.py
# ==========================================================

import os
import streamlit as st
from PyPDF2 import PdfReader

# ==========================================================
# OPTIONAL MODEL IMPORTS
# ==========================================================

import google.generativeai as genai
from openai import OpenAI

# ==========================================================
# FILE PATHS
# ==========================================================

PDF_FILE = "SusGRL.pdf"

REVISED_FILE = "revised.txt"

SUMMARY_FILE = "summary_output.txt"

# ==========================================================
# PAGE TITLE
# ==========================================================

st.markdown("""
<h1 style='color:#0f172a;'>
Sustainability Knowledge Management
</h1>
""", unsafe_allow_html=True)

# ==========================================================
# LOAD PDF TEXT
# ==========================================================

def load_pdf_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted + "\n"

    return text

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
# GEMINI CALL
# ==========================================================

def run_gemini(prompt, api_key, model_name):

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)

    response = model.generate_content(prompt)

    return response.text

# ==========================================================
# OPENAI CALL
# ==========================================================

def run_openai(prompt, api_key, model_name):

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(

        model=model_name,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content

# ==========================================================
# SAVE FILE
# ==========================================================

def save_text(text, filename):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)

# ==========================================================
# LOAD EXISTING KNOWLEDGE
# ==========================================================

if "knowledge_text" not in st.session_state:

    if os.path.exists(REVISED_FILE):

        with open(
            REVISED_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            st.session_state.knowledge_text = f.read()

    else:

        st.session_state.knowledge_text = load_pdf_text(PDF_FILE)

# ==========================================================
# LAYOUT
# ==========================================================

left, right = st.columns([1.2, 1])

# ==========================================================
# LEFT PANEL
# ==========================================================

with left:

    st.markdown("## Sustainability Knowledge")

    edited_text = st.text_area(

        "Edit Sustainability Knowledge",

        value=st.session_state.knowledge_text,

        height=700
    )

    st.session_state.knowledge_text = edited_text

    if st.button("Save Revised Knowledge"):

        save_text(
            edited_text,
            REVISED_FILE
        )

        st.success(
            f"Saved to {REVISED_FILE}"
        )

# ==========================================================
# RIGHT PANEL
# ==========================================================

with right:

    st.markdown("## Knowledge Summarization")

    # ------------------------------------------------------
    # MODEL SELECTION
    # ------------------------------------------------------

    model_provider = st.selectbox(

        "Select Provider",

        [
            "Gemini",
            "OpenAI"
        ]
    )

    # ------------------------------------------------------
    # MODEL LIST
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
                "gpt-4.1",
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
    # GENERATE SUMMARY
    # ------------------------------------------------------

    if st.button("Generate Knowledge Summary"):

        if not api_key:

            st.error("Please provide API key.")

        else:
            if "workflow_state" in st.session_state:

                st.session_state.workflow_state[
                    "knowledge"
                ] = "active"
                
            with st.spinner(
                "Generating knowledge summary..."
            ):

                prompt = build_prompt(
                    st.session_state.knowledge_text
                )

                try:

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
                    # UPDATE GLOBAL WORKFLOW STATE
                    # --------------------------------------
                    
                    if "workflow_state" in st.session_state:
                    
                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "saved"
                    
                    st.success(
                        f"Summary saved to {SUMMARY_FILE}"
                    )

                    st.markdown("## Generated Summary")

                    st.text_area(

                        "LLM Output",

                        value=result,

                        height=500
                    )

                except Exception as e:

                    
                    if "workflow_state" in st.session_state:

                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "failed"
                    st.error(str(e))

# ==========================================================
# LOAD EXISTING SUMMARY
# ==========================================================

if os.path.exists(SUMMARY_FILE):

    st.markdown("---")

    st.markdown("## Existing Saved Summary")

    with open(
        SUMMARY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        saved_summary = f.read()

    st.text_area(

        "Saved Summary",

        value=saved_summary,

        height=400
    )
