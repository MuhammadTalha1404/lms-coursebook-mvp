# Coursebook
## Learning Management System

A MySQL, Python, Streamlit and Pandas project built around the supplied **LMS Client Requirements - Mini Project**. It manages students, instructors, courses, enrollments and grades through seven application screens. The additional Terms & Conditions and privacy pages are accessible from the sidebar, and a local favicon is included.

This is an academic administration application, not a marketing website or a video-course platform.

### Start here

On your Mac, open Terminal in the extracted `coursebook-lms` folder and run:

```bash
bash run.sh
```

On the first run, this creates a Python virtual environment, installs dependencies and runs an interactive MySQL setup. It asks for your existing MySQL administrator password once. That password is not saved. Setup creates a separate application database account, saves its generated password in `.env`, and imports clearly fictional training data.

Your MySQL server must already be running. Use **Python 3.11, 3.12 or 3.13**. If `python3` points to a different Python version, select one explicitly:

```bash
PYTHON=python3.12 bash run.sh
```

Once started, open `http://localhost:8501`. Keep Terminal open while using the application. Press `Control+C` in Terminal to stop it. On Windows, run `run.bat` or follow the manual setup below.

**Verification status:** 131 offline checks passed in the build environment. The 12 real-MySQL and 10 Streamlit runtime checks are included but were not run here: MySQL and Streamlit were unavailable and the environment blocked dependency downloads. Offline database tests use an explicitly test-only SQLite adapter. The application itself has no SQLite fallback. Read [the test report](docs/TEST_REPORT.md) before treating the project as deployment-verified.

## What is included

| Screen | Functions |
| --- | --- |
| Dashboard | Live database counts, course-popularity chart, enrollment-status chart, recent enrollments and missing-grade count |
| Students | Add, search, view, update and delete; name, email, phone, enrollment date and status; enrollment history |
| Instructors | Add, search, view, update and delete; specialization, email and status |
| Courses | Add, search, view, update and delete; description, related instructor, duration, fee and status |
| Enrollments | Add, search, view, update and delete; student/course dropdowns; Enrolled, Completed and Dropped; student history |
| Grades | Add, search, view, update and delete; assignment, quiz, final examination and generated total |
| Reports | BR-01 through BR-06; chart or summary, full result table, visible SQL and CSV/SQL downloads |
| Terms & Conditions | Editable institute policy template |
| Privacy policy | A description of the project's default data handling, with deployment details to complete |

All directory screens have **Records**, **Add**, **Edit** and **Delete** tabs. Filters affect the displayed table and its CSV export. Search uses parameterized `LIKE` expressions; literal percent signs and underscores are escaped.

There are no invented growth figures, testimonials, animated counters, generated photographic assets, cursor effects or decorative scroll animations. The interface uses solid green and neutral surfaces, local geometric artwork, standard line icons and rectangular controls.

## Important implementation choices

The source brief does not specify these details. They are explicit project conventions, not additional client requirements:

* Each assessment is **0-100**. Total marks are the unweighted sum, **0-300**; percentage is total divided by three. All three marks are required to create a grade. A missing grade is not recorded as zero. There is no assumed pass threshold or letter-grade scheme.
* Course duration is in **hours**. Fees use the currency in `APP_CURRENCY`, initially `PKR`. Fees are catalog values, not collected revenue; payment tracking is not included.
* Students, instructors and courses use `Active` / `Inactive`. Enrollments use exactly `Enrolled` / `Completed` / `Dropped`. Inactive records remain selectable to allow historical administration.
* Enrollment history means the student's existing course enrollment records, dates and current statuses. This project does not keep an audit log of every status change.
* `UNIQUE(student_id, course_id)` applies even to a Dropped enrollment. Change the existing enrollment rather than inserting a second one.
* One grade record belongs to one enrollment. Changing the student or course on an already graded enrollment is blocked until its grade record is removed. A course enrollment cannot predate the student's institute enrollment date.

See [the requirement matrix](docs/REQUIREMENTS.md) and [the data model](docs/ERD.md) for the detailed mapping.

## Manual local setup

### 1. Create the Python environment

```bash
cd /path/to/coursebook-lms
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead. The pinned application dependencies are Streamlit 1.55.0, MySQL Connector/Python 9.5.0, Pandas 2.3.3 and python-dotenv 1.2.1.

### 2. Create the database and configuration

Use a running **Oracle MySQL 8.0.16 or newer** server. MySQL 8.4 is the Docker target. This project is not specified or tested against MariaDB.

For a new training database:

```bash
python scripts/setup.py
```

For a new empty database containing no sample records:

```bash
python scripts/setup.py --empty --database institute_lms --app-user institute_lms_app
```

The setup script refuses to overwrite `.env`, reuse an existing account or alter a database that already contains tables. To avoid a naming conflict, choose a new database and app-account name. Do not delete an existing database to get past that check.

The local account receives only `SELECT`, `INSERT`, `UPDATE` and `DELETE` on the selected database. The application's saved configuration never needs MySQL root privileges.

### 3. Check and launch

```bash
python scripts/doctor.py
python -m streamlit run app.py
```

The checker reads the five tables, verifies the server family/version, checks for the four foreign keys, and compares recorded grade totals with their components. It does not write records or prove every acceptance criterion by itself.

### Alternative: import in MySQL Workbench

Open `lms_database.sql` in Workbench, connect as an administrator, and execute the script once. It creates `lms`, its five related tables, constraints and sample data. It contains no DROP or TRUNCATE statements. Re-importing the sample data into a populated database will raise duplicate-key errors; the script is not a migration or reset tool.

Create an application account separately. Replace the password placeholder with a strong, unique password:

```sql
CREATE USER 'lms_app'@'localhost' IDENTIFIED BY 'replace_with_a_strong_unique_password';
CREATE USER 'lms_app'@'127.0.0.1' IDENTIFIED BY 'replace_with_a_strong_unique_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON lms.* TO 'lms_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON lms.* TO 'lms_app'@'127.0.0.1';
```

Copy `.env.example` to `.env` and enter that account's details. Use `APP_DATA_MODE=sample` for the supplied sample data. The `MYSQL_ROOT_PASSWORD` setting is for Docker only and is unused by the local application. Run the checker and start Streamlit as above. Do not run the interactive setup against this already initialized database.

To create an empty database manually, create/select the database in Workbench and import **only** `database/schema.sql`, not `lms_database.sql`.

## Docker setup

Docker is an alternative to a separately installed local MySQL server. It is not required for the Mac workflow above. The app is exposed only at `127.0.0.1:8501`; the database has no published host port.

For an empty workspace, from a fresh project directory with no `.env`:

```bash
python3 scripts/docker_env.py
docker compose up --build
```

For a sample workspace, again using a fresh configuration and database volume:

```bash
python3 scripts/docker_env.py --sample
docker compose -f compose.yaml -f compose.sample.yaml up --build
```

The credential generator creates two different random passwords. The database initializes before the app starts. Data persists in the `mysql_data` Docker volume. Initialization scripts run only when that volume is first created. Adding the sample overlay to an already initialized volume does not import sample records.

Stop with `docker compose down`. **Do not use `docker compose down -v` on a database you need to keep: it deletes the volume.** Back up important records first. A different project name, for example `docker compose -p institute-live ...`, creates a separate volume for a new workspace.

The official MySQL image's `MYSQL_USER` initialization grants access to its configured database. The local Python setup is more restrictive and grants only CRUD operations. Review and narrow the Docker account's grants before a shared deployment.

## Configuration

| Setting | Purpose |
| --- | --- |
| `DB_HOST`, `DB_PORT` | MySQL host and TCP port |
| `DB_NAME` | Database name; letters, numbers and underscores only, beginning with a letter |
| `DB_USER`, `DB_PASSWORD` | Application account, not root |
| `DB_SSL_CA` | Optional CA certificate path for verified TLS to a remote MySQL server |
| `INSTITUTE_NAME` | Institute name in the interface and policy pages |
| `APP_CURRENCY` | Three-letter display code for course fees |
| `APP_DATA_MODE` | `sample` shows the fictional-record notice; `live` is for your own records |
| `PRIVACY_CONTACT` | A genuine institute contact for the privacy and terms pages |

Changing `APP_DATA_MODE` changes the notice only. It does not remove, convert or verify existing sample records. Start with an empty database for live work instead of relabeling the fictional dataset.

`.env` is excluded from Git and Docker build context. The setup script writes it with owner-only permissions where supported. Do not email it, put it in screenshots or upload it to a public repository.

## Reports and their definitions

**BR-01: Course popularity.** Total enrollment records per course across all statuses, sorted highest first, with separate counts for currently enrolled, completed and dropped. Includes zero-enrollment courses.

**BR-02: Instructor workload.** Course count, active course count and sum of assigned course hours. The `LEFT JOIN` keeps instructors with no assigned courses visible. Assigned hours are course-duration sums, not a weekly timetable.

**BR-03: Student performance.** Sum of recorded totals across courses, graded-course count and average percentage. The sum is the requested primary ranking; students taking more courses can accumulate more marks. Missing grades are excluded. Recorded grades from Dropped enrollments are retained as historical results.

**BR-04: Active students.** Count of student master records with `status = 'Active'`.

**BR-05: Enrollment status.** Counts of Enrolled, Completed and Dropped, including an explicit zero for any status with no records.

**BR-06: Courses without enrollments.** Courses with no enrollment records in any status. A course with only completed or dropped students is not counted here.

The application executes the SQL defined in `lms/reports.py`. The same queries are submitted separately in `database/reports.sql`. SQL training examples covering CRUD and the required concepts are in `database/crud_examples.sql`.

## Validation and safe changes

The application validates required fields, email structure, date ranges, phone format, positive durations, nonnegative fees, permitted statuses and 0-100 marks. MySQL additionally enforces keys, non-null columns, unique email addresses, unique student/course pairs, one grade per enrollment, CHECK constraints and restricted foreign-key deletion.

Delete screens show dependencies, require typing `DELETE` and require a confirmation checkbox. Parent records are never silently cascade-deleted. To remove a complete test workflow, delete its grade, enrollment, student, course and then instructor, in that order.

Updates use a revision number to detect stale edits. When a record changes after you opened it, reload it before saving. CSV exports neutralize text that could otherwise be interpreted as a spreadsheet formula. HTML fragments escape record names and other user-entered text.

## Testing

Run offline tests after installing the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q -m "not integration and not ui"
```

For actual MySQL and Streamlit tests, create a **separate disposable database** named `lms_test`, and a test account with permissions to create and drop its tables. The test fixture drops and recreates only the five core tables in that explicitly configured test database. Never point it at important records.

```bash
export RUN_MYSQL_TESTS=1
export LMS_TEST_HOST=127.0.0.1
export LMS_TEST_DATABASE=lms_test
export LMS_TEST_USER=lms_test
export LMS_TEST_PASSWORD='your_test_database_password'
python -m pytest -q
```

Tests refuse a database name that does not end in `_test`. They never fall back to the application's `DB_PASSWORD`. A GitHub Actions configuration for MySQL 8.4 and Python 3.12 is included in `.github/workflows/tests.yml`, but it has not been executed during this build.

## Screenshots and demonstration

Open `application_preview.html` directly in a browser for a **read-only interface preview**. Navigation, search and report selection work on a snapshot of the supplied fictional records. It does not connect to MySQL, save changes or replace `app.py`.

The images below are screenshots of that HTML preview, not screenshots of a running Streamlit/MySQL session:

![Dashboard design preview](docs/screenshots/preview-dashboard.png)

![Students design preview](docs/screenshots/preview-students.png)

After starting the real application, generate runtime screenshots with:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/capture_screenshots.py
```

Runtime images go into `docs/screenshots/runtime/` so they cannot be confused with the design-preview images. The script refuses to capture a page that shows a database connection error.

Use `docs/DEMO.md` for the end-to-end demonstration. `docs/Coursebook-Demo.pptx` is the short presentation requested by the brief. Its interface image is explicitly identified as a design preview, and its verification slide distinguishes completed offline checks from unexecuted runtime tests.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `python3: command not found` | Install Python 3.11-3.13, reopen Terminal and check `python3 --version` |
| Package installation fails | Check internet access and Python version; run `python -m pip install -r requirements.txt` inside `.venv` |
| `Access denied for user` | Check the app account's password, host grant and database permissions; root's password is not automatically the app password |
| Cannot connect to MySQL | Start the MySQL server; check host, port and `python scripts/doctor.py` |
| Setup refuses existing tables | Choose a new database name, or configure the existing project schema manually; setup intentionally does not overwrite data |
| Duplicate enrollment | Find the existing student/course pair and update its status |
| Delete is blocked | Read the related-record count; remove those dependent records first or keep the record |
| Another operator changed a record | Click Reload selected record, review the changes and save again |
| Port 8501 is in use | Stop the other Streamlit process, or use `python -m streamlit run app.py --server.port=8502` |
| Docker sample data did not appear | Initialization runs only on a new database volume; use a fresh project/volume rather than deleting important data |

## Deployment boundary

The brief lists login and roles as optional extensions; this project does not implement them. By default it is a local mini-project, not a public, multi-user portal. Anyone able to reach the app can administer records.

Before using it beyond a local demonstration, add institute-managed authentication and authorization, HTTPS, tested backups, access logging, appropriate database grants and completed policy details. Review the code and run the real integration tests in the target environment. The policy pages are editable templates, not a substitute for an institute's deployment and privacy decisions.

## Project map

```text
app.py                       Streamlit navigation and shared layout
lms/config.py                Validated environment configuration
lms/db.py                    MySQL transactions and safe error messages
lms/repository.py            CRUD, relational checks and query execution
lms/validation.py            Input validation and field allowlists
lms/reports.py               Six report queries and dashboard queries
lms/export.py                Pandas conversion and protected CSV export
lms/ui.py                    Escaped, reusable visual components
lms/views/                   Dashboard, records, reports and legal screens
assets/                      Styles, logo and favicon files
lms_database.sql             Complete schema plus fictional sample data
database/                    Schema, sample data, reports and SQL exercises
scripts/                     Setup, diagnostics and screenshot capture
tests/                       Offline, real-MySQL and Streamlit tests
docs/                        Requirement map, ERD, policies, test report and demo
application_preview.html     Offline read-only design preview
Dockerfile / compose*.yaml   Optional container setup
```

### API references used

The project follows the official API documentation for [Streamlit multipage navigation](https://docs.streamlit.io/1.55.0/develop/api-reference/navigation/st.page), [Streamlit tables](https://docs.streamlit.io/1.55.0/develop/api-reference/data/st.dataframe), [parameterized Connector/Python execution](https://dev.mysql.com/doc/connectors/en/connector-python-api-mysqlcursor-execute.html), [Connector/Python multi-statement scripts](https://dev.mysql.com/doc/connectors/en/connector-python-multi.html) and [MySQL CHECK constraints](https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html). The supplied client brief remains the source of the application requirements.
