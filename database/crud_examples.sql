-- SQL assessment walkthrough. Select the LMS database before executing.
-- New fictional records are created, changed and deleted inside one transaction.
-- ROLLBACK at the end leaves existing records unchanged.
-- Do not run this concurrently with a demonstration using the same email values.
START TRANSACTION;

-- INSERT and primary-key identity.
INSERT INTO instructors (full_name,specialization,email,status)
VALUES ('SQL Demo Instructor','Relational databases','sql.demo.teacher@example.test','Active');
SET @instructor_id = LAST_INSERT_ID();

INSERT INTO courses (course_name,description,instructor_id,duration_hours,fee,status)
VALUES ('SQL Demo Course','Temporary SQL demonstration record',@instructor_id,12,1500.00,'Active');
SET @course_id = LAST_INSERT_ID();

INSERT INTO students (full_name,email,phone,enrollment_date,status)
VALUES ('SQL Demo Student','sql.demo.student@example.test','',CURRENT_DATE(),'Active');
SET @student_id = LAST_INSERT_ID();

INSERT INTO enrollments (student_id,course_id,enrollment_date,status)
VALUES (@student_id,@course_id,CURRENT_DATE(),'Enrolled');
SET @enrollment_id = LAST_INSERT_ID();

INSERT INTO grades (enrollment_id,assignment_marks,quiz_marks,final_exam_marks)
VALUES (@enrollment_id,82,88,91);
SET @grade_id = LAST_INSERT_ID();

-- SELECT, WHERE, LIKE and ORDER BY.
SELECT id,full_name,email FROM students
WHERE status='Active' AND full_name LIKE '%Demo%'
ORDER BY full_name ASC;

-- Multi-table INNER JOIN, aliases and a calculated field.
SELECT s.full_name AS student,c.course_name AS course,
       g.assignment_marks,g.quiz_marks,g.final_exam_marks,g.total_marks,
       ROUND(g.total_marks/3,2) AS percentage
FROM students AS s
INNER JOIN enrollments AS e ON e.student_id=s.id
INNER JOIN courses AS c ON c.id=e.course_id
INNER JOIN grades AS g ON g.enrollment_id=e.id
WHERE e.id=@enrollment_id;

-- GROUP BY, COUNT and SUM. No payment or revenue claim is made.
SELECT s.id,s.full_name,COUNT(g.id) AS graded_courses,
       SUM(g.total_marks) AS total_recorded_marks
FROM students AS s
INNER JOIN enrollments AS e ON e.student_id=s.id
INNER JOIN grades AS g ON g.enrollment_id=e.id
GROUP BY s.id,s.full_name
ORDER BY total_recorded_marks DESC;

-- LEFT JOIN retains courses without any enrollment.
SELECT c.id,c.course_name,COUNT(e.id) AS enrollment_count
FROM courses AS c
LEFT JOIN enrollments AS e ON e.course_id=c.id
GROUP BY c.id,c.course_name
ORDER BY enrollment_count DESC;

-- UPDATE and the application's revision convention.
UPDATE students SET phone='+92 300 1234567',version=version+1 WHERE id=@student_id;
UPDATE instructors SET specialization='MySQL and SQL',version=version+1 WHERE id=@instructor_id;
UPDATE courses SET duration_hours=18,version=version+1 WHERE id=@course_id;
UPDATE enrollments SET status='Completed',version=version+1 WHERE id=@enrollment_id;
UPDATE grades SET final_exam_marks=95,version=version+1 WHERE id=@grade_id;
SELECT assignment_marks,quiz_marks,final_exam_marks,total_marks FROM grades WHERE id=@grade_id;

-- DELETE in dependency order. Foreign keys prevent unsafe parent deletion.
DELETE FROM grades WHERE id=@grade_id;
DELETE FROM enrollments WHERE id=@enrollment_id;
DELETE FROM students WHERE id=@student_id;
DELETE FROM courses WHERE id=@course_id;
DELETE FROM instructors WHERE id=@instructor_id;

ROLLBACK;

-- CREATE TABLE and all named keys/constraints are in lms_database.sql.
-- The six client report queries are in database/reports.sql.
