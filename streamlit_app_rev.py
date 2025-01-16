import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- PAGE SETUP ---
about_page = st.Page(
    "views/mainpage.py",
    title="about",
    icon=":material/account_circle:",
)
project_1_page = st.Page(
    "views/Running_Script_rev.py",
    title="Running Script",
    icon=":material/account_circle:",
)
project_2_page = st.Page(
    "views/indicator.py",
    title="Indicator",
    icon=":material/bar_chart:",
)
project_3_page = st.Page(
    "views/Summary_rev.py",
    title="Information per Product",
    icon=":material/bar_chart:",
)
project_4_page = st.Page(
    "views/Summary_per_cohort.py",
    title="Information per Cohort",
    icon=":material/bar_chart:",
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Menu": [about_page, project_1_page, project_2_page, project_3_page, project_4_page],
    }
)

# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")
st.sidebar.markdown("Reference from [Sven](https://youtube.com/@codingisfun)")


# --- RUN NAVIGATION ---
pg.run()