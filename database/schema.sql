-- Coursebook core schema. Requires MySQL 8.0.16+; MySQL 8.4 is recommended.
-- Execute inside the intended database. No DROP, TRUNCATE or cascading deletes.
SET NAMES utf8mb4;
SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,ONLY_FULL_GROUP_BY';

CREATE TABLE IF NOT EXISTS students (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(32) NOT NULL DEFAULT '',
    enrollment_date DATE NOT NULL,
    status VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL DEFAULT 'Active',
    version INT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_students_email UNIQUE (email),
    CONSTRAINT ck_students_name CHECK (CHAR_LENGTH(TRIM(full_name)) >= 2),
    CONSTRAINT ck_students_email CHECK (LOCATE('@', email) > 1),
    CONSTRAINT ck_students_status CHECK (status IN ('Active', 'Inactive')),
    CONSTRAINT ck_students_version CHECK (version > 0),
    INDEX idx_students_name (full_name),
    INDEX idx_students_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS instructors (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    specialization VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL,
    status VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL DEFAULT 'Active',
    version INT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_instructors_email UNIQUE (email),
    CONSTRAINT ck_instructors_name CHECK (CHAR_LENGTH(TRIM(full_name)) >= 2),
    CONSTRAINT ck_instructors_specialization CHECK (CHAR_LENGTH(TRIM(specialization)) >= 2),
    CONSTRAINT ck_instructors_email CHECK (LOCATE('@', email) > 1),
    CONSTRAINT ck_instructors_status CHECK (status IN ('Active', 'Inactive')),
    CONSTRAINT ck_instructors_version CHECK (version > 0),
    INDEX idx_instructors_name (full_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS courses (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    instructor_id INT UNSIGNED NOT NULL,
    duration_hours SMALLINT UNSIGNED NOT NULL,
    fee DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL DEFAULT 'Active',
    version INT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_courses_instructor FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_courses_name CHECK (CHAR_LENGTH(TRIM(course_name)) >= 2),
    CONSTRAINT ck_courses_duration CHECK (duration_hours BETWEEN 1 AND 10000),
    CONSTRAINT ck_courses_fee CHECK (fee >= 0),
    CONSTRAINT ck_courses_status CHECK (status IN ('Active', 'Inactive')),
    CONSTRAINT ck_courses_version CHECK (version > 0),
    INDEX idx_courses_name (course_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS enrollments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    student_id INT UNSIGNED NOT NULL,
    course_id INT UNSIGNED NOT NULL,
    enrollment_date DATE NOT NULL,
    status VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL DEFAULT 'Enrolled',
    version INT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT uq_enrollments_student_course UNIQUE (student_id, course_id),
    CONSTRAINT ck_enrollments_status CHECK (status IN ('Enrolled', 'Completed', 'Dropped')),
    CONSTRAINT ck_enrollments_version CHECK (version > 0),
    INDEX idx_enrollments_status (status),
    INDEX idx_enrollments_date (enrollment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS grades (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT UNSIGNED NOT NULL,
    assignment_marks DECIMAL(5,2) NOT NULL,
    quiz_marks DECIMAL(5,2) NOT NULL,
    final_exam_marks DECIMAL(5,2) NOT NULL,
    total_marks DECIMAL(6,2) GENERATED ALWAYS AS (assignment_marks + quiz_marks + final_exam_marks) STORED,
    version INT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_grades_enrollment FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT uq_grades_enrollment UNIQUE (enrollment_id),
    CONSTRAINT ck_grades_assignment CHECK (assignment_marks BETWEEN 0 AND 100),
    CONSTRAINT ck_grades_quiz CHECK (quiz_marks BETWEEN 0 AND 100),
    CONSTRAINT ck_grades_final CHECK (final_exam_marks BETWEEN 0 AND 100),
    CONSTRAINT ck_grades_version CHECK (version > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
