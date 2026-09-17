"""TEST DOUBLE ONLY. The shipped application never imports or uses SQLite.

This adapter verifies Python CRUD logic, query results, validation and rollback
without requiring network access. It does NOT validate MySQL's parser, locking,
collations, server CHECK enforcement, or the Streamlit runtime.
"""
from contextlib import contextmanager
from datetime import date,datetime
from decimal import Decimal
from pathlib import Path
import sqlite3
from lms.db import mysql_error

ROOT=Path(__file__).resolve().parents[1]
sqlite3.register_adapter(Decimal,str)
sqlite3.register_adapter(date,date.isoformat)
sqlite3.register_adapter(datetime,datetime.isoformat)
sqlite3.register_converter("DATE",lambda value:date.fromisoformat(value.decode()))

SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL CHECK(length(trim(full_name))>=2), email TEXT COLLATE NOCASE NOT NULL UNIQUE, phone TEXT NOT NULL DEFAULT '', enrollment_date DATE NOT NULL, status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Inactive')), version INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE instructors (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, specialization TEXT NOT NULL, email TEXT COLLATE NOCASE NOT NULL UNIQUE, status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Inactive')), version INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE courses (id INTEGER PRIMARY KEY AUTOINCREMENT, course_name TEXT NOT NULL, description TEXT NOT NULL, instructor_id INTEGER NOT NULL REFERENCES instructors(id) ON DELETE RESTRICT, duration_hours INTEGER NOT NULL CHECK(duration_hours BETWEEN 1 AND 10000), fee NUMERIC NOT NULL CHECK(fee>=0), status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Inactive')), version INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE RESTRICT, course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT, enrollment_date DATE NOT NULL, status TEXT NOT NULL DEFAULT 'Enrolled' CHECK(status IN ('Enrolled','Completed','Dropped')), version INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(student_id,course_id));
CREATE TABLE grades (id INTEGER PRIMARY KEY AUTOINCREMENT, enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollments(id) ON DELETE RESTRICT, assignment_marks NUMERIC NOT NULL CHECK(assignment_marks BETWEEN 0 AND 100), quiz_marks NUMERIC NOT NULL CHECK(quiz_marks BETWEEN 0 AND 100), final_exam_marks NUMERIC NOT NULL CHECK(final_exam_marks BETWEEN 0 AND 100), total_marks NUMERIC GENERATED ALWAYS AS (assignment_marks+quiz_marks+final_exam_marks) STORED, version INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


class Cursor:
    def __init__(self,cursor):
        self.cursor=cursor

    def execute(self,query,params=()):
        query=query.replace("%s","?").replace(" FOR UPDATE","")
        try:
            self.cursor.execute(query,params)
        except sqlite3.IntegrityError as exc:
            message=str(exc)
            if "UNIQUE" in message:
                key=""
                for signature,constraint in (("students.email","uq_students_email"),("instructors.email","uq_instructors_email"),("enrollments.student_id","uq_enrollments_student_course"),("grades.enrollment_id","uq_grades_enrollment")):
                    if signature in message: key=constraint
                raise mysql_error(1062,key) from exc
            if "FOREIGN KEY" in message:
                raise mysql_error(1451 if query.lstrip().upper().startswith("DELETE") else 1452) from exc
            raise mysql_error(3819,message) from exc
        return self

    def fetchone(self):
        row=self.cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(row) for row in self.cursor.fetchall()]

    @property
    def lastrowid(self): return self.cursor.lastrowid
    @property
    def rowcount(self): return self.cursor.rowcount


class SQLiteTestDatabase:
    def __init__(self,seed=False):
        self.connection=sqlite3.connect(":memory:",detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory=sqlite3.Row
        self.connection.executescript(SCHEMA)
        if seed:
            sql=(ROOT/"database/sample_data.sql").read_text().replace("START TRANSACTION;","BEGIN TRANSACTION;")
            self.connection.executescript(sql)

    @contextmanager
    def session(self,*,write=False):
        cursor=self.connection.cursor()
        try:
            yield Cursor(cursor)
            if write: self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def fetch_all(self,query,params=()):
        with self.session() as cursor:
            cursor.execute(query,params)
            return cursor.fetchall()

    def fetch_one(self,query,params=()):
        with self.session() as cursor:
            cursor.execute(query,params)
            return cursor.fetchone()

    def close(self): self.connection.close()
