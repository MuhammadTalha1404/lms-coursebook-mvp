"""All CRUD and reporting operations, independent of Streamlit.

Identifiers come only from allowlists. Operators' search, IDs and form values
are always supplied through the connector's %s parameters.
"""
from .errors import ValidationError, ConflictError, NotFoundError, RelatedRecordsError
from .validation import FIELDS, validate_record, positive_int, like_pattern
from .reports import REPORT_BY_ID, SUMMARY_SQL, RECENT_SQL

LIST_SPECS = {
    "students": ("SELECT s.* FROM students s", ("s.full_name", "s.email", "s.phone"), "s.full_name, s.id", "s.status"),
    "instructors": ("SELECT i.* FROM instructors i", ("i.full_name", "i.email", "i.specialization"), "i.full_name, i.id", "i.status"),
    "courses": ("SELECT c.*, i.full_name AS instructor_name FROM courses c INNER JOIN instructors i ON i.id=c.instructor_id", ("c.course_name", "c.description", "i.full_name"), "c.course_name, c.id", "c.status"),
    "enrollments": ("SELECT e.*, s.full_name AS student_name, c.course_name FROM enrollments e INNER JOIN students s ON s.id=e.student_id INNER JOIN courses c ON c.id=e.course_id", ("s.full_name", "c.course_name"), "e.enrollment_date DESC, e.id DESC", "e.status"),
    "grades": ("SELECT g.*, s.full_name AS student_name, c.course_name, e.status AS enrollment_status, ROUND(g.total_marks/3,2) AS percentage FROM grades g INNER JOIN enrollments e ON e.id=g.enrollment_id INNER JOIN students s ON s.id=e.student_id INNER JOIN courses c ON c.id=e.course_id", ("s.full_name", "c.course_name"), "g.updated_at DESC, g.id DESC", "e.status"),
}
DEPENDENCIES = {
    "students": (("enrollments", "student_id"),),
    "instructors": (("courses", "instructor_id"),),
    "courses": (("enrollments", "course_id"),),
    "enrollments": (("grades", "enrollment_id"),),
    "grades": (),
}


class Repository:
    def __init__(self, database):
        self.db = database

    def _entity(self, entity: str) -> str:
        if entity not in FIELDS:
            raise ValidationError("Unknown record type.")
        return entity

    def list_records(self, entity: str, search: str = "", status: str | None = None) -> list[dict]:
        query, search_fields, ordering, status_column = LIST_SPECS[self._entity(entity)]
        clauses, params = [], []
        if search.strip():
            pattern = like_pattern(search)
            clauses.append("(" + " OR ".join(f"{field} LIKE %s ESCAPE '!'" for field in search_fields) + ")")
            params.extend([pattern] * len(search_fields))
        if status:
            clauses.append(f"{status_column} = %s")
            params.append(status)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        return self.db.fetch_all(query + " ORDER BY " + ordering, tuple(params))

    def get(self, entity: str, record_id: int) -> dict:
        entity = self._entity(entity)
        record_id = positive_int(record_id, "Record ID")
        row = self.db.fetch_one(f"SELECT * FROM {entity} WHERE id = %s", (record_id,))
        if not row:
            raise NotFoundError("This record no longer exists. Refresh the page.")
        return row

    def _links(self, cursor, entity: str, clean: dict, old: dict | None = None) -> None:
        if entity == "courses":
            cursor.execute("SELECT id FROM instructors WHERE id = %s FOR UPDATE", (clean["instructor_id"],))
            if not cursor.fetchone():
                raise ValidationError("Select an existing instructor.")
        elif entity == "enrollments":
            cursor.execute("SELECT enrollment_date FROM students WHERE id = %s FOR UPDATE", (clean["student_id"],))
            student = cursor.fetchone()
            if not student:
                raise ValidationError("Select an existing student.")
            if str(clean["enrollment_date"]) < str(student["enrollment_date"]):
                raise ValidationError("A course enrollment cannot predate the student's institute enrollment date.")
            cursor.execute("SELECT id FROM courses WHERE id = %s FOR UPDATE", (clean["course_id"],))
            if not cursor.fetchone():
                raise ValidationError("Select an existing course.")
            if old and (old["student_id"] != clean["student_id"] or old["course_id"] != clean["course_id"]):
                cursor.execute("SELECT id FROM grades WHERE enrollment_id = %s", (old["id"],))
                if cursor.fetchone():
                    raise ValidationError("This enrollment has grades. Delete its grade record before changing the student or course.")
        elif entity == "grades":
            cursor.execute("SELECT id FROM enrollments WHERE id = %s FOR UPDATE", (clean["enrollment_id"],))
            if not cursor.fetchone():
                raise ValidationError("Select an existing enrollment.")
        elif entity == "students" and old:
            cursor.execute("SELECT MIN(enrollment_date) AS first_date FROM enrollments WHERE student_id = %s", (old["id"],))
            first_date = cursor.fetchone()["first_date"]
            if first_date and str(clean["enrollment_date"]) > str(first_date):
                raise ValidationError("The institute enrollment date cannot be later than this student's earliest course enrollment.")

    def create(self, entity: str, values: dict) -> int:
        entity = self._entity(entity)
        clean = validate_record(entity, values)
        columns = FIELDS[entity]
        query = f"INSERT INTO {entity} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        with self.db.session(write=True) as cursor:
            self._links(cursor, entity, clean)
            cursor.execute(query, tuple(clean[column] for column in columns))
            return int(cursor.lastrowid)

    def update(self, entity: str, record_id: int, version: int, values: dict) -> None:
        entity = self._entity(entity)
        record_id = positive_int(record_id, "Record ID")
        version = positive_int(version, "Version")
        clean = validate_record(entity, values)
        columns = FIELDS[entity]
        with self.db.session(write=True) as cursor:
            cursor.execute(f"SELECT * FROM {entity} WHERE id = %s FOR UPDATE", (record_id,))
            old = cursor.fetchone()
            if not old:
                raise NotFoundError("This record was deleted by another operator. Refresh the page.")
            if old["version"] != version:
                raise ConflictError("This record changed after you opened it. Reload the record before saving again.")
            self._links(cursor, entity, clean, old)
            assignments = ", ".join(f"{column} = %s" for column in columns)
            cursor.execute(f"UPDATE {entity} SET {assignments}, version = version + 1 WHERE id = %s AND version = %s",
                           tuple(clean[column] for column in columns) + (record_id, version))
            if cursor.rowcount != 1:
                raise ConflictError("This record changed. Reload it before trying again.")

    def dependencies(self, entity: str, record_id: int) -> dict[str, int]:
        entity = self._entity(entity)
        record_id = positive_int(record_id, "Record ID")
        return {table: int(self.db.fetch_one(f"SELECT COUNT(*) AS n FROM {table} WHERE {column} = %s", (record_id,))["n"])
                for table, column in DEPENDENCIES[entity]}

    def delete(self, entity: str, record_id: int, version: int) -> None:
        entity = self._entity(entity)
        record_id = positive_int(record_id, "Record ID")
        version = positive_int(version, "Version")
        with self.db.session(write=True) as cursor:
            cursor.execute(f"SELECT version FROM {entity} WHERE id = %s FOR UPDATE", (record_id,))
            old = cursor.fetchone()
            if not old:
                raise NotFoundError("This record has already been deleted.")
            if old["version"] != version:
                raise ConflictError("This record changed after you selected it. Reload before deleting.")
            for table, column in DEPENDENCIES[entity]:
                cursor.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE {column} = %s", (record_id,))
                count = int(cursor.fetchone()["n"])
                if count:
                    raise RelatedRecordsError(f"Cannot delete this record: {count} related {table} still exist. Delete those records first.")
            cursor.execute(f"DELETE FROM {entity} WHERE id = %s AND version = %s", (record_id, version))
            if cursor.rowcount != 1:
                raise ConflictError("This record changed. Reload before deleting.")

    def student_history(self, student_id: int) -> list[dict]:
        return self.db.fetch_all("""
SELECT e.id, c.course_name, e.enrollment_date, e.status,
       g.assignment_marks, g.quiz_marks, g.final_exam_marks, g.total_marks
FROM enrollments e INNER JOIN courses c ON c.id = e.course_id
LEFT JOIN grades g ON g.enrollment_id = e.id
WHERE e.student_id = %s
ORDER BY e.enrollment_date DESC, e.id DESC
""", (positive_int(student_id, "Student"),))

    def report(self, report_id: str) -> list[dict]:
        if report_id not in REPORT_BY_ID:
            raise ValidationError("Unknown report.")
        return self.db.fetch_all(REPORT_BY_ID[report_id].sql)

    def summary(self) -> dict:
        return self.db.fetch_one(SUMMARY_SQL) or {}

    def recent_enrollments(self, limit: int = 6) -> list[dict]:
        return self.db.fetch_all(RECENT_SQL, (positive_int(limit, "Row limit", 100),))
