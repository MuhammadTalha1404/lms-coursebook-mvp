import os
from pathlib import Path
import pytest
from lms.config import Settings,identifier
from lms.db import Database
from lms.repository import Repository
from .sqlite_adapter import SQLiteTestDatabase

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def empty_repo():
    db=SQLiteTestDatabase()
    yield Repository(db)
    db.close()

@pytest.fixture
def repo():
    db=SQLiteTestDatabase(seed=True)
    yield Repository(db)
    db.close()

@pytest.fixture
def mysql_settings():
    if os.getenv("RUN_MYSQL_TESTS")!="1":
        pytest.skip("Real MySQL tests are opt-in: set RUN_MYSQL_TESTS=1 and LMS_TEST_* credentials.")
    database=identifier(os.getenv("LMS_TEST_DATABASE","lms_test"))
    if not database.endswith("_test"):
        pytest.fail("Refusing to modify a database whose name does not end in _test.")
    password=os.getenv("LMS_TEST_PASSWORD")
    if not password:
        pytest.fail("LMS_TEST_PASSWORD is required; production DB_PASSWORD is never used by these tests.")
    pytest.importorskip("mysql.connector")
    return Settings(host=os.getenv("LMS_TEST_HOST","127.0.0.1"),port=int(os.getenv("LMS_TEST_PORT","3306")),database=database,user=os.getenv("LMS_TEST_USER","lms_test"),password=password)

@pytest.fixture
def mysql_repo(mysql_settings):
    import mysql.connector
    from scripts.sql_utils import execute_script
    with mysql.connector.connect(**mysql_settings.connection_args()) as connection:
        with connection.cursor() as cursor:
            for table in ("grades","enrollments","courses","instructors","students"):
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
        execute_script(connection,ROOT/"database/schema.sql")
        execute_script(connection,ROOT/"database/sample_data.sql")
    return Repository(Database(mysql_settings))
