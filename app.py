import streamlit as st
from backend.ui import (
    dashboard_page, symptom_page, doctors_page, ai_page, fitness_page,
)

st.set_page_config(
    page_title="CareBuddy AI | Health & Wellness",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #f7f6ff;
    --card-bg: #ffffff;
    --card-border: #e6e3f2;
    --text-main: #20243a;
    --text-muted: #73788c;
    --accent-teal: #168f87;
    --accent-lime: #d2fa7a;
    --accent-glow: rgba(133, 91, 245, 0.13);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at 82% 0%, rgba(203, 185, 255, .23), transparent 31%), linear-gradient(135deg, #fbfaff 0%, #f1f3fb 56%, #f6f2fc 100%);
    color: var(--text-main);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f7f5ff 100%);
    border-right: 1px solid #e9e6f2;
}
[data-testid="stSidebar"] * {
    color: #30334a !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #85879a !important;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-main) !important;
    letter-spacing: -.02em;
    font-weight: 700;
}

[data-testid="stMetric"] {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    padding: 18px 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(15, 29, 45, 0.04);
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: var(--text-main) !important;
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stFormSubmitButton"] button, .stButton>button, .stDownloadButton>button {
    border-radius: 10px;
    border: 0;
    font-weight: 700;
    background: linear-gradient(120deg, #7457e8 0%, #8f4de5 55%, #aa52ca 100%) !important;
    color: #fff !important;
    padding: .6rem 1.2rem;
    box-shadow: 0 5px 15px rgba(125, 82, 220, 0.23);
    transition: all 0.2s ease;
}
[data-testid="stFormSubmitButton"] button:hover, .stButton>button:hover, .stDownloadButton>button:hover {
    background: linear-gradient(120deg, #6243d7 0%, #7740cf 55%, #9041b5 100%) !important;
    box-shadow: 0 7px 20px rgba(125, 82, 220, 0.33);
}

[data-testid="stForm"] {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 8px 30px rgba(15, 29, 45, 0.05);
}

[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] > div {
    background-color: #f8fafc !important;
    color: #0f1d2d !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid var(--card-border);
}

.hg-hero {
    background: radial-gradient(circle at 88% 15%, rgba(215,198,255,.38), transparent 20%), linear-gradient(115deg, #3156d9 0%, #6849df 56%, #9c37dc 100%);
    color: white;
    border-radius: 24px;
    padding: 34px 38px;
    margin: 0 0 24px;
    box-shadow: 0 18px 45px rgba(74, 61, 154, 0.18);
    position: relative;
    overflow: hidden;
}
.hg-hero-fitness {
    background: radial-gradient(circle at 88% 12%, rgba(255, 185, 115, .30), transparent 19%), linear-gradient(118deg, #101b35 0%, #263766 48%, #087f78 100%);
}
.hg-hero-fitness .hg-eyebrow { color: #d8ff72; }
.hg-hero h1 {
    color: white !important;
    margin: 0 0 8px 0;
    font-size: 2.1rem;
}
.hg-hero p {
    color: #ccfbf1;
    margin: 0;
    font-size: 1.02rem;
}
.hg-eyebrow {
    color: #e2ff86;
    text-transform: uppercase;
    letter-spacing: .15em;
    font-size: .72rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.hg-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 20px;
    height: auto;
    box-shadow: 0 8px 26px rgba(15, 29, 45, 0.055);
    transition: transform .18s ease, box-shadow .18s ease;
}
.hg-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 32px rgba(15, 29, 45, 0.09);
}
.hg-card h3 {
    margin: 0 0 7px;
    font-size: 1.08rem;
    color: #0f1d2d;
}
.hg-card p {
    color: var(--text-muted);
    margin: 0;
    font-size: .92rem;
    line-height: 1.55;
}

.hg-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 99px;
    background: #f0eaff;
    color: #6844c4;
    font-size: .74rem;
    font-weight: 700;
    margin-bottom: 12px;
    border: 1px solid #ded2ff;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px;
    padding: 4px 8px;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(127, 92, 220, .08);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(119, 87, 226, .16), rgba(154, 93, 225, .04));
    box-shadow: inset 3px 0 #805be7;
}
[data-testid="stMetric"]:nth-child(1) { background: linear-gradient(145deg, #fff7f0, #ffffff); }
[data-testid="stMetric"]:nth-child(2) { background: linear-gradient(145deg, #f5fff0, #ffffff); }
[data-testid="stMetric"]:nth-child(3) { background: linear-gradient(145deg, #f0faff, #ffffff); }
[data-testid="stMetric"]:nth-child(4) { background: linear-gradient(145deg, #f8f1ff, #ffffff); }
[data-testid="stCheckbox"] label { color: #30334a !important; }
[data-testid="stCheckbox"] input:checked + div { background: #805be7 !important; border-color: #805be7 !important; }
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    border-color: #e1deee !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] { background: rgba(255,255,255,.82); }
.hg-pill { background: #f0eaff; border-color: #ded2ff; color: #6844c4; }
.hg-card { border-color: #e7e3f1; }
.hg-card:nth-child(4n+1) { background: linear-gradient(145deg, #fffaf6, #ffffff); }
.hg-card:nth-child(4n+2) { background: linear-gradient(145deg, #f8fff5, #ffffff); }
.hg-card:nth-child(4n+3) { background: linear-gradient(145deg, #f3faff, #ffffff); }
.hg-card:nth-child(4n) { background: linear-gradient(145deg, #faf5ff, #ffffff); }
[data-testid="stForm"] { border-color: #e5e1f0; }
.hg-section-label { color: #7656d9; font-size: .78rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
.hg-soft-panel { background: linear-gradient(135deg,#f7f3ff,#f1f8ff); border: 1px solid #e6e0f4; border-radius: 18px; padding: 20px 22px; }
.hg-soft-panel h3 { margin-top: 0; }
.hg-risk-signal { display: flex; align-items: center; gap: 12px; border-radius: 14px; padding: 13px 15px; border: 1px solid; margin: 12px 0; }
.hg-risk-signal small { display: block; font-size: .63rem; font-weight: 800; letter-spacing: .12em; opacity: .78; }
.hg-risk-signal strong { display: block; font-size: 1.22rem; line-height: 1.25; text-transform: uppercase; }
.hg-signal-dot { width: 15px; height: 15px; border-radius: 50%; flex: 0 0 15px; box-shadow: 0 0 0 5px rgba(255,255,255,.55); }
.hg-risk-green { color: #176b3c; background: #eaf8ee; border-color: #b9e6c6; }
.hg-risk-green .hg-signal-dot { background: #20a95b; }
.hg-risk-yellow { color: #80580b; background: #fff6d9; border-color: #f1dc91; }
.hg-risk-yellow .hg-signal-dot { background: #e7ad18; }
.hg-risk-red { color: #a52d35; background: #ffeded; border-color: #f3b6ba; }
.hg-risk-red .hg-signal-dot { background: #e2424c; }
.hg-risk-copy { font-size: .91rem; line-height: 1.55; }
[data-testid="stPlotlyChart"] { background: rgba(255,255,255,.75); border: 1px solid #e8e4f1; border-radius: 18px; padding: 8px; }
[data-testid="stExpander"] summary:hover { color: #7150d4; }

/* Dark fitness dashboard: scoped to the page marker rendered by fitness_page(). */
.stApp:has(.hg-fitness-page) {
    background: radial-gradient(ellipse at 78% 7%, rgba(133, 43, 58, .22), transparent 28%), linear-gradient(145deg, #100c0e 0%, #171113 52%, #211316 100%);
    color: #f4edef;
}
.stApp:has(.hg-fitness-page) h1,
.stApp:has(.hg-fitness-page) h2,
.stApp:has(.hg-fitness-page) h3,
.stApp:has(.hg-fitness-page) [data-testid="stMarkdownContainer"] p,
.stApp:has(.hg-fitness-page) label { color: #f3eaec !important; }
.stApp:has(.hg-fitness-page) h2,
.stApp:has(.hg-fitness-page) h3 { letter-spacing: -.025em; }
.stApp:has(.hg-fitness-page) [data-testid="stCaptionContainer"] p { color: #b7a9ad !important; }
.stApp:has(.hg-fitness-page) [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #120d0f 0%, #1e1215 100%);
    border-right-color: #352126;
}
.stApp:has(.hg-fitness-page) [data-testid="stSidebar"] * { color: #f5edef !important; }
.stApp:has(.hg-fitness-page) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b7a9ad !important; }
.stApp:has(.hg-fitness-page) [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(237, 83, 91, .25), rgba(237, 83, 91, .04));
    box-shadow: inset 3px 0 #f26b70;
}
.stApp:has(.hg-fitness-page) .hg-hero-fitness {
    background: radial-gradient(circle at 82% 12%, rgba(255, 194, 122, .32), transparent 19%), linear-gradient(112deg, #31171c 0%, #762b35 53%, #da594c 100%);
    border: 1px solid rgba(255,255,255,.09);
    box-shadow: 0 18px 46px rgba(0,0,0,.28);
}
.stApp:has(.hg-fitness-page) .hg-hero h1 { color: #fff8f6 !important; }
.stApp:has(.hg-fitness-page) .hg-hero p { color: #ffe2dc !important; }
.stApp:has(.hg-fitness-page) .hg-eyebrow { color: #ffd18a; }
.stApp:has(.hg-fitness-page) [data-testid="stForm"] {
    background: #1c1518;
    border: 1px solid #3b292e;
    box-shadow: 0 12px 36px rgba(0,0,0,.2);
}
.stApp:has(.hg-fitness-page) [data-testid="stMetric"] {
    background: linear-gradient(145deg, #24191d, #1a1416);
    border-color: #3b292e;
    box-shadow: 0 9px 25px rgba(0,0,0,.18);
}
.stApp:has(.hg-fitness-page) [data-testid="stMetricLabel"] { color: #c6b6ba !important; }
.stApp:has(.hg-fitness-page) [data-testid="stMetricValue"] { color: #fff4f0 !important; }
.stApp:has(.hg-fitness-page) [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
.stApp:has(.hg-fitness-page) [data-testid="stTextInput"] input,
.stApp:has(.hg-fitness-page) [data-testid="stTextArea"] textarea,
.stApp:has(.hg-fitness-page) [data-testid="stNumberInput"] input {
    background: #261c20 !important;
    color: #fff4f0 !important;
    border-color: #493238 !important;
}
.stApp:has(.hg-fitness-page) [data-testid="stFormSubmitButton"] button,
.stApp:has(.hg-fitness-page) .stButton > button {
    background: linear-gradient(115deg, #f26b70, #e84e55 58%, #fa875e) !important;
    box-shadow: 0 6px 19px rgba(233, 74, 82, .24);
}
.stApp:has(.hg-fitness-page) [data-testid="stFormSubmitButton"] button:hover,
.stApp:has(.hg-fitness-page) .stButton > button:hover { background: linear-gradient(115deg, #dc5961, #d93c48 58%, #ed704f) !important; }
.stApp:has(.hg-fitness-page) [data-testid="stCheckbox"] label { color: #e8dfe1 !important; }
.stApp:has(.hg-fitness-page) [data-testid="stCheckbox"] input:checked + div { background: #ed6269 !important; border-color: #ed6269 !important; }
.stApp:has(.hg-fitness-page) [data-testid="stCheckbox"] { background: #21191c; border: 1px solid #3c2a2f; border-radius: 12px; padding: 10px 13px; margin: 5px 0; }
.stApp:has(.hg-fitness-page) [data-testid="stExpander"] { background: #21191c; border-color: #493137; border-radius: 12px; }
.stApp:has(.hg-fitness-page) [data-testid="stExpander"] summary { color: #f4edef; }
.hg-fitness-panel {
    background: linear-gradient(145deg, #21191c, #191416);
    border: 1px solid #3c2a2f;
    border-radius: 18px;
    padding: 19px 21px;
    margin: 3px 0 12px;
    box-shadow: 0 10px 26px rgba(0,0,0,.17);
}
.hg-fitness-panel h3 { margin: 8px 0 5px; color: #fff2ef; }
.hg-fitness-panel p { color: #b9a9ad; font-size: .9rem; }
.hg-fitness-kicker { color: #ff9b84; font-size: .68rem; font-weight: 800; letter-spacing: .16em; }
.hg-fitness-spotlight {
    min-height: 190px;
    padding: 25px 27px;
    border-radius: 20px;
    color: #fff8f5;
    background: radial-gradient(circle at 86% 48%, rgba(255,207,140,.38), transparent 17%), linear-gradient(125deg, #702832, #bd4147 58%, #f07959);
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 16px 35px rgba(207,66,74,.20);
    border: 1px solid rgba(255,255,255,.13);
}
.hg-fitness-spotlight h2 { color: #fff8f5 !important; margin: 10px 0 8px; }
.hg-fitness-spotlight p { color: #ffe3dc !important; max-width: 620px; }
.hg-fitness-tag { display: inline-block; color: #321518; background: #ffd18a; border-radius: 30px; padding: 7px 12px; font-size: .68rem; font-weight: 800; letter-spacing: .08em; }
.hg-fitness-emblem { width: 94px; height: 94px; flex: 0 0 94px; border: 1px solid rgba(255,255,255,.4); border-radius: 50%; display: grid; place-items: center; font-size: 3rem; color: #fff1d2; box-shadow: 0 0 0 12px rgba(255,255,255,.06), 0 0 55px rgba(255,207,140,.24); }
.hg-fitness-progress h3 { color: #fff2ef; margin: 11px 0 16px; }
.hg-fitness-progress p { color: #b9a9ad; font-size: .83rem; margin: 12px 0; }
.hg-progress-track { height: 9px; background: #39272c; border-radius: 9px; overflow: hidden; }
.hg-progress-track div { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #f26b70, #ffb370); }
.hg-progress-foot { display: flex; justify-content: space-between; color: #e4d4d7; font-size: .78rem; }
.hg-fitness-session { min-height: 102px; background: linear-gradient(145deg, #302126, #25191d); border: 1px solid #493137; border-radius: 13px; padding: 12px; margin: 5px 0; }
.hg-fitness-session span,.hg-fitness-meal span { display: block; color: #ff9b84; font-size: .64rem; font-weight: 800; letter-spacing: .12em; margin-bottom: 7px; }
.hg-fitness-session strong { display: block; color: #fff0ed; font-size: .86rem; margin-bottom: 6px; }
.hg-fitness-session small { color: #b9a9ad; font-size: .72rem; }
.hg-fitness-meal { min-height: 96px; background: #21191c; border: 1px solid #3c2a2f; border-radius: 14px; padding: 15px; }
.hg-fitness-meal p { color: #eee1e3; margin: 0; font-size: .84rem; }
.hg-fitness-footnote { margin-top: 12px; color: #b9a9ad; font-size: .8rem; }
.hg-fitness-onboarding { min-height: 170px; position: relative; overflow: hidden; }
.hg-fitness-onboarding h2 { color: #fff2ef; margin: 12px 0 4px; }
.hg-fitness-onboarding p { color: #c5b5b9; max-width: 640px; }
.hg-fitness-orbit { position: absolute; right: 8%; top: 18px; width: 125px; height: 125px; border: 1px solid #75414a; border-radius: 50%; display: grid; place-items: center; color: #ffba89; font-size: 3rem; box-shadow: 0 0 0 18px rgba(226,87,92,.06),0 0 70px rgba(226,87,92,.1); }
@media (max-width: 700px) {
    .hg-hero { padding: 25px 22px; border-radius: 18px; }
    .hg-hero h1 { font-size: 1.65rem; }
    [data-testid="stForm"] { padding: 17px; }
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='font-family:Plus Jakarta Sans;font-size:1.45rem;font-weight:800;line-height:1.15'>🧬 CareBuddy <span style='color:#5eead4'>AI</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:.8rem;margin-top:6px;color:#94a3b8'>YOUR PERSONAL HEALTH SPACE</p>", unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["Overview", "AI Symptom Analyzer", "Doctor Consultation", "AI Health Assistant", "Fitness AI Coach"],
        key="workspace_page",
        label_visibility="visible",
    )
    st.divider()
    st.markdown("<div style='font-size:.76rem;line-height:1.5;color:#94a3b8'>Your health, movement & everyday momentum.<br>Personalized plans. Small wins.</div>", unsafe_allow_html=True)

if page == "Overview":
    dashboard_page()
elif page == "AI Symptom Analyzer":
    symptom_page()
elif page == "Doctor Consultation":
    doctors_page()
elif page == "Fitness AI Coach":
    fitness_page()
else:
    ai_page()
