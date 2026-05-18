# ==========================================================
# ISR GENERATION ASSISTANT
# FULL FIXED MODERN UI
# ==========================================================

import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ISR Generation Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* =====================================================
GLOBAL
===================================================== */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #f5f7fb;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #03122e 0%,
        #021024 100%
    );

    width: 270px !important;
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* =====================================================
LOGO
===================================================== */

.sidebar-logo {

    display: flex;

    align-items: center;

    gap: 14px;

    margin-bottom: 28px;
}

.logo-circle {

    width: 46px;
    height: 46px;

    border-radius: 50%;

    background: white;

    display: flex;

    align-items: center;
    justify-content: center;

    font-size: 24px;
}

.logo-title {

    font-size: 24px;

    font-weight: 700;
}

.logo-subtitle {

    color: #b6c2d9;

    font-size: 14px;
}

/* =====================================================
NAVIGATION
===================================================== */

.nav-section {

    margin-top: 20px;

    margin-bottom: 12px;

    color: #9ba8c4;

    font-size: 12px;

    letter-spacing: 1px;

    text-transform: uppercase;
}

.nav-item {

    display: flex;

    align-items: center;

    gap: 12px;

    padding: 14px 16px;

    border-radius: 14px;

    margin-bottom: 10px;

    transition: 0.2s;
}

.nav-item:hover {

    background: rgba(255,255,255,0.08);
}

.nav-active {

    background: linear-gradient(
        90deg,
        #2563eb 0%,
        #1d4ed8 100%
    );

    box-shadow:
        0px 4px 14px rgba(37,99,235,0.35);
}

.nav-icon {

    font-size: 20px;
}

.nav-text {

    font-size: 16px;

    font-weight: 500;
}

/* =====================================================
BOTTOM CARD
===================================================== */

.sidebar-card {

    margin-top: 40px;

    background: rgba(255,255,255,0.05);

    border-radius: 18px;

    padding: 22px;

    border: 1px solid rgba(255,255,255,0.08);
}

.metric-title {

    color: #c8d3ea;

    font-size: 14px;
}

.metric-value {

    font-size: 40px;

    font-weight: 700;

    margin-top: 6px;

    margin-bottom: 16px;
}

.divider {

    border-top: 1px solid rgba(255,255,255,0.1);

    margin-top: 16px;

    margin-bottom: 16px;
}

/* =====================================================
PAGE TITLES
===================================================== */

.page-title {

    font-size: 42px;

    font-weight: 800;

    color: #0f172a;
}

.page-subtitle {

    color: #64748b;

    margin-top: -10px;

    font-size: 16px;
}

/* =====================================================
CARDS
===================================================== */

.main-card {

    background: white;

    border-radius: 18px;

    padding: 22px;

    border: 1px solid #e4e9f2;

    box-shadow:
        0px 2px 8px rgba(0,0,0,0.04);
}

/* =====================================================
METRICS
===================================================== */

.metric-icon {

    font-size: 38px;

    margin-bottom: 12px;
}

.metric-heading {

    color: #64748b;

    font-size: 14px;
}

.metric-number {

    font-size: 42px;

    font-weight: 700;

    margin-top: 10px;
}

/* =====================================================
BUTTONS
===================================================== */

.stButton > button {

    border-radius: 12px;

    padding: 10px 16px;

    border: 1px solid #dce3f0;

    background: white;

    font-weight: 500;
}

/* =====================================================
CONCERN ITEMS
===================================================== */

.concern-item {

    padding: 18px;

    border-radius: 14px;

    border: 1px solid #e4e9f2;

    margin-bottom: 12px;
}

.concern-item:hover {

    border: 1px solid #2563eb;
}

/* =====================================================
ISR BLOCKS
===================================================== */

.isr-block {

    background: #f8fffb;

    border: 1px solid #d7f0df;

    padding: 20px;

    border-radius: 14px;

    margin-bottom: 18px;
}

.tag {

    display: inline-block;

    background: #dcfce7;

    color: #166534;

    padding: 5px 10px;

    border-radius: 20px;

    margin-right: 6px;

    margin-top: 6px;

    font-size: 13px;
}

.nfr-tag {

    display: inline-block;

    background: #dbeafe;

    color: #1d4ed8;

    padding: 5px 10px;

    border-radius: 20px;

    margin-right: 6px;

    margin-top: 6px;

    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    # ------------------------------------------------------
    # LOGO
    # ------------------------------------------------------

    st.markdown("""
    <div class="sidebar-logo">

        <div class="logo-circle">
        🧠
        </div>

        <div>

            <div class="logo-title">
            ISR Generation Assistant
            </div>

            <div class="logo-subtitle">
            Individual Sustainability Requirements
            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # NAVIGATION TITLE
    # ------------------------------------------------------

    st.markdown("""
    <div class="nav-section">
    Navigation
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # ACTIVE NAV ITEM
    # ------------------------------------------------------

    st.markdown("""
    <div class="nav-item nav-active">

        <div class="nav-icon">
        🏠
        </div>

        <div class="nav-text">
        Dashboard
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # OTHER ITEMS
    # ------------------------------------------------------

    nav_items = [

        ("📋", "Concerns & ISRs"),
        ("📄", "System Scope"),
        ("📚", "Sustainability Knowledge"),
        ("📊", "Analytics"),
        ("🗂️", "Export History"),
        ("⚙️", "Settings"),
        ("ℹ️", "About")
    ]

    for icon, label in nav_items:

        st.markdown(f"""
        <div class="nav-item">

            <div class="nav-icon">
            {icon}
            </div>

            <div class="nav-text">
            {label}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # SIDEBAR METRIC CARD
    # ------------------------------------------------------

    st.markdown("""
    <div class="sidebar-card">

        <div class="metric-title">
        Total Processed
        </div>

        <div class="metric-value">
        12
        </div>

        <div class="divider"></div>

        <div class="metric-title">
        Generated ISRs
        </div>

        <div class="metric-value">
        21
        </div>

    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

left, right = st.columns([4,2])

with left:

    st.markdown("""
    <div class="page-title">
    Concerns to ISR Generation
    </div>

    <div class="page-subtitle">
    Transform sustainability concerns into actionable Individual Sustainability Requirements
    </div>
    """, unsafe_allow_html=True)

with right:

    b1, b2, b3 = st.columns(3)

    with b1:
        st.button("⬇ Export JSON")

    with b2:
        st.button("⬇ Export CSV")

    with b3:
        st.button("🌙")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# METRIC CARDS
# ==========================================================

m1, m2, m3, m4 = st.columns(4)

metrics = [

    ("🟣", "Total Concerns", "12"),
    ("🔵", "Total Questions", "24"),
    ("🟢", "NFR Categories", "6"),
    ("🟠", "ISRs Generated", "21")
]

for col, metric in zip([m1,m2,m3,m4], metrics):

    icon, title, value = metric

    with col:

        st.markdown(f"""
        <div class="main-card">

            <div class="metric-icon">
            {icon}
            </div>

            <div class="metric-heading">
            {title}
            </div>

            <div class="metric-number">
            {value}
            </div>

        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# MAIN CONTENT
# ==========================================================

left_panel, right_panel = st.columns([1.2, 2])

# ==========================================================
# CONCERNS PANEL
# ==========================================================

with left_panel:

    st.markdown("""
    <div class="main-card">

        <h3>
        Concerns List
        </h3>

        <hr>

        <div class="concern-item">

            <h4>
            1. Cognitive overload and increased stress...
            </h4>

            <p>
            Health, Achievement, Benevolence
            </p>

        </div>

        <div class="concern-item">

            <h4>
            2. Privacy risks and loss of trust...
            </h4>

            <p>
            Security, Privacy, Trust
            </p>

        </div>

    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# ISR PANEL
# ==========================================================

with right_panel:

    st.markdown("""
    <div class="main-card">

        <h2>
        Generated ISRs
        </h2>

        <hr>

        <div class="isr-block">

            <h4>
            ISR-1
            </h4>

            <p>
            The system shall provide configurable display
            modes allowing healthcare professionals to
            filter and prioritize patient information.
            </p>

            <br>

            <b>Targeted Human Values</b>

            <br>

            <span class="tag">Health</span>
            <span class="tag">Achievement</span>
            <span class="tag">Benevolence</span>

            <br><br>

            <b>Supported NFRs</b>

            <br>

            <span class="nfr-tag">Usability</span>
            <span class="nfr-tag">Efficiency</span>
            <span class="nfr-tag">User Control</span>

            <br><br>

            <b>Reasoning</b>

            <p>
            Reducing information overload minimizes stress
            and improves decision-making efficiency.
            </p>

        </div>

        <div class="isr-block">

            <h4>
            ISR-2
            </h4>

            <p>
            The system shall provide adaptive
            summarization mechanisms to reduce
            cognitive overload.
            </p>

            <br>

            <b>Targeted Human Values</b>

            <br>

            <span class="tag">Health</span>
            <span class="tag">Achievement</span>

            <br><br>

            <b>Supported NFRs</b>

            <br>

            <span class="nfr-tag">Usability</span>
            <span class="nfr-tag">Reliability</span>

            <br><br>

            <b>Reasoning</b>

            <p>
            Adaptive summarization surfaces only
            relevant insights and reduces stress.
            </p>

        </div>

    </div>
    """, unsafe_allow_html=True)
