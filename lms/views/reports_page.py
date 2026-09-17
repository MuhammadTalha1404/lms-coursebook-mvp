import streamlit as st
from ..runtime import repository
from ..reports import REPORTS, REPORT_BY_ID
from ..export import display_frame, safe_csv
from ..ui import heading, bars_html, status_html, updated_caption


def render():
    heading("Reports", "Six management reports, calculated directly from your academic records.", "Insights")
    a,b=st.columns([4,1])
    with a:
        selected=st.selectbox("Report",[r.id for r in REPORTS],format_func=lambda key:f"{key} | {REPORT_BY_ID[key].title}",key="selected_report")
    with b:
        st.write("")
        if st.button("Refresh data",width="stretch",key="refresh_reports"):
            st.rerun()
    report=REPORT_BY_ID[selected]
    st.subheader(report.title)
    st.caption(report.description)
    rows=repository().report(selected)
    if selected=="BR-04":
        st.metric("Active students",int(rows[0]["active_students"]))
    elif selected=="BR-05":
        st.html('<div class="cb-card">'+status_html(rows)+'</div>')
    elif selected in {"BR-01","BR-02","BR-03"} and rows:
        label,value={"BR-01":("course_name","total_enrollments"),"BR-02":("instructor_name","course_count"),"BR-03":("student_name","total_marks")}[selected]
        st.html('<div class="cb-card"><p class="cb-card-caption">Top ten results. The table and export include every result.</p>'+bars_html(rows,label,value,limit=10)+'</div>')
    columns={key:key.replace("_"," ").capitalize() for key in rows[0]} if rows else None
    frame=display_frame(rows,columns)
    if frame.empty:
        st.info("No matching records. This report will update as records are added or changed.")
    else:
        st.dataframe(frame,width="stretch",hide_index=True,row_height=42,height=min(560,42*(len(frame)+1)))
        st.download_button("Export report as CSV",safe_csv(frame),f"{selected.lower()}.csv","text/csv",key="report_csv")
    with st.expander("View the SQL query"):
        st.code(report.sql.strip()+";",language="sql")
        st.download_button("Download SQL",report.sql.strip()+";\n",f"{selected.lower()}.sql","text/plain",key="report_sql")
    updated_caption()
