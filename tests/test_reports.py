from decimal import Decimal
import pytest
from lms.reports import REPORTS


def test_dashboard_seed_totals(repo):
    s=repo.summary()
    assert (s["students"],s["instructors"],s["courses"],s["enrollments"])==(12,4,6,18)
    assert (s["active_students"],s["active_instructors"],s["active_courses"])==(10,3,5)
    assert s["current_enrollments"]==11
    assert s["graded_enrollments"]==10
    assert s["awaiting_grades"]==6


def test_course_popularity(repo):
    rows=repo.report("BR-01")
    assert rows[0]["course_name"]=="Database Foundations"
    assert rows[0]["total_enrollments"]==5
    assert rows[0]["currently_enrolled"]==3
    assert sum(row["total_enrollments"] for row in rows)==18
    assert rows[-1]["total_enrollments"]==0


def test_instructor_workload(repo):
    rows=repo.report("BR-02")
    assert len(rows)==4
    assert sum(row["course_count"] for row in rows)==6
    assert sum(row["assigned_hours"] for row in rows)==222


def test_performance_exact_totals(repo):
    rows=repo.report("BR-03")
    assert rows[0]["student_id"]==1
    assert Decimal(str(rows[0]["total_marks"]))==Decimal("542")
    assert rows[0]["graded_courses"]==2
    assert float(rows[0]["average_percentage"])==90.33
    assert not any(row["student_id"]==12 for row in rows)


def test_active_count(repo): assert repo.report("BR-04")==[{"active_students":10}]


def test_all_status_counts(repo):
    assert repo.report("BR-05")==[{"status":"Enrolled","enrollment_count":11},{"status":"Completed","enrollment_count":5},{"status":"Dropped","enrollment_count":2}]


def test_course_with_no_enrollments(repo):
    rows=repo.report("BR-06")
    assert len(rows)==1
    assert rows[0]["course_name"]=="Business Analysis"

@pytest.mark.parametrize("report",REPORTS,ids=lambda report:report.id)
def test_reports_work_with_empty_database(empty_repo,report):
    rows=empty_repo.report(report.id)
    if report.id=="BR-04": assert rows==[{"active_students":0}]
    elif report.id=="BR-05": assert len(rows)==3 and all(row["enrollment_count"]==0 for row in rows)
    else: assert rows==[]


def test_recent_enrollments_sorted(repo):
    rows=repo.recent_enrollments(3)
    assert len(rows)==3
    assert [row["id"] for row in rows]==[18,15,17]
