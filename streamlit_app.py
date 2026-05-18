# ==========================================================
# MODERN SIDEBAR UI DESIGN
# Similar to provided screenshot
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

.stApp {
    background-color: #f5f7fb;
    font-family: 'Inter', sans-serif;
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

/* Remove default padding */
section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white;
}

/* =====================================================
LOGO AREA
===================================================== */

.sidebar-logo {

    display: flex;
    align-items: center;

    gap: 14px;

    margin-bottom: 30px;
}

.logo-circle {

    width: 46px;
    height: 46px;

    border-radius: 50%;

    background: white;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #03122e;

    font-size: 22px;
    font-weight: bold;
}

.logo-title {

    font-size: 28px;
    font-weight: 700;

    line-height: 1.2;
}

.logo-subtitle {

    font-size: 14px;
    color: #c6d0e1;
}

/* =====================================================
NAVIGATION
===================================================== */

.nav-section-title {

    color: #9caecf;

    font-size: 12px;

    letter-spacing: 1px;

    margin-top: 10px;
    margin-bottom: 14px;

    text-transform: uppercase;
}

.nav-item {

    display: flex;

    align-items: center;

    gap: 14px;

    padding: 14px 16px;

    border-radius: 14px;

    margin-bottom: 8px;

    cursor: pointer;

    transition: 0.2s;
}

/* Hover */
.nav-item:hover {

    background: rgba(255,255,255,0.08);
}

/* Active */
.nav-active {

    background: linear-gradient(
        90deg,
        #2563eb 0%,
        #1d4ed8 100%
    );

    box-shadow:
        0px 4px 14px rgba(37,99,235,0.35);
}

/* Icon */
.nav-icon {

    font-size: 20px;
}

/* Text */
.nav-text {

    font-size: 16px;
    font-weight: 500;
}

/* =====================================================
BOTTOM METRIC CARD
===================================================== */

.sidebar-card {

    margin-top: 40px;

    background: rgba(255,255,255,0.05);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 22px;
}

.metric-title {

    color: #c6d0e1;

    font-size: 14px;
}

.metric-value {

    font-size: 42px;

    font-weight: 700;

    margin-top: 8px;

    margin-bottom: 18px;
}

.divider {

    border-top: 1px solid rgba(255,255,255,0.12);

    margin-top: 16px;
    margin-bottom: 16px;
}

/* =====================================================
HEADER BUTTONS
===================================================== */

.top-btn {

    border: 1px solid #dce3f0;

    border-radius: 12px;

    padding: 10px 18px;

    background: white;

    font-weight: 500;
}

/* =====================================================
CARDS
===================================================== */

.main-card {

    background: white;

    border-radius: 18px;

    padding: 22px;

    border: 1px solid #e6e9f0;

    box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
}

/* =====================================================
TITLES
===================================================== */

.page-title {

    font-size: 42px;

    font-weight: 800;

    color: #0f172a;
}

.page-subtitle {

    color: #64748b;

    font-size: 16px;

    margin-top: -10px;
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
    # NAVIGATION
    # ------------------------------------------------------

    st.markdown("""
    <div class="nav-section-title">
    Navigation
    </div>
    """, unsafe_allow_html=True)

    # ACTIVE ITEM

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

    # OTHER ITEMS

    nav_items = [

        ("📋", "Concerns & ISRs"),
        ("📄", "System Scope"),
        ("📚", "Sustainability Knowledge"),
        ("📊", "Analytics"),
        ("🗂️", "Export History"),
        ("⚙️", "Settings"),
        ("ℹ️", "About")
    ]

    for icon, text in nav_items:

        st.markdown(f"""
        <div class="nav-item">

            <div class="nav-icon">
            {icon}
            </div>

            <div class="nav-text">
            {text}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # BOTTOM CARD
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
# MAIN PAGE
# ==========================================================

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------

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

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("⬇ Export JSON")

    with c2:
        st.button("⬇ Export CSV")

    with c3:
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

            <div style="
                font-size:38px;
                margin-bottom:12px;
            ">
            {icon}
            </div>

            <div style="
                color:#64748b;
                font-size:14px;
            ">
            {title}
            </div>

            <div style="
                font-size:42px;
                font-weight:700;
                margin-top:10px;
            ">
            {value}
            </div>

        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# SAMPLE CONTENT
# ==========================================================

left_panel, right_panel = st.columns([1.2, 2])

with left_panel:

    st.markdown("""
    <div class="main-card">

        <h3>
        Concerns List
        </h3>

        <hr>

        <h4>
        1. Cognitive overload and increased stress...
        </h4>

        <p>
        Health, Achievement, Benevolence
        </p>

        <hr>

        <h4>
        2. Privacy risks and loss of trust...
        </h4>

        <p>
        Security, Privacy, Trust
        </p>

    </div>
    """, unsafe_allow_html=True)

with right_panel:

    st.markdown("""
    <div class="main-card">

        <h2>
        Generated ISRs
        </h2>

        <hr>

        <h4>
        ISR-1
        </h4>

        <p>
        The system shall provide configurable display modes
        that allow healthcare professionals to filter and
        prioritize patient information.
        </p>

        <hr>

        <h4>
        ISR-2
        </h4>

        <p>
        The system shall provide adaptive summarization
        mechanisms to reduce cognitive overload.
        </p>

    </div>
    """, unsafe_allow_html=True)
