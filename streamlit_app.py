# ==========================================================
# ISR GENERATION ASSISTANT DASHBOARD
# Streamlit UI similar to provided design
# ==========================================================

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
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background-color: #f5f7fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #03122e 0%, #021024 100%);
    color: white;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white;
}

/* Cards */
.metric-card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.06);
    border: 1px solid #e6e9f0;
}

.metric-title {
    color: #5d6785;
    font-size: 15px;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 40px;
    font-weight: 700;
    color: #0f172a;
}

/* Concern card */
.concern-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #dce3f0;
    margin-bottom: 14px;
    transition: 0.2s;
}

.concern-card:hover {
    border: 1px solid #2563eb;
    box-shadow: 0px 4px 14px rgba(37,99,235,0.15);
}

/* ISR cards */
.isr-card {
    background: #f8fffb;
    border: 1px solid #d8f0df;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 18px;
}

.tag {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    padding: 4px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-top: 5px;
    font-size: 13px;
}

.nfr-tag {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    padding: 4px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-top: 5px;
    font-size: 13px;
}

/* Header */
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #0f172a;
}

.sub-title {
    color: #64748b;
    margin-top: -10px;
    margin-bottom: 20px;
}

/* Search */
.search-box input {
    border-radius: 12px !important;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    border: none;
    background: #2563eb;
    color: white;
    font-weight: 600;
    padding: 10px 16px;
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

    st.markdown("## Navigation")

    st.markdown("🏠 Dashboard")
    st.markdown("📋 Concerns & ISRs")
    st.markdown("📄 System Scope")
    st.markdown("📚 Sustainability Knowledge")
    st.markdown("📊 Analytics")
    st.markdown("⚙️ Settings")

    st.markdown("---")

    st.markdown("## Upload Files")

    uploaded_csv = st.file_uploader(
        "Upload Concern CSV",
        type=["csv"]
    )

    uploaded_scope = st.file_uploader(
        "Upload System Scope",
        type=["txt"]
    )

    uploaded_summary = st.file_uploader(
        "Upload Sustainability Summary",
        type=["txt"]
    )

    st.markdown("---")

    st.markdown("## Actions")

    st.button("Generate ISRs")

    st.button("Export JSON")

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="main-title">
Concerns to ISR Generation
</div>

<div class="sub-title">
Transform sustainability concerns into actionable Individual Sustainability Requirements
</div>
""", unsafe_allow_html=True)

# ==========================================================
# SAMPLE DATA
# ==========================================================

sample_data = [
    {
        "Concern":
        "Cognitive overload and increased stress for healthcare professionals from managing large patient datasets.",
        "Values":
        ["Health", "Achievement", "Benevolence"],
        "NFRs":
        ["Usability", "User Control", "Efficiency"],
        "ISR":
        "The system shall provide configurable display modes allowing healthcare professionals to filter and prioritize patient information based on urgency.",
        "Reasoning":
        "Reducing information overload minimizes stress and improves decision-making efficiency."
    },

    {
        "Concern":
        "Over-reliance on AI leading to deskilling of healthcare professionals.",
        "Values":
        ["Achievement", "Autonomy"],
        "NFRs":
        ["Transparency", "Reliability"],
        "ISR":
        "The system shall require human validation for AI-generated clinical recommendations in high-risk scenarios.",
        "Reasoning":
        "Human review prevents blind trust in AI outputs and preserves professional judgment."
    }
]

# ==========================================================
# METRICS
# ==========================================================

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Total Concerns</div>
        <div class="metric-value">12</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Total Questions</div>
        <div class="metric-value">24</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">NFR Categories</div>
        <div class="metric-value">6</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Generated ISRs</div>
        <div class="metric-value">21</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# FILTERS
# ==========================================================

f1, f2, f3 = st.columns([2,1,1])

with f1:
    search = st.text_input(
        "Search concerns..."
    )

with f2:
    st.selectbox(
        "Filter by NFR",
        ["All", "Usability", "Safety", "Reliability"]
    )

with f3:
    st.selectbox(
        "Filter by Human Value",
        ["All", "Health", "Autonomy", "Achievement"]
    )

# ==========================================================
# MAIN PANELS
# ==========================================================

left, right = st.columns([1.1, 1.9])

# ==========================================================
# LEFT PANEL - CONCERNS
# ==========================================================

with left:

    st.markdown("## Concerns List")

    for idx, item in enumerate(sample_data):

        st.markdown(f"""
        <div class="concern-card">

        <h4>{idx+1}. {item['Concern']}</h4>

        <div style="margin-top:10px;">
        {" ".join([f'<span class="tag">{v}</span>' for v in item['Values']])}
        </div>

        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# RIGHT PANEL - GENERATED ISR
# ==========================================================

with right:

    st.markdown("## Generated ISRs")

    for idx, item in enumerate(sample_data):

        st.markdown(f"""
        <div class="isr-card">

        <h4>ISR-{idx+1}</h4>

        <p style="font-size:16px;">
        {item['ISR']}
        </p>

        <hr>

        <b>Targeted Human Values</b><br>
        {" ".join([f'<span class="tag">{v}</span>' for v in item['Values']])}

        <br><br>

        <b>Supported NFRs</b><br>
        {" ".join([f'<span class="nfr-tag">{n}</span>' for n in item['NFRs']])}

        <br><br>

        <b>Reasoning</b><br>
        <p>
        {item['Reasoning']}
        </p>

        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.markdown("""
<center>
ISR Generation Assistant • Individual Sustainability Requirements Framework
</center>
""", unsafe_allow_html=True)
