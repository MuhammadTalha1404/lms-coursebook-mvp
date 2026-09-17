from datetime import date
from decimal import Decimal
import pytest
from lms.errors import ValidationError,ConflictError,RelatedRecordsError,NotFoundError
from lms.validation import FIELDS


def student(email="new.student@example.test"):
    return dict(full_name="New Student",email=email,phone="",enrollment_date=date(2026,1,1),status="Active")


def lifecycle(repo):
    iid=repo.create("instructors",dict(full_name="Test Teacher",specialization="Testing",email="teacher@example.test",status="Active"))
    cid=repo.create("courses",dict(course_name="Test Course",description="",instructor_id=iid,duration_hours=10,fee=Decimal("100.25"),status="Active"))
    sid=repo.create("students",student())
    eid=repo.create("enrollments",dict(student_id=sid,course_id=cid,enrollment_date=date(2026,2,1),status="Enrolled"))
    gid=repo.create("grades",dict(enrollment_id=eid,assignment_marks=10.25,quiz_marks=20.5,final_exam_marks=30))
    assert Decimal(str(repo.get("grades",gid)["total_marks"]))==Decimal("60.75")
    for entity,record_id in (("instructors",iid),("courses",cid),("students",sid),("enrollments",eid),("grades",gid)):
        row=repo.get(entity,record_id)
        values={field:row[field] for field in FIELDS[entity]}
        if entity in {"students","instructors"}: values["full_name"]="Updated Person"
        elif entity=="courses": values["course_name"]="Updated Course"
        elif entity=="enrollments": values["status"]="Completed"
        else: values["final_exam_marks"]=90
        repo.update(entity,record_id,row["version"],values)
        assert repo.get(entity,record_id)["version"]==2
    assert Decimal(str(repo.get("grades",gid)["total_marks"]))==Decimal("120.75")
    for entity,record_id in (("grades",gid),("enrollments",eid),("students",sid),("courses",cid),("instructors",iid)):
        repo.delete(entity,record_id,2)
        with pytest.raises(NotFoundError): repo.get(entity,record_id)


def test_end_to_end_all_five_entities(empty_repo): lifecycle(empty_repo)

@pytest.mark.parametrize("entity,id",[("students",1),("instructors",1),("courses",1),("enrollments",1)])
def test_protected_deletions(repo,entity,id):
    with pytest.raises(RelatedRecordsError): repo.delete(entity,id,1)
    assert repo.get(entity,id)

@pytest.mark.parametrize("entity,id",[("students",1),("instructors",1),("courses",1),("enrollments",1),("grades",1)])
def test_stale_edits_are_rejected(repo,entity,id):
    row=repo.get(entity,id)
    values={field:row[field] for field in FIELDS[entity]}
    repo.update(entity,id,1,values)
    with pytest.raises(ConflictError): repo.update(entity,id,1,values)
    with pytest.raises(ConflictError): repo.delete(entity,id,1)


def test_duplicate_student_email(repo):
    with pytest.raises(ConflictError,match="email"):
        repo.create("students",student("AMINA.KHAN@example.test"))


def test_duplicate_instructor_email(repo):
    with pytest.raises(ConflictError,match="email"):
        repo.create("instructors",dict(full_name="Different Name",specialization="SQL",email="SARA.MALIK@example.test",status="Active"))


def test_duplicate_enrollment_including_dropped(repo):
    with pytest.raises(ConflictError,match="already has an enrollment"):
        repo.create("enrollments",dict(student_id=10,course_id=5,enrollment_date=date(2026,8,12),status="Enrolled"))


def test_duplicate_grade(repo):
    with pytest.raises(ConflictError,match="Marks already exist"):
        repo.create("grades",dict(enrollment_id=1,assignment_marks=0,quiz_marks=0,final_exam_marks=0))


def test_zero_grade_is_recorded_not_missing(repo):
    gid=repo.create("grades",dict(enrollment_id=5,assignment_marks=0,quiz_marks=0,final_exam_marks=0))
    assert repo.get("grades",gid)["total_marks"]==0
    assert any(row["student_id"]==5 for row in repo.report("BR-03"))


def test_cannot_reassign_graded_enrollment(repo):
    row=repo.get("enrollments",1)
    values={field:row[field] for field in FIELDS["enrollments"]}
    values["course_id"]=6
    with pytest.raises(ValidationError,match="has grades"):
        repo.update("enrollments",1,1,values)
    assert repo.get("enrollments",1)["course_id"]==1


def test_course_enrollment_date_not_before_institute_date(repo):
    with pytest.raises(ValidationError,match="predate"):
        repo.create("enrollments",dict(student_id=12,course_id=6,enrollment_date=date(2026,1,1),status="Enrolled"))


def test_student_date_edit_preserves_history(repo):
    row=repo.get("students",1)
    values={field:row[field] for field in FIELDS["students"]}
    values["enrollment_date"]=date(2026,8,1)
    with pytest.raises(ValidationError,match="earliest"):
        repo.update("students",1,1,values)


def test_nonexistent_foreign_keys(repo):
    with pytest.raises(ValidationError,match="existing instructor"):
        repo.create("courses",dict(course_name="Unknown teacher",description="",instructor_id=999,duration_hours=10,fee=0,status="Active"))
    with pytest.raises(ValidationError,match="existing enrollment"):
        repo.create("grades",dict(enrollment_id=999,assignment_marks=10,quiz_marks=10,final_exam_marks=10))


def test_search_parameterization(repo):
    assert repo.list_records("students","' OR 1=1 --")==[]
    assert len(repo.list_records("students"))==12
    assert len(repo.list_records("students","Amina"))==1
    assert len(repo.list_records("courses","Sara"))==2
    assert len(repo.list_records("students",status="Inactive"))==2


def test_literal_wildcard_search(repo):
    values=student()
    values["full_name"]="Test 50%_entry!"
    repo.create("students",values)
    assert len(repo.list_records("students","50%_"))==1
    assert len(repo.list_records("students","%"))==1


def test_unknown_table_and_bad_ids(repo):
    with pytest.raises(ValidationError): repo.list_records("students; DROP TABLE courses")
    with pytest.raises(ValidationError): repo.get("students",0)
    with pytest.raises(NotFoundError): repo.get("students",9999)


def test_history_uses_left_join_for_ungraded_records(repo):
    history=repo.student_history(3)
    assert len(history)==2
    assert any(row["total_marks"] is None for row in history)


def test_failed_transaction_rolls_back(repo):
    before=len(repo.list_records("students"))
    with pytest.raises(RuntimeError):
        with repo.db.session(write=True) as cursor:
            cursor.execute("INSERT INTO students(full_name,email,phone,enrollment_date,status) VALUES (%s,%s,%s,%s,%s)",( "Rollback Student","rollback@example.test","",date(2026,1,1),"Active"))
            raise RuntimeError("rollback")
    assert len(repo.list_records("students"))==before
