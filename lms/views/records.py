"""Complete create/read/update/delete screens for all five core entities."""
from datetime import date
import streamlit as st
from ..runtime import repository, settings
from ..errors import LMSError
from ..export import display_frame, safe_csv
from ..validation import MASTER_STATUSES, ENROLLMENT_STATUSES
from ..ui import heading, saved

from ..catalog import SINGULAR, DESCRIPTIONS, COLUMNS


def record_label(entity, row):
    if entity in {"students", "instructors"}:
        return f"{row['full_name']} | {row['email']} | #{row['id']}"
    if entity == "courses":
        return f"{row['course_name']} | #{row['id']}"
    return f"{row['student_name']} | {row['course_name']} | #{row['id']}"


def selector(label, rows, label_fn, key, current=None):
    lookup = {int(row["id"]): row for row in rows}
    options = [None] + list(lookup)
    index = options.index(current) if current in options else 0
    return st.selectbox(label, options, index=index,
                        format_func=lambda value: "Select a record" if value is None else label_fn(lookup[value]),
                        key=key)


def table(rows, columns, key):
    frame = display_frame(rows, columns)
    if frame.empty:
        st.info("No records match this view. Add a record or change the search and status filter.")
        return
    st.dataframe(frame, hide_index=True, width="stretch", height=min(565, 42 * (len(frame) + 1)),
                 row_height=42, placeholder="", column_config={"Percentage":st.column_config.ProgressColumn("Percentage", min_value=0, max_value=100, format="%.2f%%")})
    st.download_button("Export this view as CSV", safe_csv(frame), f"{key}.csv", "text/csv", key=f"csv_{key}")


def browse(entity, repo):
    a, b = st.columns([3, 1])
    with a:
        search = st.text_input("Search records", placeholder="Search by name, email or course", max_chars=160, key=f"search_{entity}")
    with b:
        choices = ENROLLMENT_STATUSES if entity in {"enrollments", "grades"} else MASTER_STATUSES
        state = st.selectbox("Status", ("All statuses",) + choices, key=f"status_{entity}")
    rows = repo.list_records(entity, search, None if state == "All statuses" else state)
    st.caption(f"{len(rows):,} matching record(s)")
    cols = dict(COLUMNS[entity])
    if entity == "courses":
        cols["fee"] = f"Fee ({settings().currency})"
    table(rows, cols, entity)
    if entity in {"students", "enrollments"}:
        with st.expander("Student enrollment history"):
            students = repo.list_records("students")
            selected = selector("Student", students, lambda row: row["full_name"] + " | " + row["email"], f"history_{entity}")
            if selected:
                history = repo.student_history(selected)
                if history:
                    table(history, {"id":"Enrollment ID", "course_name":"Course", "enrollment_date":"Enrollment date", "status":"Status", "assignment_marks":"Assignment /100", "quiz_marks":"Quiz /100", "final_exam_marks":"Final /100", "total_marks":"Total /300"}, f"{entity}_history_{selected}")
                    st.caption("Blank marks mean no grade record. This is enrollment history, not an audit log of every status change.")
                else:
                    st.info("This student has no course enrollments.")


def build_form(entity, repo, prefix, record=None):
    record = record or {}
    related = {}
    if entity == "courses":
        related["instructors"] = repo.list_records("instructors")
        if not related["instructors"]:
            st.info("Add an instructor before creating a course.")
            return False, {}
    elif entity == "enrollments":
        related["students"], related["courses"] = repo.list_records("students"), repo.list_records("courses")
        if not related["students"] or not related["courses"]:
            st.info("Add at least one student and one course before creating an enrollment.")
            return False, {}
    elif entity == "grades":
        all_enrollments = repo.list_records("enrollments")
        occupied = {row["enrollment_id"] for row in repo.list_records("grades")}
        related["enrollments"] = [row for row in all_enrollments if row["id"] not in occupied or row["id"] == record.get("enrollment_id")]
        if not related["enrollments"]:
            st.info("No ungraded enrollment is available. Create an enrollment or edit an existing grade.")
            return False, {}
    val = lambda field, default="": record.get(field, default)
    key = lambda field: f"{prefix}_{field}"
    with st.form(prefix, clear_on_submit=False):
        st.markdown("#### " + ("Update " if record else "New ") + SINGULAR[entity])
        if entity in {"students", "instructors"}:
            a,b = st.columns(2)
            with a:
                full_name = st.text_input("Full name", val("full_name"), max_chars=120, key=key("name"))
            with b:
                email = st.text_input("Email", val("email"), max_chars=254, key=key("email"))
            a,b = st.columns(2)
            with a:
                if entity == "students":
                    extra = st.text_input("Phone (optional)", val("phone"), max_chars=32, key=key("phone"))
                else:
                    extra = st.text_input("Specialization", val("specialization"), max_chars=120, key=key("specialization"))
            with b:
                status = st.selectbox("Status", MASTER_STATUSES, index=MASTER_STATUSES.index(val("status", "Active")), key=key("status"))
            values = dict(full_name=full_name,email=email,status=status)
            if entity == "students":
                joined = st.date_input("Institute enrollment date", val("enrollment_date",date.today()), min_value=date(1900,1,1), max_value=date.today(), key=key("date"))
                values.update(phone=extra,enrollment_date=joined)
            else:
                values["specialization"] = extra
        elif entity == "courses":
            name = st.text_input("Course name", val("course_name"), max_chars=150, key=key("name"))
            description = st.text_area("Description", val("description"), max_chars=5000, height=105, key=key("description"))
            instructor = selector("Instructor",related["instructors"],lambda row: f"{row['full_name']} | {row['specialization']} | {row['status']}",key("instructor"),val("instructor_id",None))
            a,b,c=st.columns(3)
            with a:
                duration = st.number_input("Duration (hours)",min_value=1,max_value=10000,value=int(val("duration_hours",24)),step=1,key=key("duration"))
            with b:
                fee = st.number_input(f"Fee ({settings().currency})",min_value=0.0,max_value=99999999.99,value=float(val("fee",0)),step=100.0,format="%.2f",key=key("fee"))
            with c:
                status = st.selectbox("Status",MASTER_STATUSES,index=MASTER_STATUSES.index(val("status","Active")),key=key("status"))
            values = dict(course_name=name,description=description,instructor_id=instructor,duration_hours=duration,fee=fee,status=status)
        elif entity == "enrollments":
            a,b=st.columns(2)
            with a:
                student = selector("Student",related["students"],lambda row:f"{row['full_name']} | {row['email']} | {row['status']}",key("student"),val("student_id",None))
            with b:
                course = selector("Course",related["courses"],lambda row:f"{row['course_name']} | {row['status']}",key("course"),val("course_id",None))
            a,b=st.columns(2)
            with a:
                joined = st.date_input("Course enrollment date",val("enrollment_date",date.today()),min_value=date(1900,1,1),max_value=date.today(),key=key("date"))
            with b:
                status = st.selectbox("Status",ENROLLMENT_STATUSES,index=ENROLLMENT_STATUSES.index(val("status","Enrolled")),key=key("status"))
            st.caption("One enrollment per student and course. Re-enroll by updating the existing record. Inactive records remain selectable for historical administration.")
            values = dict(student_id=student,course_id=course,enrollment_date=joined,status=status)
        else:
            enrollment = selector("Enrollment",related["enrollments"],lambda row:f"{row['student_name']} | {row['course_name']} | {row['status']} | #{row['id']}",key("enrollment"),val("enrollment_id",None))
            st.caption("Each assessment is out of 100. Total = assignment + quiz + final exam, out of 300. No weighting or pass/fail threshold is applied.")
            columns=st.columns(3)
            values={"enrollment_id":enrollment}
            for col,field,label in zip(columns,("assignment_marks","quiz_marks","final_exam_marks"),("Assignment /100","Quiz /100","Final exam /100")):
                with col:
                    default=float(record[field]) if field in record else None
                    values[field]=st.number_input(label,min_value=0.0,max_value=100.0,value=default,step=1.0,format="%.2f",key=key(field))
            st.caption("Enter all three marks to save. A missing grade is not the same as a zero mark.")
        submitted=st.form_submit_button("Save changes" if record else f"Add {SINGULAR[entity]}",type="primary")
    return submitted, values


def add(entity,repo):
    generation=st.session_state.get(f"_form_generation_{entity}",0)
    submitted,values=build_form(entity,repo,f"add_{entity}_{generation}")
    if submitted:
        try:
            record_id=repo.create(entity,values)
            saved(f"{SINGULAR[entity].capitalize()} #{record_id} added.",entity)
        except LMSError as exc:
            st.error(str(exc))


def snapshot(entity,record_id,repo,purpose):
    key=f"_snapshot_{entity}_{purpose}_{record_id}"
    if key not in st.session_state:
        st.session_state[key]=repo.get(entity,record_id)
    return st.session_state[key],key


def edit(entity,repo):
    rows=repo.list_records(entity)
    if not rows:
        st.info("Add a record before editing.")
        return
    record_id=selector(f"Choose a {SINGULAR[entity]} to edit",rows,lambda row:record_label(entity,row),f"edit_choice_{entity}")
    if record_id is None:
        return
    record,snapshot_key=snapshot(entity,record_id,repo,"edit")
    nonce_key=f"_reload_{entity}_{record_id}"
    if st.button("Reload selected record",key=f"reload_{entity}"):
        st.session_state.pop(snapshot_key,None)
        st.session_state[nonce_key]=st.session_state.get(nonce_key,0)+1
        st.rerun()
    st.caption(f"Editing record #{record_id}. Revision {record['version']}. Reload discards unsaved changes.")
    prefix=f"edit_{entity}_{record_id}_{record['version']}_{st.session_state.get(nonce_key,0)}"
    submitted,values=build_form(entity,repo,prefix,record)
    if submitted:
        try:
            repo.update(entity,record_id,record["version"],values)
            saved(f"{SINGULAR[entity].capitalize()} #{record_id} updated.",entity)
        except LMSError as exc:
            st.error(str(exc))


def delete(entity,repo):
    rows=repo.list_records(entity)
    if not rows:
        st.info("There are no records to delete.")
        return
    record_id=selector(f"Choose a {SINGULAR[entity]} to delete",rows,lambda row:record_label(entity,row),f"delete_choice_{entity}")
    if record_id is None:
        return
    record,snapshot_key=snapshot(entity,record_id,repo,"delete")
    if st.button("Reload deletion details",key=f"delete_reload_{entity}"):
        st.session_state.pop(snapshot_key,None)
        st.rerun()
    dependencies=repo.dependencies(entity,record_id)
    blocked={name:count for name,count in dependencies.items() if count}
    if blocked:
        st.warning("Deletion is blocked: " + ", ".join(f"{count} related {name}" for name,count in blocked.items()) + ". Remove dependent records first. No records are deleted automatically.")
    else:
        st.warning("This permanently deletes the selected record. There is no undo. Keep records with historical value and change their status instead.")
    with st.form(f"delete_form_{entity}_{record_id}_{record['version']}"):
        st.write(f"Selected {SINGULAR[entity]} ID: {record_id}")
        confirmation=st.text_input("Type DELETE to confirm",key=f"delete_text_{entity}_{record_id}_{record['version']}")
        checked=st.checkbox("I have checked the selected record and understand that deletion is permanent.",key=f"delete_ack_{entity}_{record_id}_{record['version']}")
        submitted=st.form_submit_button(f"Permanently delete {SINGULAR[entity]}",disabled=bool(blocked),type="secondary")
    if submitted:
        if confirmation.strip()!="DELETE" or not checked:
            st.error("Type DELETE and check the confirmation box before deleting.")
        else:
            try:
                repo.delete(entity,record_id,record["version"])
                saved(f"{SINGULAR[entity].capitalize()} #{record_id} deleted.",entity)
            except LMSError as exc:
                st.error(str(exc))


def render(entity):
    repo=repository()
    heading(entity.capitalize(),DESCRIPTIONS[entity])
    tabs=st.tabs(["Records",f"Add {SINGULAR[entity]}",f"Edit {SINGULAR[entity]}",f"Delete {SINGULAR[entity]}"])
    for tab,fn in zip(tabs,(browse,add,edit,delete)):
        with tab:
            fn(entity,repo)


def students(): render("students")
def instructors(): render("instructors")
def courses(): render("courses")
def enrollments(): render("enrollments")
def grades(): render("grades")
