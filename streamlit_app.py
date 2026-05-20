import streamlit as st
import streamlit.components.v1 as components
import os
from github import Github
import base64
from pypdf import PdfReader
import json
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
# SAVE FILE TO GITHUB
# ==========================================================

def save_to_github(
    file_content,
    repo_name,
    file_path,
    github_token,
    commit_message="Update revised knowledge"
):

    try:

        # --------------------------------------------------
        # AUTH
        # --------------------------------------------------

        g = Github(github_token)

        repo = g.get_repo(repo_name)

        # --------------------------------------------------
        # CHECK EXISTING FILE
        # --------------------------------------------------

        try:

            existing_file = repo.get_contents(
                file_path
            )

            repo.update_file(

                path=file_path,

                message=commit_message,

                content=file_content,

                sha=existing_file.sha
            )

        # --------------------------------------------------
        # CREATE NEW FILE
        # --------------------------------------------------

        except Exception:

            repo.create_file(

                path=file_path,

                message=commit_message,

                content=file_content
            )

        return True

    except Exception as e:

        st.error(
            f"GitHub Save Failed: {e}"
        )

        return False
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
# GENERATE INDIVIDUAL CONCERNS
# ==========================================================
# ==========================================================
# BUILD INDIVIDUAL CONCERN PROMPT
# ==========================================================

def build_concern_prompt(

    summary,

    scope,

    analyst_opinion=""

):

    prompt = f"""
    You are an expert in software requirements engineering with deep knowledge of individual sustainability in socio-technical systems. You have been  provided with a knowledge summary of individual sustainability concepts, frameworks, and value mappings. Use this knowledge actively throughout your reasoning.
    ---
    
    ## Knowledge Summary
    
    {summary}
    
    ---
    
    ## Your Task
    
    Given a product's scope, user characteristics, and features, you will  identify key INDIVIDUAL SUSTAINABILITY CONCERNS — not requirements, but meaningful concerns that a requirements engineer should consider when  designing such a system.
    
    A concern is a potential risk, tension, or impact area related to  individual sustainability dimensions (health, privacy, safety, lifelong learning, self-awareness and free will) or human values that the product may affect — positively or negatively.
    
    **Important distinctions**:
    - A CONCERN is not a requirement. It does not say "the system shall..."
    - A CONCERN identifies *what could go wrong or what needs careful attention* for individual sustainability.
    - A CONCERN should be grounded in at least one individual sustainability category (mentioned in SuSAF framework) or human value from the knowledge summary.
    - A CONCERN may be a tension between two values (e.g., security vs. freedom) or a unidirectional risk (e.g., erosion of autonomy).
    
    ---
    
    ## Reasoning Protocol
    
    For a given product scope, follow these steps in order.
    
    -Step 1 — Understand the system**
    Understand what the product does, who uses it (targeted end users- mentioned), and its key features. Identify the primary domain (e.g., health, education, finance, social or any other) of the software.
    
    -Step 2- Consider user characteristics (carefully consider the targeted end user mentioned within the system scope) and vulnerabilities for each user group mentioned
    
    **Step 3 — Identify relevant human values**
    Consider both positively  activated values (the system could support them) and at-risk values (the system could undermine them).
    You must consider each category defined in SuSAF framework.
    
    
    -Step 4 — Derive concerns**
    For each identified individual risk dimension, formulate concerns that might be of interest for the given product. Each concern must:
    - Be written as a clear, specific statement of what needs attention
    - Reference the sustainability dimension of the SuSAF framework it relates to
    - Set of human values the concern might impact. If there are more than one human values affected- assign an order among them.
    - Mention the specific user group or feature that triggers the concern
    - Set a basis for your derived concern. The basis should contain (i) excerpt from system scope that made you think of particular concern and (ii) your own reasoning.
    
    Consider the following examples for your own understanding of the task.
    
    Example 1:
    
    INPUT:
    Product Scope: Mobile health monitoring app that continuously tracks biometric data of elderly users and sends automated alerts to caregivers when anomalies are detected.
    Users: Elderly individuals
    Features: Continuous biometric tracking, AI anomaly detection, automated caregiver alerts, health dashboard
    
    OUTPUT:
    - Loss of autonomy due to over-reliance on automated health monitoring replacing self-directed health awareness
    - Privacy concerns from continuous collection of sensitive biometric data without granular user consent controls
    - Psychological distress caused by frequent uninterpretable AI alerts generating chronic anxiety rather than reassurance
    - Dependence on system reducing the user's natural bodily self-awareness and health literacy over time
    
    Example 2:
    
    INPUT:
    Product Scope: Online learning platform that delivers personalised course content to university students through algorithmic recommendations and benchmarks individual performance against peer cohorts.
    Users: University students
    Features: AI content personalisation, performance tracking dashboard, peer comparison analytics, progress benchmarking
    
    OUTPUT:
    - Impact on learner autonomy due to algorithmic recommendations replacing independent self-directed study pathway decisions
    - Chronic academic anxiety and psychological stress generated by continuous performance tracking and peer comparison mechanics
    - Privacy concerns regarding granular learning behaviour data captured beyond the student's awareness or consent
    - Feedback loops progressively narrowing content complexity for low-engagement students — permanently limiting academic development for those who need challenge most
    - Unequal access affecting students with low digital literacy or limited device availability
    - Erosion of intrinsic learning motivation as students optimise for platform metrics rather than genuine understanding
    - Skill atrophy in self-directed study as students become permanently dependent on AI-curated learning pathways
    - Risk of performance data being shared with institutions or third parties beyond the educational context students originally consented to
    
    Example 3:
    
    INPUT:
    Product Scope: Digital banking platform that uses automated credit scoring, personalised financial product recommendations, and transaction anomaly detection to manage and advise on customer finances.
    Users: General banking customers including elderly, low-literacy, and low-income users
    Features: Automated credit scoring, AI financial recommendations, transaction anomaly detection, personalised product suggestions, automated account management
    
    OUTPUT:
    - Loss of financial autonomy due to opaque AI credit scoring decisions made without human review or plain-language explanation accessible to low-literacy users
    - Privacy concerns from continuous behavioural transaction monitoring creating sensitive financial profiles whose secondary use may not be transparent or consented to
    - Exclusion of elderly and low-literacy users who cannot understand, contest, or override automated financial decisions affecting their economic well-being
    - Psychological distress caused by automated anomaly detection flags that generate account restrictions or alerts without accessible explanation or correction pathways
    - Dependence on AI financial recommendations reducing users' own financial literacy and capacity for independent financial decision-making over time

    --------------------------------------------------
    PRODUCT SCOPE
    --------------------------------------------------
    
    {scope}
    """
    # ------------------------------------------------------
    # OUTPUT FORMAT
    # ------------------------------------------------------

    prompt += """
    
    --------------------------------------------------
    OUTPUT FORMAT
    --------------------------------------------------
    
    Return only valid json format as:
    {{
    
      "sustainability_concerns": {{
        "health": [
          {{
            "concern": "<string>",
            "impact": "positive | negative | mixed",
            "Human Values affected (ordered from high to low)": ["<string>"],
            "User Groups Affected (ordered from high to low)": "<string>",
            "Basis": "<string>"
          }}
        ],
        "lifelong_learning": [
          {{
            "concern": "<string>",
            "impact": "positive | negative | mixed",
            "Human Values affected (ordered from high to low)": ["<string>"],
            "User Groups Affected (ordered from high to low)": "<string>",
            "Basis": "<string>"
          }}
        ],
        "privacy": [
          {{
            "concern": "<string>",
            "impact": "positive | negative | mixed",
            "Human Values affected (ordered from high to low)": ["<string>"],
            "User Groups Affected (ordered from high to low)": "<string>",
            "Basis": "<string>"
          }}
        ],
        "safety": [
          {{
            "concern": "<string>",
            "impact": "positive | negative | mixed",
            "Human Values affected (ordered from high to low)": ["<string>"],
            "User Groups Affected (ordered from high to low)": "<string>",
            "Basis": "<string>"
          }}
        ],
        "self_awareness_and_free_will": [
          {{
            "concern": "<string>",
            "impact": "positive | negative | mixed",
            "Human Values affected (ordered from high to low)": ["<string>"],
            "User Groups Affected (ordered from high to low)": "<string>",
            "Basis": "<string>"
          }}
        ]
      }}
    }}
    Your output will be evaluated on:
    - Alignment with knowledge summary
    - Coverage of relevant human values
    - Relevance to product context
    """
    return prompt
def generate_individual_concerns(
    summary,
    scope,
    api_key,
    provider,
    model_name,
    analyst_opinion=""
):

    prompt = build_concern_prompt(
        summary,
        scope
    )

    # ------------------------------------------------------
    # ADD ANALYST FEEDBACK
    # ------------------------------------------------------

    if analyst_opinion.strip():

        prompt += f"""

        ------------------------------------------------------

        Analyst Opinion / Feedback:
        {analyst_opinion}
        Incorporate this feedback carefully while deriving sustainability concerns.
        """

    # ------------------------------------------------------
    # GOOGLE
    # ------------------------------------------------------

    if provider == "Google":

        result = run_gemini(
            prompt,
            api_key,
            model_name
        )

    # ------------------------------------------------------
    # OPENAI
    # ------------------------------------------------------

    else:

        result = run_openai(
            prompt,
            api_key,
            model_name
        )

    # ------------------------------------------------------
    # CLEAN JSON
    # ------------------------------------------------------

    cleaned = (
        result
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(cleaned)
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

    # ======================================================
    # INITIALIZE SESSION STATE
    # ======================================================

    if "knowledge_text" not in st.session_state:

        st.session_state.knowledge_text = ""

    if "summary_editor" not in st.session_state:

        st.session_state.summary_editor = ""

    # ======================================================
    # LOAD KNOWLEDGE SOURCE
    # ======================================================

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

                loaded_text = load_pdf_text(
                    PDF_FILE
                )

                st.session_state.knowledge_text = (
                    loaded_text
                )

            else:

                st.warning(
                    f"{PDF_FILE} not found."
                )

        except Exception as e:

            st.error(
                f"Error loading knowledge source: {e}"
            )

    # ======================================================
    # LOAD EXISTING SUMMARY
    # ======================================================

    if st.session_state.summary_editor == "":

        if os.path.exists(SUMMARY_FILE):

            with open(
                SUMMARY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                st.session_state.summary_editor = (
                    f.read()
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

    left, right = st.columns([1.2, 1])

    # ======================================================
    # LEFT PANEL
    # ======================================================

    with left:

        st.markdown(
            "## Sustainability Knowledge"
        )

        edited_text = st.text_area(

            "Edit Sustainability Knowledge",

            key="knowledge_text",

            height=700
        )

        # --------------------------------------------------
        # SAVE KNOWLEDGE
        # --------------------------------------------------

        if st.button(
            "Save Revised Knowledge",
            key="save_knowledge_btn"
        ):

            try:

                # ------------------------------------------
                # SAVE LOCAL FILE
                # ------------------------------------------

                save_text(
                    edited_text,
                    REVISED_FILE
                )

                # ------------------------------------------
                # SAVE TO GITHUB
                # ------------------------------------------

                save_to_github(

                    file_content=edited_text,

                    repo_name="MCompRETools/IndividualSR",

                    file_path="revised.txt",

                    github_token=st.secrets[
                        "GITHUB_TOKEN"
                    ],

                    commit_message=(
                        "Update revised sustainability knowledge"
                    )
                )

                # ------------------------------------------
                # UPDATE WORKFLOW
                # ------------------------------------------

                st.session_state.workflow_state[
                    "knowledge"
                ] = "uploaded"

                st.success(
                    f"Saved to {REVISED_FILE}"
                )

                st.rerun()

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
                "Google",
                "OpenAI"
            ]
        )

        # --------------------------------------------------
        # MODEL
        # --------------------------------------------------

        if model_provider == "Google":

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
        # GENERATE SUMMARY
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

                    st.session_state.workflow_state[
                        "knowledge"
                    ] = "active"

                    with st.spinner(
                        "Generating sustainability knowledge summary..."
                    ):

                        prompt = build_prompt(
                            edited_text
                        )

                        # ----------------------------------
                        # GEMINI
                        # ----------------------------------

                        if model_provider == "Google":

                            result = run_gemini(

                                prompt,

                                api_key,

                                model_name
                            )

                        # ----------------------------------
                        # OPENAI
                        # ----------------------------------

                        else:

                            result = run_openai(

                                prompt,

                                api_key,

                                model_name
                            )

                        # ----------------------------------
                        # SAVE LOCAL
                        # ----------------------------------

                        save_text(
                            result,
                            SUMMARY_FILE
                        )

                        # ----------------------------------
                        # SAVE TO GITHUB
                        # ----------------------------------

                        save_to_github(

                            file_content=result,

                            repo_name="MCompRETools/IndividualSR",

                            file_path="summary_output.txt",

                            github_token=st.secrets[
                                "GITHUB_TOKEN"
                            ],

                            commit_message=(
                                "Update sustainability summary"
                            )
                        )

                        # ----------------------------------
                        # UPDATE SESSION
                        # ----------------------------------

                        st.session_state.summary_editor = (
                            result
                        )

                        st.session_state.workflow_state[
                            "knowledge"
                        ] = "saved"

                        st.success(
                            f"Summary saved to {SUMMARY_FILE}"
                        )

                        st.rerun()

                except Exception as e:

                    st.session_state.workflow_state[
                        "knowledge"
                    ] = "failed"

                    st.error(str(e))

        # ==================================================
        # SUMMARY TEXT AREA
        # ==================================================

        st.markdown(
            "## Generated Summary"
        )

        edited_summary = st.text_area(

            "Edit Sustainability Knowledge Summary",

            key="summary_editor",

            height=500
        )

        # --------------------------------------------------
        # SAVE SUMMARY
        # --------------------------------------------------

        if st.button(
            "Save Edited Summary",
            key="save_summary_btn"
        ):

            try:

                updated_summary = (
                    st.session_state.summary_editor
                )

                # ------------------------------------------
                # SAVE LOCAL
                # ------------------------------------------

                save_text(
                    updated_summary,
                    SUMMARY_FILE
                )

                # ------------------------------------------
                # SAVE TO GITHUB
                # ------------------------------------------

                save_to_github(

                    file_content=updated_summary,

                    repo_name="MCompRETools/IndividualSR",

                    file_path="summary_output.txt",

                    github_token=st.secrets[
                        "GITHUB_TOKEN"
                    ],

                    commit_message=(
                        "Update summarized sustainability knowledge"
                    )
                )

                st.session_state.workflow_state[
                    "knowledge"
                ] = "saved"

                st.success(
                    "Summary updated successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Failed to save summary: {e}"
                )
# ==========================================================
# GENERATE CONCERNS
# ==========================================================

elif selected_page == "Generate Concerns":

    st.markdown("""
    <div class='content-card'>
        <h2>Generate Individual Sustainability Concerns</h2>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # LOAD REQUIRED FILES
    # ======================================================

    summary_text = ""

    scope_text = ""

    if os.path.exists(SUMMARY_FILE):

        with open(
            SUMMARY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            summary_text = f.read()

    if os.path.exists("saved_scope.txt"):

        with open(
            "saved_scope.txt",
            "r",
            encoding="utf-8"
        ) as f:

            scope_text = f.read()

    # ======================================================
    # PROVIDER
    # ======================================================

    provider = st.selectbox(

        "Select Provider",

        [
            "Google",
            "OpenAI"
        ]
    )

    # ======================================================
    # MODEL
    # ======================================================

    if provider == "Google":

        model_name = st.selectbox(

            "Select Gemini Model",

            [
                "gemini-2.5-flash",
                "gemini-1.5-pro"
            ]
        )

    else:

        model_name = st.selectbox(

            "Select OpenAI Model",

            [
                "gpt-4o",
                "gpt-4.1-mini"
            ]
        )

    # ======================================================
    # API KEY
    # ======================================================

    api_key = st.text_input(
        "Enter API Key",
        type="password"
    )

    # ======================================================
    # ANALYST FEEDBACK
    # ======================================================

    analyst_feedback = st.text_area(

        "Analyst Opinion / Feedback",

        placeholder="""
Example:
- Focus more on privacy concerns.
- Consider elderly voters separately.
- Add concerns related to cognitive overload.
""",

        height=150
    )

    # ======================================================
    # GENERATE BUTTON
    # ======================================================

    if st.button("Generate Sustainability Concerns"):

        try:

            with st.spinner(
                "Generating sustainability concerns..."
            ):

                generated_concerns = (
                    generate_individual_concerns(

                        summary=summary_text,

                        scope=scope_text,

                        api_key=api_key,

                        provider=provider,

                        model_name=model_name,

                        analyst_opinion=analyst_feedback
                    )
                )

                st.session_state.generated_concerns = (
                    generated_concerns
                )

                st.session_state.workflow_state[
                    "concerns"
                ] = "saved"

                st.success(
                    "Concerns generated successfully."
                )

        except Exception as e:

            st.error(str(e))

    # ======================================================
    # DISPLAY GENERATED CONCERNS
    # ======================================================

    if "generated_concerns" in st.session_state:

        concerns_data = (
            st.session_state.generated_concerns
        )

        sustainability_concerns = (
            concerns_data["sustainability_concerns"]
        )

        for category, concerns in (
            sustainability_concerns.items()
        ):

            st.markdown(f"""
            <div class='content-card'>
                <h3>{category.replace("_", " ").title()}</h3>
            </div>
            """, unsafe_allow_html=True)

            for idx, concern_obj in enumerate(concerns):

                unique_id = (
                    f"{category}_{idx}"
                )

                with st.expander(
                    f"Concern {idx+1}"
                ):

                    # --------------------------------------
                    # CONCERN TEXT
                    # --------------------------------------

                    edited_concern = st.text_area(

                        "Concern",

                        value=concern_obj["concern"],

                        key=f"concern_{unique_id}",

                        height=100
                    )

                    # --------------------------------------
                    # IMPACT
                    # --------------------------------------

                    impact = st.selectbox(

                        "Impact",

                        [
                            "positive",
                            "negative",
                            "mixed"
                        ],

                        index=[
                            "positive",
                            "negative",
                            "mixed"
                        ].index(
                            concern_obj["impact"]
                        ),

                        key=f"impact_{unique_id}"
                    )

                    # --------------------------------------
                    # HUMAN VALUES
                    # --------------------------------------

                    human_values = st.text_area(

                        "Human Values",

                        value="\n".join(
                            concern_obj[
                                "Human Values affected (ordered from high to low)"
                            ]
                        ),

                        key=f"values_{unique_id}",

                        height=100
                    )

                    # --------------------------------------
                    # USER GROUPS
                    # --------------------------------------

                    user_groups = st.text_area(

                        "User Groups Affected",

                        value=concern_obj[
                            "User Groups Affected (ordered from high to low)"
                        ],

                        key=f"users_{unique_id}",

                        height=100
                    )

                    # --------------------------------------
                    # BASIS
                    # --------------------------------------

                    basis = st.text_area(

                        "Basis",

                        value=concern_obj["Basis"],

                        key=f"basis_{unique_id}",

                        height=150
                    )

                    # --------------------------------------
                    # ANALYST COMMENT
                    # --------------------------------------

                    analyst_note = st.text_area(

                        "Analyst Comment",

                        key=f"comment_{unique_id}",

                        height=100
                    )

                    # --------------------------------------
                    # ACTION BUTTONS
                    # --------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        if st.button(
                            "✅ Accept",
                            key=f"accept_{unique_id}"
                        ):

                            concern_obj["status"] = (
                                "accepted"
                            )

                            st.success(
                                "Concern accepted."
                            )

                    with col2:

                        if st.button(
                            "❌ Reject",
                            key=f"reject_{unique_id}"
                        ):

                            concern_obj["status"] = (
                                "rejected"
                            )

                            st.warning(
                                "Concern rejected."
                            )

                    with col3:

                        if st.button(
                            "💾 Save Edit",
                            key=f"save_{unique_id}"
                        ):

                            concern_obj["concern"] = (
                                edited_concern
                            )

                            concern_obj["impact"] = (
                                impact
                            )

                            concern_obj[
                                "Human Values affected (ordered from high to low)"
                            ] = [
                                x.strip()
                                for x in human_values.split("\n")
                                if x.strip()
                            ]

                            concern_obj[
                                "User Groups Affected (ordered from high to low)"
                            ] = (
                                user_groups
                            )

                            concern_obj["Basis"] = (
                                basis
                            )

                            concern_obj[
                                "Analyst Feedback"
                            ] = analyst_note

                            st.success(
                                "Concern updated."
                            )

        # ==================================================
        # SAVE ALL
        # ==================================================

        if st.button(
            "Save All Concerns"
        ):

            with open(
                "generated_concerns.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(

                    st.session_state.generated_concerns,

                    f,

                    indent=4,

                    ensure_ascii=False
                )

            st.success(
                "All concerns saved."
            )
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
