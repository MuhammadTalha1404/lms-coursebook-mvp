"""Short-lived MySQL transactions. Every user-supplied value is bound separately."""
from contextlib import contextmanager
from .config import Settings
from .errors import ConflictError, RelatedRecordsError, StorageError, ValidationError


def mysql_error(errno: int | None, message: str = "") -> Exception:
    if errno == 1062:
        if "uq_students_email" in message:
            return ConflictError("That email already belongs to another student.")
        if "uq_instructors_email" in message:
            return ConflictError("That email already belongs to another instructor.")
        if "uq_enrollments_student_course" in message:
            return ConflictError("This student already has an enrollment for that course. Edit the existing enrollment instead.")
        if "uq_grades_enrollment" in message:
            return ConflictError("Marks already exist for this enrollment. Use Edit grade.")
        return ConflictError("A record with those unique details already exists.")
    if errno == 1451:
        return RelatedRecordsError("This record is still in use. Delete its dependent records first, or keep it and change its status.")
    if errno == 1452:
        return ValidationError("A related record no longer exists. Refresh the page and select it again.")
    if errno in {1048, 1264, 1366, 1406, 3819, 4025}:
        return ValidationError("A value does not meet the database constraints. Check required fields, lengths, marks and status.")
    if errno in {1205, 1213}:
        return ConflictError("Another operation is updating these records. Refresh and try again.")
    if errno in {1045, 1049, 1146, 2002, 2003, 2005, 2006, 2013}:
        return StorageError("MySQL is unavailable or not configured. Check .env, start MySQL and run python scripts/doctor.py.")
    if errno == 1142:
        return StorageError("The database account does not have the required permission. Check the grants in the setup guide.")
    return StorageError("The database operation could not be completed. Run python scripts/doctor.py and check the MySQL server logs.")


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings

    @contextmanager
    def session(self, *, write: bool = False):
        try:
            import mysql.connector
        except ImportError as exc:
            raise StorageError("MySQL Connector/Python is missing. Run python -m pip install -r requirements.txt.") from exc
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**self.settings.connection_args())
            cursor = connection.cursor(dictionary=True, buffered=True)
            yield cursor
            if write:
                connection.commit()
            else:
                connection.rollback()
        except mysql.connector.Error as exc:
            if connection:
                connection.rollback()
            raise mysql_error(exc.errno, str(exc)) from exc
        except BaseException:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        with self.session() as cursor:
            cursor.execute(query, params)
            return list(cursor.fetchall())

    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        with self.session() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def health(self) -> dict:
        result = self.fetch_one("SELECT VERSION() AS server_version, DATABASE() AS database_name, CURRENT_USER() AS account")
        for table in ("students", "instructors", "courses", "enrollments", "grades"):
            self.fetch_one(f"SELECT COUNT(*) AS n FROM {table}")
        return result or {}
