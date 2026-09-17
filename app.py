"""Entry point: python -m streamlit run app.py"""
from html import escape
import streamlit as st
from lms.config import ROOT, Settings
from lms.errors import LMSError
from lms.ui import brand_html, flash
from lms.views import dashboard, records, reports_page, legal

st.set_page_config(page_title="Coursebook",page_icon=str(ROOT/"assets/favicon.svg"),layout="wide",initial_sidebar_state="auto")
st.html("<style>"+(ROOT/"assets/style.css").read_text()+"</style>")
try:
    cfg=Settings.from_env()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

main_pages=[
    st.Page(dashboard.render,title="Dashboard",icon=":material/space_dashboard:",default=True),
    st.Page(records.students,title="Students",icon=":material/group:",url_path="students"),
    st.Page(records.instructors,title="Instructors",icon=":material/person:",url_path="instructors"),
    st.Page(records.courses,title="Courses",icon=":material/menu_book:",url_path="courses"),
    st.Page(records.enrollments,title="Enrollments",icon=":material/assignment:",url_path="enrollments"),
    st.Page(records.grades,title="Grades",icon=":material/grading:",url_path="grades"),
    st.Page(reports_page.render,title="Reports",icon=":material/bar_chart:",url_path="reports"),
]
legal_pages=[
    st.Page(legal.terms,title="Terms & Conditions",url_path="terms"),
    st.Page(legal.privacy,title="Privacy policy",url_path="privacy"),
]
page=st.navigation(main_pages+legal_pages,position="hidden")
st.set_page_config(page_title=f"{page.title} | Coursebook",page_icon=str(ROOT/"assets/favicon.svg"))
with st.sidebar:
    st.html(brand_html())
    st.html('<div class="cb-sidebar-section">WORKSPACE</div>')
    for item in main_pages:
        st.page_link(item,label=item.title,icon=item.icon)
    st.html('<div class="cb-sidebar-note"><strong>Local academic workspace</strong><p>No account login is enabled. Keep this application on localhost or behind institute-managed authentication.</p></div>')
    st.divider()
    for item in legal_pages:
        st.page_link(item,label=item.title)
    st.caption("Coursebook / v1.0")

st.html(f'<div class="cb-topline"><strong>{escape(cfg.institute)}</strong><span>Academic records / MySQL workspace</span></div>')
st.html(
    '<div class="cb-data-note"><strong>Welcome to Talha\'s Learning Management System</strong>'
    'A complete academic management project built to manage records, track performance, and generate useful insights from MySQL data.</div>'
)
flash()
try:
    page.run()
except LMSError as exc:
    st.error(str(exc))
    st.code("python scripts/doctor.py",language="bash")
    st.caption("No data is shown from a fallback database. The application requires the configured MySQL connection.")
    if st.button("Try again",key="retry_connection"):
        st.rerun()
st.html('<div class="cb-footer">Coursebook keeps academic records in your configured MySQL database. Refresh a page to retrieve current data.</div>')
