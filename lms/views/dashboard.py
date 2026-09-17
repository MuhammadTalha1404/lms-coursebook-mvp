import streamlit as st
from ..runtime import repository
from ..ui import heading, kpis_html, bars_html, status_html, table_html, updated_caption


def render():
    repo = repository()
    heading("Academic overview", "Student records, teaching assignments and course activity at a glance.")
    summary = repo.summary()
    left, right = st.columns([4, 1])
    with left:
        updated_caption()
    with right:
        if st.button("Refresh data", width="stretch", key="refresh_dashboard"):
            st.rerun()
    st.html(kpis_html(summary))
    popularity, statuses = repo.report("BR-01"), repo.report("BR-05")
    left, right = st.columns([1.65, 1], gap="medium")
    with left:
        st.html('<section class="cb-card"><h2 class="cb-card-title">Course popularity</h2><p class="cb-card-caption">Enrollment records across all statuses. Top six courses.</p>' + bars_html(popularity, "course_name", "total_enrollments", limit=6) + '</section>')
    with right:
        st.html('<section class="cb-card"><h2 class="cb-card-title">Enrollment status</h2><p class="cb-card-caption">Current status of every enrollment record.</p>' + status_html(statuses) + '</section>')
    st.write("")
    recent = repo.recent_enrollments()
    st.html('<section class="cb-card"><div class="cb-section-line"><div><h2 class="cb-card-title">Recent enrollments</h2><p class="cb-card-caption" style="margin-bottom:0">The six most recent course enrollment dates.</p></div></div>' + table_html(recent, {"student_name":"Student", "course_name":"Course", "enrollment_date":"Enrolled on", "status":"Status"}) + '</section>')
    if int(summary.get("awaiting_grades", 0)):
        st.caption(f"{int(summary['awaiting_grades'])} non-dropped enrollment(s) do not have a grade record yet. Open Grades to record marks.")
    elif not summary.get("enrollments"):
        st.info("Start with an instructor and a course, add a student, then create an enrollment.")
