import streamlit as st
import streamlit.components.v1 as components
import os
import google.generativeai as genai
from github import Github
import base64
from pypdf import PdfReader
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import shutil
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
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
# RETRIEVAL — SIMILARITY
# ==========================================================

def retrieve_similarity(
    vectorstore,
    query,
    k=5
):

    retrieved = (
        vectorstore.similarity_search(
            query,
            k=k
        )
    )

    return retrieved


# ==========================================================
# RETRIEVAL — MMR
# ==========================================================

def retrieve_MMR(
    vectorstore,
    query,
    k=5,
    lambda_mult=0.5
):

    retrieved = (
        vectorstore.max_marginal_relevance_search(
            query,
            k=k,
            lambda_mult=lambda_mult
        )
    )

    return retrieved
def retrieve_prompt_questions(
    vectorstore,
    concern,
    k=5,
    lambda_mult=0.5
):

    # ------------------------------------------------------
    # SIMILARITY SEARCH
    # ------------------------------------------------------

    similarity_docs = retrieve_similarity(
        vectorstore,
        concern,
        k=k
    )

    # ------------------------------------------------------
    # MMR SEARCH
    # ------------------------------------------------------

    mmr_docs = retrieve_MMR(
        vectorstore,
        concern,
        k=k,
        lambda_mult=lambda_mult
    )

    # ------------------------------------------------------
    # COMBINE WITHOUT DUPLICATES
    # ------------------------------------------------------

    combined = []

    seen_questions = set()

    for doc in (
        similarity_docs +
        mmr_docs
    ):

        question = doc.metadata.get(
            "prompt_question",
            ""
        )

        if question not in seen_questions:

            seen_questions.add(
                question
            )

            combined.append(doc)

    return combined
def get_text_from_llm_response(response):
    if hasattr(response, "content"):
        return response.content

    if hasattr(response, "text"):
        return response.text

    return str(response)


def parse_llm_json(text):
    """
    Robustly extract and parse JSON returned by an LLM.
    Handles markdown fences and extra text surrounding JSON.
    """

    if text is None:
        raise ValueError("LLM returned an empty response.")

    text = str(text).strip()

    # ------------------------------------------------------
    # REMOVE MARKDOWN CODE FENCES
    # ------------------------------------------------------

    if "```json" in text:
        text = text.replace("```json", "")

    if "```" in text:
        text = text.replace("```", "")

    text = text.strip()

    # ------------------------------------------------------
    # FIND JSON OBJECT
    # ------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "LLM response does not contain a valid JSON object.\n\n"
            f"LLM response:\n{text}"
        )

    json_text = text[start:end + 1]

    # ------------------------------------------------------
    # FIRST ATTEMPT
    # ------------------------------------------------------

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as e:

        # --------------------------------------------------
        # SHOW THE EXACT PROBLEMATIC LOCATION
        # --------------------------------------------------

        error_position = e.pos

        start_context = max(
            0,
            error_position - 300
        )

        end_context = min(
            len(json_text),
            error_position + 300
        )

        problematic_text = json_text[
            start_context:end_context
        ]

        raise ValueError(
            "LLM returned malformed JSON.\n\n"
            f"JSON error: {e}\n\n"
            f"Problematic section:\n"
            f"{problematic_text}"
        ) from e
    
PROMPT_RETRIEVAL_PROMPT = """
You are an expert Requirements Elicitation Agent
specializing in individual sustainability, human values,
and software requirements engineering.

Your task is to identify the most relevant elicitation
questions for a given individual sustainability concern.

==================================================
CONCERN
==================================================

{concern}

==================================================
RETRIEVED PROMPT QUESTIONS
==================================================

{retrieved_questions}

==================================================
TASK
==================================================

STEP 1 — Understand the Concern

Understand the underlying individual sustainability
concern and identify what the system needs to address.

STEP 2 — Analyze Each Retrieved Question

For every retrieved prompt question:

- Determine the system quality property it addresses.
- Determine how directly it addresses the concern.
- Consider the associated SuSAF category.
- Consider the human abilities.
- Consider the NFR quality attributes.

STEP 3 — Assign Relevance

Use ONLY these relevance levels:

VERY HIGH
Directly mitigates the root cause of the concern.

HIGH
Addresses a key contributing factor.

MEDIUM
Indirectly or partially addresses the concern.

LOW
Weak or no meaningful connection.

Do NOT overestimate relevance.

Generic questions should not receive HIGH or VERY HIGH
unless they have a clear connection to the concern.

STEP 4 — Select Questions

Return the TOP 3 most relevant questions.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

{{
    "selected_questions": [
        {{
            "question": "...",
            "system_quality_property": "...",
            "relevance": "VERY HIGH",
            "reasoning": "...",
            "susaf_category": ["..."],
            "human_abilities": ["..."],
            "nfr_quality": ["..."]
        }}
    ]
}}
"""


def evaluate_retrieved_questions(
    concern,
    retrieved_docs,
    llm
):

    question_blocks = []

    for idx, doc in enumerate(
        retrieved_docs,
        start=1
    ):

        question_blocks.append(
            f"""
--- Retrieved Question {idx} ---

Prompt Question:
{doc.metadata.get(
    "prompt_question",
    ""
)}

SuSAF Category:
{doc.metadata.get(
    "susaf_category",
    []
)}

Human Abilities:
{doc.metadata.get(
    "human_abilities",
    []
)}

NFR Quality Attributes:
{doc.metadata.get(
    "nfr_quality",
    []
)}

Sub-Questions:
{doc.metadata.get(
    "sub_questions",
    []
)}

Example Scenario:
{doc.metadata.get(
    "example_scenario",
    ""
)}

Full Retrieval Text:
{doc.page_content}
"""
        )

    retrieved_text = "\n".join(
        question_blocks
    )

    prompt = PROMPT_RETRIEVAL_PROMPT.format(

        concern=concern,

        retrieved_questions=
            retrieved_text
    )

    response = llm.invoke(
        prompt
    )

    text = get_text_from_llm_response(
        response
    )

    return parse_llm_json(
        text
    )
# ==========================================================
# ISR PROMPT QUESTION VECTOR DATABASE
# ==========================================================

QUESTIONNAIRE_FILE = os.path.join(
    BASE_DIR,
    "Questionnaire.json"
)

ISR_VECTORSTORE_DIR = os.path.join(
    BASE_DIR,
    "chroma2_isr"
)


def create_prompt_question_text(entry):

    question = entry["Prompt_question"]
    metadata = entry["metadata"]

    categories = ", ".join(
        metadata["susaf_category"]
    )

    abilities = ", ".join(
        metadata["human_abilities"]
    )

    nfrs = ", ".join(
        metadata["nfr_quality"]
    )

    sub_questions = "; ".join(
        metadata["sub_questions"]
    )

    example_scenario = metadata[
        "example_scenario"
    ]

    text = (
        f"Prompt: {question}\n\n"
        f"This relates to {categories}.\n"
        f"It considers human abilities such as {abilities}.\n"
        f"Relevant quality attributes include {nfrs}.\n\n"
        f"Some sub prompting questions: "
        f"{sub_questions}\n\n"
        f"An example scenario: "
        f"{example_scenario}"
    )

    return text


def build_isr_vectorstore():

    if not os.path.exists(
        QUESTIONNAIRE_FILE
    ):

        raise FileNotFoundError(
            f"Questionnaire file not found: "
            f"{QUESTIONNAIRE_FILE}"
        )

    # ------------------------------------------------------
    # LOAD QUESTIONNAIRE
    # ------------------------------------------------------

    with open(
        QUESTIONNAIRE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    documents = []

    # ------------------------------------------------------
    # CREATE DOCUMENTS
    # ------------------------------------------------------

    for entry in data:

        text = create_prompt_question_text(
            entry
        )

        metadata = entry["metadata"]

        doc = Document(

            page_content=text,

            metadata={
                "prompt_question":
                    entry["Prompt_question"],

                "susaf_category":
                    metadata["susaf_category"],

                "human_abilities":
                    metadata["human_abilities"],

                "nfr_quality":
                    metadata["nfr_quality"],

                "sub_questions":
                    metadata["sub_questions"],

                "example_scenario":
                    metadata["example_scenario"],

                "type":
                    "elicitation_prompt"
            }
        )

        documents.append(doc)

    # ------------------------------------------------------
    # EMBEDDING MODEL
    # ------------------------------------------------------

    embeddings = HuggingFaceEmbeddings(

        model_name=
            "BAAI/bge-large-en",

        encode_kwargs={
            "prompt":
                "Represent the query for retrieval "
                "of prompting questions based on "
                "a given concern: "
        }
    )

    # ------------------------------------------------------
    # BUILD / REBUILD CHROMA
    # ------------------------------------------------------

    if os.path.exists(
        ISR_VECTORSTORE_DIR
    ):

        shutil.rmtree(
            ISR_VECTORSTORE_DIR
        )

    vectorstore = Chroma.from_documents(

        documents=documents,

        embedding=embeddings,

        persist_directory=
            ISR_VECTORSTORE_DIR
    )

    return vectorstore
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
# ISR GENERATION
# ==========================================================

ISR_GENERATION_PROMPT = """
You are an expert Sustainability Requirements Engineer
specializing in Individual Sustainability and Software
Requirements Engineering.

Your task is to derive Individual Sustainability
Requirements (ISRs) from an individual sustainability
concern and a relevant prompting question.

==========================================================
SYSTEM SCOPE
==========================================================

{system_scope}

==========================================================
SUSTAINABILITY KNOWLEDGE
==========================================================

{sustainability_knowledge}

==========================================================
INDIVIDUAL SUSTAINABILITY CONCERN
==========================================================

{concern}

==========================================================
SuSAF CATEGORY
==========================================================

{susaf_category}

==========================================================
TARGETED INDIVIDUALS / USER GROUPS
==========================================================

{targeted_individuals}

==========================================================
HUMAN VALUES
==========================================================

{human_values}

==========================================================
PROMPTING QUESTION
==========================================================

{prompt_question}

==========================================================
HUMAN ABILITIES
==========================================================

{human_abilities}

==========================================================
NFR QUALITY ATTRIBUTES
==========================================================

{nfr_quality}

==========================================================
TASK
==========================================================

Analyze the supplied information carefully.

The Individual Sustainability Concern represents a potential
negative impact, unmet need, or risk affecting individuals.

The Prompting Question represents a question intended to
elicit requirements that address that concern.

The Sustainability Knowledge provides the conceptual
knowledge that should ground the requirement.

The System Scope describes what the existing system does.

Based on these inputs:

1. Determine whether the current system scope already
   addresses the concern and prompting question.

2. Identify the gap between the existing system and the
   expected condition.

3. Derive one or more Individual Sustainability Requirements
   that address the identified gap.

4. Each ISR must:

   - Start with "The system shall..."
   - Be specific.
   - Be actionable.
   - Be testable or verifiable.
   - Be measurable where appropriate.
   - Address the individual sustainability concern.
   - Be relevant to the targeted individuals.
   - Preserve the relevant human value.
   - Be grounded in the supplied sustainability knowledge.
   - Be consistent with the system scope.
   - Consider the supplied NFR quality attributes.

5. Do not introduce functionality that has no relationship
   to the concern or prompting question.

6. Do not invent facts about the system that are not present
   in the supplied system scope.

7. If the existing system already satisfies the concern,
   explicitly identify this rather than unnecessarily
   generating a new requirement.

==========================================================
REQUIREMENT TYPE
==========================================================

For each requirement classify it as one of:

- "new"
- "already_satisfied"
- "partial"

==========================================================
OUTPUT
==========================================================

Return ONLY valid JSON.

{
    "requirements": [
        {
            "requirement_id": "ISR-1",

            "requirement":
                "The system shall ...",

            "requirement_type":
                "new",

            "human_values":
                ["..."],

            "nfr_quality_attributes":
                ["..."],

            "targeted_individuals":
                ["..."],

            "concern_addressed":
                "...",

            "prompting_question":
                "...",

            "system_scope_assessment":
                "...",

            "gap_identified":
                "...",

            "rationale":
                "...",

            "how_concern_is_mitigated":
                "..."
        }
    ]
}
"""


def generate_isrs_for_question(
    system_scope,
    sustainability_knowledge,
    concern,
    susaf_category,
    targeted_individuals,
    human_values,
    prompt_question,
    human_abilities,
    nfr_quality,
    llm
):

    prompt = ISR_GENERATION_PROMPT.format(

        system_scope=system_scope,

        sustainability_knowledge=
            sustainability_knowledge,

        concern=concern,

        susaf_category=
            susaf_category,

        targeted_individuals=
            targeted_individuals,

        human_values=
            human_values,

        prompt_question=
            prompt_question,

        human_abilities=
            human_abilities,

        nfr_quality=
            nfr_quality
    )

    response = llm.invoke(prompt)

    response_text = get_text_from_llm_response(
        response
    )

    result = parse_llm_json(
        response_text
    )

    return result
# ==========================================================
# ISR → FUNCTIONAL / NON-FUNCTIONAL REQUIREMENT
# DECOMPOSITION
# ==========================================================

ISR_DECOMPOSITION_PROMPT = """
You are an expert Software Requirements Engineer.

You are given an Individual Sustainability Requirement
(ISR).

Your task is to decompose the ISR into:

1. Functional Requirement(s) — FR
2. Non-Functional Requirement(s) — NFR

==========================================================
INDIVIDUAL SUSTAINABILITY REQUIREMENT
==========================================================

{isr}

==========================================================
ISR RATIONALE
==========================================================

{rationale}

==========================================================
TASK
==========================================================

Analyze the ISR carefully.

A Functional Requirement specifies WHAT the system should
do, provide, allow, prevent, calculate, display, store,
communicate, or otherwise perform.

A Non-Functional Requirement specifies a QUALITY, CONSTRAINT,
or CONDITION under which the functionality must operate.

Examples of NFR qualities include:

- Usability
- Accessibility
- Security
- Privacy
- Reliability
- Performance
- Transparency
- Explainability
- Safety
- Maintainability
- Availability
- Controllability

Rules:

1. Do not invent requirements that are not implied by the ISR.

2. Preserve the original meaning of the ISR.

3. An ISR may produce:
   - one FR and one NFR,
   - multiple FRs,
   - multiple NFRs,
   - or only an FR / only an NFR.

4. Do not force a requirement into both categories if it
   does not belong there.

5. Keep the FR and NFR independently understandable.

6. If a quality attribute is embedded within a functional
   statement, separate the functionality from the quality
   constraint where possible.

==========================================================
EXAMPLE
==========================================================

ISR:

"The system shall allow users to override automated
recommendations and shall provide a clear explanation
of each recommendation."

Functional Requirements:

- The system shall allow users to override automated
  recommendations.

Non-Functional Requirements:

- The system shall provide clear explanations for automated
  recommendations.

==========================================================
OUTPUT
==========================================================

Return ONLY valid JSON.

{
    "functional_requirements": [
        {
            "id": "FR-1",
            "requirement": "...",
            "source_isr": "..."
        }
    ],

    "non_functional_requirements": [
        {
            "id": "NFR-1",
            "requirement": "...",
            "quality_attribute": "...",
            "source_isr": "..."
        }
    ]
}
"""


def decompose_isr(
    isr,
    rationale,
    llm
):

    prompt = ISR_DECOMPOSITION_PROMPT.format(

        isr=isr,

        rationale=rationale
    )

    response = llm.invoke(
        prompt
    )

    response_text = get_text_from_llm_response(
        response
    )

    result = parse_llm_json(
        response_text
    )

    return result
# ==========================================================
# COMPLETE ISR PIPELINE
# ==========================================================

def produce_isr_pipeline(
    system_scope,
    sustainability_knowledge,
    accepted_concerns,
    llm,
    k=5,
    lambda_mult=0.5
):

    all_generated_isrs = []

    all_decompositions = []

    all_prompt_results = []

    # ======================================================
    # STEP 1
    # BUILD / LOAD VECTOR DATABASE
    # ======================================================

    vectorstore = build_isr_vectorstore()

    # ======================================================
    # STEP 2
    # PROCESS EACH ACCEPTED CONCERN
    # ======================================================

    for concern_index, concern_obj in enumerate(
        accepted_concerns,
        start=1
    ):

        # --------------------------------------------------
        # READ CONCERN DATA
        # --------------------------------------------------

        concern = concern_obj.get(
            "concern",
            ""
        )

        susaf_category = concern_obj.get(
            "category",
            []
        )

        targeted_individuals = concern_obj.get(
            "User Groups Affected (ordered from high to low)",
            []
        )

        human_values = concern_obj.get(
            "Human Values affected (ordered from high to low)",
            []
        )

        basis = concern_obj.get(
            "Basis",
            ""
        )

        # --------------------------------------------------
        # NORMALIZE VALUES
        # --------------------------------------------------

        if isinstance(
            susaf_category,
            str
        ):

            susaf_category_text = (
                susaf_category
            )

        else:

            susaf_category_text = ", ".join(
                susaf_category
            )

        if isinstance(
            targeted_individuals,
            str
        ):

            targeted_individuals_text = (
                targeted_individuals
            )

        else:

            targeted_individuals_text = ", ".join(
                targeted_individuals
            )

        if isinstance(
            human_values,
            str
        ):

            human_values_text = (
                human_values
            )

        else:

            human_values_text = ", ".join(
                human_values
            )

        # ==================================================
        # STEP 3
        # VECTOR RETRIEVAL
        # ==================================================

        retrieved_docs = retrieve_prompt_questions(

            vectorstore=
                vectorstore,

            concern=
                concern,

            k=
                k,

            lambda_mult=
                lambda_mult
        )

        if not retrieved_docs:

            continue

        # ==================================================
        # STEP 4
        # LLM EVALUATES RETRIEVED QUESTIONS
        # ==================================================

        evaluated = (
            evaluate_retrieved_questions(

                concern=
                    concern,

                retrieved_docs=
                    retrieved_docs,

                llm=
                    llm
            )
        )

        selected_questions = (
            evaluated.get(
                "selected_questions",
                []
            )
        )

        # Keep only maximum 3
        selected_questions = (
            selected_questions[:3]
        )

        # --------------------------------------------------
        # SAVE RETRIEVAL RESULTS
        # --------------------------------------------------

        all_prompt_results.append({

            "concern_id":
                concern_index,

            "concern":
                concern,

            "retrieved_questions":
                [
                    doc.metadata.get(
                        "prompt_question",
                        ""
                    )
                    for doc in retrieved_docs
                ],

            "selected_questions":
                selected_questions
        })

        # ==================================================
        # STEP 5
        # GENERATE ISR FOR SELECTED QUESTIONS
        # ==================================================

        for selected_index, selected in enumerate(
            selected_questions,
            start=1
        ):

            prompt_question = selected.get(
                "question",
                ""
            )

            if not prompt_question.strip():
                continue

            # --------------------------------------------------
            # FIND METADATA FOR SELECTED QUESTION
            # --------------------------------------------------

            matching_doc = None

            for doc in retrieved_docs:

                stored_question = doc.metadata.get(
                    "prompt_question",
                    ""
                )

                if (
                    stored_question.strip()
                    ==
                    prompt_question.strip()
                ):

                    matching_doc = doc

                    break

            # --------------------------------------------------
            # QUESTION METADATA
            # --------------------------------------------------

            if matching_doc:

                metadata = (
                    matching_doc.metadata
                )

            else:

                metadata = {}

            human_abilities = metadata.get(
                "human_abilities",
                []
            )

            nfr_quality = metadata.get(
                "nfr_quality",
                []
            )

            if isinstance(
                human_abilities,
                list
            ):

                human_abilities_text = (
                    ", ".join(
                        human_abilities
                    )
                )

            else:

                human_abilities_text = (
                    str(human_abilities)
                )

            if isinstance(
                nfr_quality,
                list
            ):

                nfr_quality_text = (
                    ", ".join(
                        nfr_quality
                    )
                )

            else:

                nfr_quality_text = (
                    str(nfr_quality)
                )

            # ==================================================
            # GENERATE ISR
            # ==================================================

            isr_result = (
                generate_isrs_for_question(

                    system_scope=
                        system_scope,

                    sustainability_knowledge=
                        sustainability_knowledge,

                    concern=
                        concern,

                    susaf_category=
                        susaf_category_text,

                    targeted_individuals=
                        targeted_individuals_text,

                    human_values=
                        human_values_text,

                    prompt_question=
                        prompt_question,

                    human_abilities=
                        human_abilities_text,

                    nfr_quality=
                        nfr_quality_text,

                    llm=
                        llm
                )
            )

            generated_requirements = (
                isr_result.get(
                    "requirements",
                    []
                )
            )

            # ==================================================
            # STEP 6
            # DECOMPOSE EACH ISR
            # ==================================================

            for requirement_index, requirement in enumerate(
                generated_requirements,
                start=1
            ):

                isr_text = requirement.get(
                    "requirement",
                    ""
                )

                if not isr_text.strip():
                    continue

                # ----------------------------------------------
                # CREATE UNIQUE ISR ID
                # ----------------------------------------------

                isr_id = (
                    f"ISR-{concern_index}-"
                    f"{selected_index}-"
                    f"{requirement_index}"
                )

                # ----------------------------------------------
                # DECOMPOSITION
                # ----------------------------------------------

                decomposition = (
                    decompose_isr(

                        isr=
                            isr_text,

                        rationale=
                            requirement.get(
                                "rationale",
                                ""
                            ),

                        llm=
                            llm
                    )
                )

                # ==================================================
                # STORE ISR
                # ==================================================

                isr_record = {

                    "requirement_id":
                        isr_id,

                    "concern_id":
                        concern_index,

                    "concern":
                        concern,

                    "susaf_category":
                        susaf_category,

                    "targeted_individuals":
                        targeted_individuals,

                    "human_values":
                        human_values,

                    "human_abilities":
                        human_abilities,

                    "prompt_question":
                        prompt_question,

                    "prompt_relevance":
                        selected.get(
                            "relevance",
                            ""
                        ),

                    "prompt_reasoning":
                        selected.get(
                            "reasoning",
                            ""
                        ),

                    "nfr_quality":
                        nfr_quality,

                    "basis":
                        basis,

                    "isr":
                        isr_text,

                    "requirement_type":
                        requirement.get(
                            "requirement_type",
                            ""
                        ),

                    "concern_addressed":
                        requirement.get(
                            "concern_addressed",
                            ""
                        ),

                    "system_scope_assessment":
                        requirement.get(
                            "system_scope_assessment",
                            ""
                        ),

                    "gap_identified":
                        requirement.get(
                            "gap_identified",
                            ""
                        ),

                    "rationale":
                        requirement.get(
                            "rationale",
                            ""
                        ),

                    "how_concern_is_mitigated":
                        requirement.get(
                            "how_concern_is_mitigated",
                            ""
                        )
                }

                all_generated_isrs.append(
                    isr_record
                )

                # ==================================================
                # STORE DECOMPOSITION
                # ==================================================

                all_decompositions.append({

                    "requirement_id":
                        isr_id,

                    "isr":
                        isr_text,

                    "functional_requirements":
                        decomposition.get(
                            "functional_requirements",
                            []
                        ),

                    "non_functional_requirements":
                        decomposition.get(
                            "non_functional_requirements",
                            []
                        )
                })

    # ======================================================
    # RETURN ALL RESULTS
    # ======================================================

    return (
        all_generated_isrs,
        all_decompositions,
        all_prompt_results
    )
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
                    "gemini-3.1-pro-preview",
                    "gemini-3.5-flash-lite",
                    "gemini-3.6-flash",
                    "gemini-3.7-flash",
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
    # PAGE LAYOUT
    # ======================================================

    left_panel, right_panel = st.columns([1, 1.5])

    # ======================================================
    # LEFT PANEL — SYSTEM SCOPE
    # ======================================================

    with left_panel:

        st.markdown("## System Scope")

        # --------------------------------------------------
        # LOAD SAVED SCOPE
        # --------------------------------------------------

        if "editable_scope" not in st.session_state:

            if os.path.exists("saved_scope.txt"):

                with open(
                    "saved_scope.txt",
                    "r",
                    encoding="utf-8"
                ) as f:

                    st.session_state.editable_scope = (
                        f.read()
                    )

            else:

                st.session_state.editable_scope = ""

        # --------------------------------------------------
        # EDITABLE SCOPE
        # --------------------------------------------------

        edited_scope = st.text_area(

            "Uploaded System Scope",

            key="editable_scope",

            height=700
        )

        # --------------------------------------------------
        # SAVE UPDATED SCOPE
        # --------------------------------------------------

        if st.button(
            "Save Updated Scope",
            key="save_scope_generate_concerns"
        ):

            try:

                with open(
                    "saved_scope.txt",
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(edited_scope)

                st.success(
                    "System scope updated locally."
                )

            except Exception as e:

                st.error(
                    f"Failed to save scope: {e}"
                )

    # ======================================================
    # RIGHT PANEL — CONCERN GENERATION
    # ======================================================

    with right_panel:

        # ==================================================
        # LOAD SUMMARY
        # ==================================================

        summary_text = ""

        if os.path.exists(SUMMARY_FILE):

            with open(
                SUMMARY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                summary_text = f.read()

        # ==================================================
        # PROVIDER
        # ==================================================

        provider = st.selectbox(

            "Select Provider",

            [
                "Google",
                "OpenAI"
            ]
        )

        # ==================================================
        # MODEL
        # ==================================================

        if provider == "Google":

            model_name = st.selectbox(

                "Select Gemini Model",

                [
                    "gemini-3.1-pro-preview",
                    "gemini-3.5-flash-lite",
                    "gemini-3.6-flash",
                    "gemini-3.7-flash",
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

        # ==================================================
        # API KEY
        # ==================================================

        api_key = st.text_input(

            "Enter API Key",

            type="password"
        )

        # ==================================================
        # ANALYST FEEDBACK
        # ==================================================

        analyst_feedback = st.text_area(

            "Analyst Opinion / Feedback",

            placeholder="""
Example:
- Focus more on cognitive overload.
- Include privacy-related concerns.
- Analyze vulnerable users separately.
- Add concerns regarding digital literacy.
""",

            height=150
        )

        # ==================================================
        # GENERATE BUTTON
        # ==================================================

        if st.button(
            "Generate Sustainability Concerns"
        ):

            if not api_key:

                st.error(
                    "Please provide API key."
                )

            else:

                try:

                    st.session_state.workflow_state[
                        "concerns"
                    ] = "active"

                    with st.spinner(
                        "Generating sustainability concerns..."
                    ):

                        generated_concerns = (
                            generate_individual_concerns(

                                summary=summary_text,

                                scope=edited_scope,

                                api_key=api_key,

                                provider=provider,

                                model_name=model_name,

                                analyst_opinion=analyst_feedback
                            )
                        )

                        st.session_state.generated_concerns = (
                            generated_concerns
                        )

                        # ----------------------------------
                        # RESET ACCEPTED CONCERNS
                        # ----------------------------------

                        st.session_state.accepted_concerns = []

                        st.session_state.workflow_state[
                            "concerns"
                        ] = "saved"

                        st.success(
                            "Concerns generated successfully."
                        )

                        st.rerun()

                except Exception as e:

                    st.session_state.workflow_state[
                        "concerns"
                    ] = "failed"

                    st.error(str(e))

        # ==================================================
        # DISPLAY GENERATED CONCERNS
        # ==================================================

        if "generated_concerns" in st.session_state:

            concerns_data = (
                st.session_state.generated_concerns
            )

            sustainability_concerns = (
                concerns_data[
                    "sustainability_concerns"
                ]
            )

            st.markdown("---")

            st.markdown(
                "## Generated Concerns"
            )

            # --------------------------------------------------
            # INITIALIZE ACCEPTED STORE
            # --------------------------------------------------

            if "accepted_concerns" not in st.session_state:

                st.session_state.accepted_concerns = []

            # --------------------------------------------------
            # CATEGORY LOOP
            # --------------------------------------------------

            for category, concerns in (
                sustainability_concerns.items()
            ):

                st.markdown(f"""
                <div class='content-card'>
                    <h3>
                        {category.replace("_", " ").title()}
                    </h3>
                </div>
                """, unsafe_allow_html=True)

                # ----------------------------------------------
                # CONCERN LOOP
                # ----------------------------------------------

                for idx, concern_obj in enumerate(concerns):

                    unique_id = (
                        f"{category}_{idx}"
                    )

                    with st.expander(
                        f"Concern {idx+1}"
                    ):

                        # --------------------------------------
                        # CONCERN
                        # --------------------------------------

                        st.text_area(

                            "Concern",

                            value=concern_obj[
                                "concern"
                            ],

                            key=f"concern_{unique_id}",

                            height=120,

                            disabled=False
                        )

                        # --------------------------------------
                        # IMPACT
                        # --------------------------------------

                        st.text_input(

                            "Impact",

                            value=concern_obj[
                                "impact"
                            ],

                            key=f"impact_{unique_id}"
                        )

                        # --------------------------------------
                        # HUMAN VALUES
                        # --------------------------------------

                        st.text_area(

                            "Human Values",

                            value="\n".join(
                                concern_obj[
                                    "Human Values affected (ordered from high to low)"
                                ]
                            ),

                            key=f"values_{unique_id}",

                            height=120
                        )

                        # --------------------------------------
                        # USER GROUPS
                        # --------------------------------------

                        st.text_area(

                            "User Groups Affected",

                            value=concern_obj[
                                "User Groups Affected (ordered from high to low)"
                            ],

                            key=f"users_{unique_id}",

                            height=120
                        )

                        # --------------------------------------
                        # BASIS
                        # --------------------------------------

                        st.text_area(

                            "Basis",

                            value=concern_obj[
                                "Basis"
                            ],

                            key=f"basis_{unique_id}",

                            height=180
                        )

                        # --------------------------------------
                        # STATUS
                        # --------------------------------------

                        current_status = concern_obj.get(
                            "status",
                            "pending"
                        )

                        status_color = {

                            "accepted": "#22c55e",

                            "rejected": "#ef4444",

                            "pending": "#facc15"

                        }.get(
                            current_status,
                            "#facc15"
                        )

                        st.markdown(f"""
                        <div style="
                            padding:8px;
                            border-radius:8px;
                            background:{status_color};
                            color:white;
                            font-weight:700;
                            text-align:center;
                            margin-bottom:10px;
                        ">
                            STATUS: {current_status.upper()}
                        </div>
                        """, unsafe_allow_html=True)

                        # --------------------------------------
                        # ACTION BUTTONS
                        # --------------------------------------

                        col1, col2 = st.columns(2)

                        # --------------------------------------
                        # ACCEPT
                        # --------------------------------------

                        with col1:

                            if st.button(
                                "✅ Accept",
                                key=f"accept_{unique_id}"
                            ):

                                concern_obj[
                                    "status"
                                ] = "accepted"

                                # ------------------------------
                                # STORE ACCEPTED CONCERN
                                # ------------------------------

                                if concern_obj not in (
                                    st.session_state.accepted_concerns
                                ):

                                    st.session_state.accepted_concerns.append(
                                        concern_obj
                                    )

                                st.success(
                                    "Concern accepted."
                                )

                                st.rerun()

                        # --------------------------------------
                        # REJECT
                        # --------------------------------------

                        with col2:

                            if st.button(
                                "❌ Reject",
                                key=f"reject_{unique_id}"
                            ):

                                concern_obj[
                                    "status"
                                ] = "rejected"

                                # ------------------------------
                                # REMOVE IF PREVIOUSLY ACCEPTED
                                # ------------------------------

                                st.session_state.accepted_concerns = [

                                    c

                                    for c in st.session_state.accepted_concerns

                                    if c["concern"] != concern_obj["concern"]
                                ]

                                st.warning(
                                    "Concern rejected."
                                )

                                st.rerun()

            # ==================================================
            # SAVE ACCEPTED CONCERNS
            # ==================================================

            st.markdown("---")

            if st.button(
                "Save Accepted Concerns"
            ):

                try:

                    accepted_output = {
                        "accepted_concerns":
                        st.session_state.accepted_concerns
                    }

                    # ------------------------------------------
                    # SAVE LOCALLY
                    # ------------------------------------------

                    with open(
                        "concern.txt",
                        "w",
                        encoding="utf-8"
                    ) as f:

                        json.dump(

                            accepted_output,

                            f,

                            indent=4,

                            ensure_ascii=False
                        )

                    # ------------------------------------------
                    # SAVE TO GITHUB
                    # ------------------------------------------

                    save_to_github(

                        file_content=json.dumps(
                            accepted_output,
                            indent=4,
                            ensure_ascii=False
                        ),

                        repo_name="MCompRETools/IndividualSR",

                        file_path="concern.txt",

                        github_token=st.secrets[
                            "GITHUB_TOKEN"
                        ],

                        commit_message=(
                            "Update accepted sustainability concerns"
                        )
                    )

                    st.success(
                        "Accepted concerns saved locally and to GitHub."
                    )

                except Exception as e:

                    st.error(
                        f"Failed to save concerns: {e}"
                    )
# ==========================================================
# PRODUCE ISR
# ==========================================================

elif selected_page == "Produce ISR":

    st.markdown("""
    <div class='content-card'>
        <h2>Produce Individual Sustainability Requirements</h2>
        <p>
        Retrieve relevant elicitation questions, generate
        Individual Sustainability Requirements, and decompose
        them into Functional and Non-Functional Requirements.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # INITIALIZE ISR SESSION STATE
    # ======================================================

    if "generated_isrs" not in st.session_state:

        st.session_state.generated_isrs = []

    if "isr_decompositions" not in st.session_state:

        st.session_state.isr_decompositions = []

    if "isr_prompt_results" not in st.session_state:

        st.session_state.isr_prompt_results = []

    # ======================================================
    # LOAD SYSTEM SCOPE
    # ======================================================

    system_scope = ""

    if os.path.exists("saved_scope.txt"):

        with open(
            "saved_scope.txt",
            "r",
            encoding="utf-8"
        ) as f:

            system_scope = f.read()

    elif "editable_scope" in st.session_state:

        system_scope = (
            st.session_state.editable_scope
        )

    # ======================================================
    # LOAD SUSTAINABILITY KNOWLEDGE
    # ======================================================

    sustainability_knowledge = ""

    if os.path.exists(SUMMARY_FILE):

        with open(
            SUMMARY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            sustainability_knowledge = f.read()

    # ======================================================
    # LOAD ACCEPTED CONCERNS
    # ======================================================

    accepted_concerns = []

    # ------------------------------------------------------
    # First preference: session state
    # ------------------------------------------------------

    if (
        "accepted_concerns"
        in st.session_state
        and st.session_state.accepted_concerns
    ):

        accepted_concerns = (
            st.session_state.accepted_concerns
        )

    # ------------------------------------------------------
    # Otherwise load concern.txt
    # ------------------------------------------------------

    elif os.path.exists("concern.txt"):

        try:

            with open(
                "concern.txt",
                "r",
                encoding="utf-8"
            ) as f:

                concern_data = json.load(f)

            accepted_concerns = concern_data.get(
                "accepted_concerns",
                []
            )

        except Exception as e:

            st.error(
                f"Unable to load concern.txt: {e}"
            )

    # ======================================================
    # INPUT VALIDATION
    # ======================================================

    if not system_scope.strip():

        st.warning(
            "System scope is not available. "
            "Please upload and save the system scope first."
        )

    if not sustainability_knowledge.strip():

        st.warning(
            "Sustainability knowledge summary is not available. "
            "Please generate or save the knowledge summary first."
        )

    if not accepted_concerns:

        st.warning(
            "No accepted sustainability concerns were found. "
            "Please accept concerns before producing ISRs."
        )

    # ======================================================
    # API / MODEL CONFIGURATION
    # ======================================================

    st.markdown("## LLM Configuration")

    config_col1, config_col2 = st.columns(2)

    with config_col1:

        isr_provider = st.selectbox(
            "Select Provider",
            [
                "Google",
                "OpenAI"
            ],
            key="isr_provider"
        )

    with config_col2:

        if isr_provider == "Google":

            isr_model = st.selectbox(
                "Select Gemini Model",
                [
                    "gemini-3.5-flash",
                    "gemini-2.5-flash",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash"
                ],
                key="isr_google_model"
            )

        else:

            isr_model = st.selectbox(
                "Select OpenAI Model",
                [
                    "gpt-4o",
                    "gpt-4.1-mini",
                    "gpt-4-turbo"
                ],
                key="isr_openai_model"
            )

    isr_api_key = st.text_input(
        "Enter API Key",
        type="password",
        key="isr_api_key"
    )

    # ======================================================
    # NUMBER OF RETRIEVED QUESTIONS
    # ======================================================

    retrieval_col1, retrieval_col2 = st.columns(2)

    with retrieval_col1:

        retrieved_k = st.number_input(
            "Number of prompt questions to retrieve",
            min_value=3,
            max_value=10,
            value=5,
            step=1
        )

    with retrieval_col2:

        st.info(
            "The LLM will evaluate the retrieved questions "
            "and retain the top 3 relevant questions for "
            "ISR generation."
        )

    # ======================================================
    # GENERATE BUTTON
    # ======================================================

    st.markdown("---")

    generate_col1, generate_col2 = st.columns(
        [1, 4]
    )

    with generate_col1:

        generate_isr_clicked = st.button(
            "⚙️ Generate ISR",
            key="generate_isr_button",
            use_container_width=True
        )

    # ======================================================
    # GENERATION PIPELINE
    # ======================================================

    if generate_isr_clicked:

        if not isr_api_key:

            st.error(
                "Please provide an API key."
            )

        elif not system_scope.strip():

            st.error(
                "System scope is missing."
            )

        elif not sustainability_knowledge.strip():

            st.error(
                "Sustainability knowledge summary is missing."
            )

        elif not accepted_concerns:

            st.error(
                "No accepted concerns are available."
            )

        else:

            try:

                st.session_state.workflow_state[
                    "isr"
                ] = "active"

                # --------------------------------------------------
                # CREATE LLM
                # --------------------------------------------------

                with st.spinner(
                    "Initializing selected LLM..."
                ):

                    if isr_provider == "Google":

                        llm = ChatGoogleGenerativeAI(
                            model=isr_model,
                            google_api_key=isr_api_key,
                            temperature=0
                        )

                    else:

                        llm = ChatOpenAI(
                            model=isr_model,
                            api_key=isr_api_key,
                            temperature=0
                        )

                # --------------------------------------------------
                # RUN PIPELINE
                # --------------------------------------------------

                with st.spinner(
                    "Retrieving prompt questions, "
                    "generating ISRs and decomposing them..."
                ):

                    (
                        generated_isrs,
                        decompositions,
                        prompt_results
                    ) = produce_isr_pipeline(

                        system_scope=
                            system_scope,

                        sustainability_knowledge=
                            sustainability_knowledge,

                        accepted_concerns=
                            accepted_concerns,

                        llm=
                            llm,

                        k=
                            retrieved_k,

                        lambda_mult=
                            0.5
                )
                # --------------------------------------------------
                # STORE RESULTS
                # --------------------------------------------------

                st.session_state.generated_isrs = (
                generated_isrs
                )

                st.session_state.isr_decompositions = (
                decompositions
                )

                st.session_state.isr_prompt_results = (
                prompt_results
                )

                st.session_state.workflow_state[
                    "isr"
                ] = "saved"

                # --------------------------------------------------
                # SAVE LOCAL JSON
                # --------------------------------------------------

                with open(
                    "generated_isrs.json",
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        generated_isrs,
                        f,
                        indent=4,
                        ensure_ascii=False
                    )

                with open(
                    "isr_decomposition.json",
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        decompositions,
                        f,
                        indent=4,
                        ensure_ascii=False
                    )

                st.success(
                    f"Generated {len(generated_isrs)} ISR(s) "
                    f"and decomposed {len(decompositions)} ISR(s)."
                )

                st.rerun()

            except Exception as e:

                st.session_state.workflow_state[
                    "isr"
                ] = "failed"

                st.error(
                    f"ISR generation failed: {e}"
                )

    # ======================================================
    # DISPLAY GENERATED ISR LIST
    # ======================================================

    if st.session_state.generated_isrs:

        st.markdown("---")

        st.markdown(
            "## Generated Individual Sustainability Requirements"
        )

        st.caption(
            "These requirements were generated from the "
            "accepted concern–prompt-question pairs."
        )

        for idx, isr_record in enumerate(
            st.session_state.generated_isrs,
            start=1
        ):

            with st.expander(
                f"ISR-{idx}: "
                f"{isr_record.get('isr', '')[:100]}..."
            ):

                st.markdown(
                    f"### ISR-{idx}"
                )

                st.markdown(
                    f"**Requirement**  \n"
                    f"{isr_record.get('isr', '')}"
                )

                st.markdown(
                    "**Concern**"
                )

                st.info(
                    isr_record.get(
                        "concern",
                        ""
                    )
                )

                st.markdown(
                    "**Prompt Question**"
                )

                st.write(
                    isr_record.get(
                        "prompt_question",
                        ""
                    )
                )

                st.markdown(
                    "**Prompt Relevance**"
                )

                st.write(
                    isr_record.get(
                        "prompt_relevance",
                        ""
                    )
                )

                st.markdown(
                    "**Targeted Individuals**"
                )

                st.write(
                    isr_record.get(
                        "targeted_individuals",
                        ""
                    )
                )

                st.markdown(
                    "**Supported NFR Properties**"
                )

                supported_nfrs = isr_record.get(
                    "supported_nfrs",
                    []
                )

                if isinstance(
                    supported_nfrs,
                    list
                ):

                    for nfr in supported_nfrs:

                        st.write(
                            f"• {nfr}"
                        )

                else:

                    st.write(
                        supported_nfrs
                    )

                st.markdown(
                    "**How the ISR mitigates the concern**"
                )

                st.write(
                    isr_record.get(
                        "mitigation",
                        ""
                    )
                )

                st.markdown(
                    "**Existing System Scope Assessment**"
                )

                st.write(
                    isr_record.get(
                        "existing_scope_score",
                        ""
                    )
                )

                st.markdown(
                    "**Requirement Type**"
                )

                st.write(
                    isr_record.get(
                        "requirement_type",
                        ""
                    )
                )
    # ======================================================
    # DISPLAY FR / NFR DECOMPOSITION
    # ======================================================

    if st.session_state.isr_decompositions:

        st.markdown("---")

        st.markdown(
            "## ISR Decomposition: FR and NFR"
        )

        st.caption(
            "Each generated ISR is decomposed into "
            "Functional Requirements (FRs) and "
            "Non-Functional Requirements (NFRs)."
        )

        for idx, decomposition in enumerate(
            st.session_state.isr_decompositions,
            start=1
        ):

            with st.expander(
                f"ISR-{idx} — FR / NFR Decomposition"
            ):

                st.markdown(
                    "### Individual Sustainability Requirement"
                )

                st.info(
                    decomposition.get(
                        "isr",
                        ""
                    )
                )

                col_fr, col_nfr = st.columns(2)

                # --------------------------------------------------
                # FR
                # --------------------------------------------------

                with col_fr:

                    st.markdown(
                        "### Functional Requirements"
                    )

                    frs = decomposition.get(
                        "functional_requirements",
                        []
                    )

                    if frs:

                        for fr_idx, fr in enumerate(
                            frs,
                            start=1
                        ):

                            st.markdown(
                                f"**FR-{idx}.{fr_idx}**"
                            )

                            st.success(
                                fr
                            )

                    else:

                        st.write(
                            "No functional requirement identified."
                        )

                # --------------------------------------------------
                # NFR
                # --------------------------------------------------

                with col_nfr:

                    st.markdown(
                        "### Non-Functional Requirements"
                    )

                    nfrs = decomposition.get(
                        "non_functional_requirements",
                        []
                    )

                    if nfrs:

                        for nfr_idx, nfr in enumerate(
                            nfrs,
                            start=1
                        ):

                            st.markdown(
                                f"**NFR-{idx}.{nfr_idx}**"
                            )

                            st.warning(
                                nfr
                            )

                    else:

                        st.write(
                            "No non-functional requirement identified."
                        )

    # ======================================================
    # SAVE ISR OUTPUT TO GITHUB
    # ======================================================

    if (
        st.session_state.generated_isrs
        and st.session_state.isr_decompositions
    ):

        st.markdown("---")

        if st.button(
            "💾 Save ISR Results to GitHub",
            key="save_isr_results"
        ):

            try:

                isr_content = json.dumps(
                    {
                        "generated_isrs":
                            st.session_state.generated_isrs,

                        "decompositions":
                            st.session_state.isr_decompositions
                    },
                    indent=4,
                    ensure_ascii=False
                )

                save_to_github(

                    file_content=isr_content,

                    repo_name=
                        "MCompRETools/IndividualSR",

                    file_path=
                        "generated_isrs.json",

                    github_token=
                        st.secrets[
                            "GITHUB_TOKEN"
                        ],

                    commit_message=
                        "Update generated ISRs"
                )

                st.success(
                    "ISR results saved to GitHub."
                )

            except Exception as e:

                st.error(
                    f"Failed to save ISR results: {e}"
                )
