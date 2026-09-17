# Verification report

Build date: 16 September 2026

## Result

**131 offline tests passed. 22 runtime tests were skipped.**

The project source and deliverables are complete, but this build is **not a verified live MySQL/Streamlit deployment**. A running MySQL server, MySQL Connector/Python and Streamlit were unavailable in the build environment. Dependency download attempts failed because network access was blocked. No successful database import, Streamlit server session, Docker build or CI run is claimed.

The runtime application connects only to MySQL. It does not substitute a SQLite database or return sample records when its MySQL connection fails.

## Executed checks

| Check | Result | Scope |
| --- | --- | --- |
| Offline pytest suite | 131 passed | Validation, CRUD service logic, report results, safe HTML/CSV output, configuration and static SQL contracts |
| Python syntax compilation | Passed | `app.py`, `lms/`, `scripts/`, `tests/` |
| Shell syntax | Passed | `run.sh`, `start.command` |
| Preview browser navigation | Passed | All nine pages in the separate read-only HTML preview |
| Preview report selection | Passed | BR-01 through BR-06 |
| Preview search and filter | Passed | Student name search returns one matching sample record; Inactive filter returns two |
| Preview CSV download | Passed | Browser download of displayed BR-01 sample results |
| Preview mobile layout | Passed | 390-pixel viewport; no horizontal document overflow; wide tables scroll inside their own containers |
| Browser script errors | None during the checks | The standalone HTML preview only |
| Presentation | Passed | Six slides rendered; all XML parts parsed; overlap checks clean; no slide overflow detected |

The browser preview was rendered from its own HTML content in Chromium through Playwright. Desktop and mobile images are in `docs/screenshots/`. These are **design-preview screenshots, not live Streamlit screenshots**. Presentation slides were rendered with LibreOffice and inspected.

### Offline environment

Python 3.13.5, pytest 9.0.2, Pandas 2.2.3 and python-dotenv 1.2.2 were available. The project's runtime requirements pin Pandas 2.3.3 and python-dotenv 1.2.1; those exact pinned versions were not installed here. Playwright 1.57.0 and system Chromium were used for the read-only preview checks.

Offline repository tests use `tests/sqlite_adapter.py`, an explicitly test-only adapter with a separate SQLite schema. It translates query placeholders and removes MySQL row-lock clauses. It checks service behavior and expected relational results; it does **not** validate MySQL's parser, locking behavior, collation, privilege model or connector behavior.

The sample SQL produced these results in that test adapter: 12 students, 4 instructors, 6 courses, 18 enrollments and 10 grade records. Ten students are Active. Enrollment states are 11 Enrolled, 5 Completed and 2 Dropped. These are counts of the supplied fictional training records, not institute performance claims.

## Included runtime checks not executed here

| Test group | Count | What it is intended to check |
| --- | --- | --- |
| MySQL integration | 12 | Actual schema/sample import, required report queries, duplicate enrollment prevention, safe lifecycle operations, range constraints and restricted deletion |
| Streamlit runtime | 10 | Nine page-render checks and a student form submission persisted in MySQL |

These tests are opt-in. Set `RUN_MYSQL_TESTS=1` and all required `LMS_TEST_*` credentials for a **separate disposable database ending in `_test`**. They drop and recreate the five core tables in that dedicated test database. Do not use an important database.

The workflow in `.github/workflows/tests.yml` defines a MySQL 8.4 service and a Python 3.12 test job. It is supplied as configuration only; it was not run during this build.

## Reproduce the tests

After installing the development dependencies:

```bash
python -m pytest -q -m "not integration and not ui"
```

For the actual MySQL and Streamlit tests, first create a disposable `lms_test` database and an account with permission to create and drop its tables, then run:

```bash
export RUN_MYSQL_TESTS=1
export LMS_TEST_HOST=127.0.0.1
export LMS_TEST_DATABASE=lms_test
export LMS_TEST_USER=lms_test
export LMS_TEST_PASSWORD='your_test_database_password'
python -m pytest -q
```

`LMS_TEST_PORT` can also be set for a nonstandard port. There is no fallback to the application's saved `DB_PASSWORD`.

## Local acceptance checklist

Before presenting the app as runtime-verified, complete this sequence on the target computer:

1. Install the pinned dependencies and import the submitted schema into a fresh MySQL database.
2. Run `python scripts/doctor.py` and resolve any connection, table, foreign-key or generated-total errors.
3. Start the app, visit every page through the main sidebar, and verify the Terms & Conditions, privacy policy and browser favicon.
4. Run the end-to-end create, view, update and delete demonstration in `docs/DEMO.md` for all five entities.
5. Confirm that duplicate emails, duplicate enrollments, invalid marks and deletion of referenced records receive clear error messages.
6. Confirm that the dashboard and all six reports change after actual database writes, and that CSV exports match the displayed filters.
7. Use two browser sessions to verify that saving a stale edit is rejected and requires a reload.
8. Run the opt-in MySQL and Streamlit tests against the separate test database and save their real output.
9. Capture actual runtime screenshots with `python scripts/capture_screenshots.py` after installing Playwright's browser.

Public deployment requires additional work beyond the mini-project brief: authentication, authorization, HTTPS, backups and institute-specific policy review. Keep the default application on localhost until that work is complete.
