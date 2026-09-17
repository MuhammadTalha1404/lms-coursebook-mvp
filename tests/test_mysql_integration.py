"""Runs against actual MySQL only. Never silently substitutes another database."""
from decimal import Decimal
import pytest
from lms.errors import ValidationError,RelatedRecordsError,ConflictError
from lms.reports import REPORTS
from .test_repository import lifecycle

pytestmark=pytest.mark.integration


def test_mysql_complete_crud_lifecycle(mysql_repo): lifecycle(mysql_repo)


def test_mysql_sample_schema_and_foreign_keys(mysql_repo):
    assert mysql_repo.summary()["students"]==12
    assert mysql_repo.summary()["enrollments"]==18
    assert len(mysql_repo.db.health())==3

@pytest.mark.parametrize("report",REPORTS,ids=lambda report:report.id)
def test_mysql_report_queries(mysql_repo,report):
    assert mysql_repo.report(report.id) is not None


def test_mysql_generated_totals_and_checks(mysql_repo):
    assert Decimal(str(mysql_repo.get("grades",1)["total_marks"]))==Decimal("273")
    with pytest.raises(ValidationError):
        with mysql_repo.db.session(write=True) as cursor:
            cursor.execute("UPDATE grades SET assignment_marks=%s WHERE id=%s",(101,1))
    assert Decimal(str(mysql_repo.get("grades",1)["assignment_marks"]))==Decimal("91")


def test_mysql_status_case_enforced(mysql_repo):
    with pytest.raises(ValidationError):
        with mysql_repo.db.session(write=True) as cursor:
            cursor.execute("UPDATE students SET status=%s WHERE id=%s",("active",1))


def test_mysql_fk_blocks_deletion(mysql_repo):
    with pytest.raises(RelatedRecordsError):
        with mysql_repo.db.session(write=True) as cursor:
            cursor.execute("DELETE FROM instructors WHERE id=%s",(1,))


def test_mysql_duplicate_enrollment_constraint(mysql_repo):
    with pytest.raises(ConflictError):
        with mysql_repo.db.session(write=True) as cursor:
            cursor.execute("INSERT INTO enrollments(student_id,course_id,enrollment_date,status) VALUES(%s,%s,%s,%s)",(1,1,"2026-07-01","Enrolled"))
