# Requirement traceability

Source: the uploaded **SQL Mini Project-LMS-Students.pdf**, headed **LMS Client Requirements - Mini Project**, pages 1-2. The table below maps the brief to the delivered implementation. It does not claim that unexecuted runtime acceptance tests passed.

| Brief requirement | Delivered implementation | Verification path |
| --- | --- | --- |
| MySQL, Python, Streamlit, Pandas | `requirements.txt`, `app.py`, `lms/db.py`, `lms/export.py` | Install pinned dependencies; run `scripts/doctor.py` |
| Students: add/view/search/update/delete and required fields | `lms/views/records.py`, student schema and validators | Offline lifecycle tests; real UI and MySQL tests supplied |
| Instructors: CRUD, specialization, email, status | Instructor form, schema and validators | Lifecycle and duplicate-email tests |
| Courses: name, description, instructor, duration, fee, status | Course form with instructor dropdown and decimal fee | Lifecycle and FK tests |
| Enroll a student, view history, update status | Enrollment CRUD, unique pair, student history join | Duplicate, history and status tests |
| Record assessment marks and calculate total | Grade CRUD, three mark fields, generated `total_marks` | Grade range and calculation tests |
| Dashboard student/instructor/course/enrollment KPIs | `SUMMARY_SQL` subqueries and database-fed visual cards | Seed and empty-data tests; runtime check still required |
| Basic charts and tables | Escaped HTML bar/status charts, recent table, Pandas dataframes | Preview browser checks; runtime smoke tests supplied |
| Five core tables and relationships | `database/schema.sql` | Static contract test; actual MySQL DDL test supplied |
| Primary/foreign keys, NOT NULL, UNIQUE email, controlled status | Explicit named constraints; case-insensitive email and case-sensitive status values | Python checks passed; server enforcement tests supplied |
| Prevent duplicate student/course enrollment | `uq_enrollments_student_course` | Offline and actual-MySQL duplicate tests |
| CRUD for all five entities | Generic allowlisted repository and five form families | Full lifecycle test; actual-MySQL lifecycle supplied |
| Required SQL concepts | `lms_database.sql`, `database/reports.sql`, `database/crud_examples.sql` | Static checks and report result tests |
| Seven named navigation screens | Dashboard, Students, Instructors, Courses, Enrollments, Grades, Reports | Source review and runtime smoke suite |
| Forms and related-record dropdowns | Streamlit forms/selectboxes, including grade enrollment selection | Runtime tests supplied |
| Searchable tables and validation | Parameterized search, status filtering, Pandas table display | Search and validation unit tests |
| Success/error messages and destructive confirmation | Flash messages, safe error types, checkbox and DELETE confirmation | Source review and deletion service tests |
| Parameterized Python-MySQL queries | `%s` bindings; table/column identifiers from allowlists | Search-injection tests and source review |
| BR-01 through BR-06 | Six report definitions with visible SQL and displayed results | All six result tests; six actual-MySQL report tests supplied |
| Live database metrics and reports | Runtime reads only from configured MySQL; no fallback data in app | Integration verification must be run locally |
| `lms_database.sql` with sample data | Root-level combined schema/sample deliverable | Static parity check; import into MySQL required |
| Setup/configuration/execution documentation | README, wizard, environment example, run scripts, Docker option | Source and syntax checks; actual install not run here |
| Screenshots | Labeled HTML-preview screenshots plus runtime capture script | Preview screenshots inspected; runtime captures still to generate |
| Short demonstration presentation | `docs/Coursebook-Demo.pptx` and `docs/DEMO.md` | Slide render/layout checks |
| User addition: Terms & Conditions | `docs/TERMS.md`, `/terms` page | Template content included; institute details require completion |
| User addition: privacy policy | `docs/PRIVACY.md`, `/privacy` page | Default behavior documented; deployment review required |
| User addition: favicon | SVG, PNG and ICO; `st.set_page_config` uses PNG | Files generated and preview icon checked |

## Optional extensions

CSV export was included. Attendance, payments, certificates, batches, completion percentages, stored procedures, individual login/roles and advanced analytics were not required by the brief and are not represented as implemented.

## Acceptance boundary

The build environment verified Python logic, report results through a test adapter, source contracts and the static design preview. It could not install Streamlit/Connector/Python or start a real MySQL service. Accordingly, **successful MySQL import, live Streamlit database behavior and full runtime acceptance remain to be verified using the supplied test suite in the user's environment**.
