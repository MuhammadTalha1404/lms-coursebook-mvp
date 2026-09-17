# Coursebook LMS Presentation Outline

## Slide 1: Coursebook LMS

**Learning Management System**

MySQL + Python + Streamlit + Pandas

A centralized academic administration system for students, instructors, courses, enrollments, grades and management reporting.

## Slide 2: Problem and Solution

The institute needs to replace spreadsheet-based academic management with one relational system.

Coursebook provides:

- Centralized student, instructor and course records
- Course enrollment tracking
- Assessment and grade management
- Live dashboard KPIs
- Six SQL-driven management reports
- Validation and relational database constraints

## Slide 3: Database Design

Five core MySQL tables:

- `students`
- `instructors`
- `courses`
- `enrollments`
- `grades`

Key relationships:

- One instructor can teach many courses
- Students and courses have a many-to-many relationship resolved by enrollments
- One enrollment can have one grade record
- `UNIQUE(student_id, course_id)` prevents duplicate enrollments

## Slide 4: Application Flow

```text
User
  ↓
Streamlit UI
  ↓
Validation
  ↓
Repository / CRUD logic
  ↓
MySQL Connector
  ↓
MySQL database
```

The `.env` file supplies database configuration through `lms/config.py`. The actual MySQL connection is created in `lms/db.py` using MySQL Connector/Python.

## Slide 5: Dashboard and Reports

The dashboard reads live values from MySQL and displays:

- Student count
- Instructor count
- Course count
- Enrollment count
- Course popularity visualization
- Enrollment status visualization
- Recent enrollments

Required reports BR-01 through BR-06 demonstrate JOIN, LEFT JOIN, COUNT, GROUP BY, SUM, calculated fields and ordering.

## Slide 6: CRUD and Validation

All five core entities support create, read, update and delete operations.

Important safeguards include:

- Unique student and instructor emails
- Duplicate enrollment prevention
- Marks restricted to 0 to 100
- Foreign-key protection
- Parameterized SQL queries
- Confirmation before destructive actions
- Transaction commit and rollback

## Slide 7: Grade Relationship

Grades are linked to an **enrollment**, not directly to a student.

Example:

```text
Talha | Project Management | enrollment_id 12
Talha | Software Testing   | enrollment_id 19
```

Selecting the Project Management enrollment stores its grade against enrollment 12. This ensures the system always knows which student's course the marks belong to.

## Slide 8: Conclusion

Coursebook demonstrates a maintainable MySQL + Python + Streamlit solution that meets the LMS mini-project requirements while keeping database structure, application logic and user interface clearly separated.

For the live demo, follow `docs/DEMO.md`.
