"""Static contracts only. Real MySQL syntax is checked by opt-in integration tests."""
import ast
from pathlib import Path
from lms.reports import REPORTS

ROOT=Path(__file__).resolve().parents[1]


def test_all_python_files_parse():
    for file in ROOT.rglob("*.py"):
        if ".venv" not in file.parts:
            ast.parse(file.read_text(encoding="utf-8"),filename=str(file))


def test_core_schema_contract():
    schema=(ROOT/"database/schema.sql").read_text()
    assert schema.count("CREATE TABLE IF NOT EXISTS")==5
    assert schema.count("FOREIGN KEY")==4
    assert "UNIQUE (student_id, course_id)" in schema
    assert "UNIQUE (enrollment_id)" in schema
    assert "GENERATED ALWAYS AS (assignment_marks + quiz_marks + final_exam_marks) STORED" in schema
    assert "ON DELETE CASCADE" not in schema
    assert "COLLATE ascii_bin" in schema


def test_submitted_sql_matches_modules():
    sql=(ROOT/"lms_database.sql").read_text()
    assert (ROOT/"database/schema.sql").read_text() in sql
    assert (ROOT/"database/sample_data.sql").read_text() in sql
    assert "DROP TABLE" not in sql
    report_sql=(ROOT/"database/reports.sql").read_text()
    for report in REPORTS: assert report.sql.strip() in report_sql


def test_runtime_has_no_sqlite_fallback():
    for path in (ROOT/"lms").rglob("*.py"):
        assert "import sqlite3" not in path.read_text()


def test_required_artifacts():
    for name in ["app.py","lms_database.sql",".env.example","assets/favicon.png","assets/favicon.svg","docs/TERMS.md","docs/PRIVACY.md"]:
        assert (ROOT/name).is_file()
