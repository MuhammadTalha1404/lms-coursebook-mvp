-- Coursebook LMS: complete assessment deliverable.
-- Creates five related tables and clearly fictional sample records.
-- Import once. This script never drops existing data.
CREATE DATABASE IF NOT EXISTS lms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lms;

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

-- FICTIONAL TRAINING DATA. Every person and address below is an example.
-- Load once into an empty schema. The app must use APP_DATA_MODE=sample.
START TRANSACTION;
INSERT INTO instructors (id,full_name,specialization,email,status) VALUES
(1,'Sara Malik','Data and databases','sara.malik@example.test','Active'),
(2,'Omar Shah','Software development','omar.shah@example.test','Active'),
(3,'Hina Abbas','Product and delivery','hina.abbas@example.test','Active'),
(4,'Bilal Noor','Business analysis','bilal.noor@example.test','Inactive');

INSERT INTO students (id,full_name,email,phone,enrollment_date,status) VALUES
(1,'Amina Khan','amina.khan@example.test','','2026-06-01','Active'),
(2,'Hamza Ali','hamza.ali@example.test','','2026-06-02','Active'),
(3,'Zoya Ahmed','zoya.ahmed@example.test','','2026-06-03','Active'),
(4,'Usman Rafiq','usman.rafiq@example.test','','2026-06-05','Active'),
(5,'Maryam Asif','maryam.asif@example.test','','2026-06-08','Active'),
(6,'Daniyal Hassan','daniyal.hassan@example.test','','2026-06-10','Active'),
(7,'Noor Fatima','noor.fatima@example.test','','2026-06-12','Active'),
(8,'Haris Iqbal','haris.iqbal@example.test','','2026-07-01','Active'),
(9,'Sana Tariq','sana.tariq@example.test','','2026-07-03','Active'),
(10,'Ali Raza','ali.raza@example.test','','2026-07-06','Inactive'),
(11,'Iqra Javed','iqra.javed@example.test','','2026-08-10','Active'),
(12,'Saad Farooq','saad.farooq@example.test','','2026-08-12','Inactive');

INSERT INTO courses (id,course_name,description,instructor_id,duration_hours,fee,status) VALUES
(1,'Database Foundations','Relational design, MySQL queries and practical database work.',1,36,18000.00,'Active'),
(2,'Python for Data','Python fundamentals, Pandas and structured data processing.',1,48,24000.00,'Active'),
(3,'Web Development','Build accessible interfaces and connect them to application services.',2,60,30000.00,'Active'),
(4,'Project Management','Scope, planning, delivery tracking and stakeholder communication.',3,30,16000.00,'Active'),
(5,'Software Testing','Test design, defect reporting and repeatable quality checks.',2,24,14000.00,'Active'),
(6,'Business Analysis','Requirements discovery and process documentation.',4,24,15000.00,'Inactive');

INSERT INTO enrollments (id,student_id,course_id,enrollment_date,status) VALUES
(1,1,1,'2026-06-15','Completed'),
(2,2,1,'2026-06-15','Completed'),
(3,3,1,'2026-07-02','Enrolled'),
(4,4,1,'2026-07-02','Enrolled'),
(5,5,1,'2026-07-03','Enrolled'),
(6,1,2,'2026-07-10','Enrolled'),
(7,6,2,'2026-07-10','Enrolled'),
(8,7,2,'2026-07-12','Completed'),
(9,8,2,'2026-08-01','Enrolled'),
(10,2,3,'2026-07-15','Completed'),
(11,3,3,'2026-07-16','Enrolled'),
(12,9,3,'2026-08-03','Enrolled'),
(13,4,4,'2026-08-05','Completed'),
(14,5,4,'2026-08-05','Enrolled'),
(15,11,4,'2026-08-15','Enrolled'),
(16,6,5,'2026-08-10','Enrolled'),
(17,10,5,'2026-08-11','Dropped'),
(18,12,5,'2026-08-20','Dropped');

INSERT INTO grades (enrollment_id,assignment_marks,quiz_marks,final_exam_marks) VALUES
(1,91,88,94),(2,83,80,86),(3,88,90,89),(4,72,78,80),
(6,90,92,87),(7,76,82,79),(8,95,93,96),(10,86,89,90),
(13,81,84,88),(16,85,79,87);
COMMIT;
