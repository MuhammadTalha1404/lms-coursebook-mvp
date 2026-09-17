-- Coursebook: six required management reports.
-- Select your database in MySQL Workbench before running.

-- BR-01: Course popularity
-- Ranked by all enrollment records, including Completed and Dropped. Current enrollment counts are shown separately.
SELECT c.id AS course_id, c.course_name,
       COUNT(e.id) AS total_enrollments,
       SUM(CASE WHEN e.status = 'Enrolled' THEN 1 ELSE 0 END) AS currently_enrolled,
       SUM(CASE WHEN e.status = 'Completed' THEN 1 ELSE 0 END) AS completed,
       SUM(CASE WHEN e.status = 'Dropped' THEN 1 ELSE 0 END) AS dropped
FROM courses AS c
LEFT JOIN enrollments AS e ON e.course_id = c.id
GROUP BY c.id, c.course_name
ORDER BY total_enrollments DESC, c.course_name ASC;

-- BR-02: Instructor workload
-- All assigned courses, including inactive courses. Instructors with no courses remain visible.
SELECT i.id AS instructor_id, i.full_name AS instructor_name, i.specialization,
       COUNT(c.id) AS course_count,
       SUM(CASE WHEN c.status = 'Active' THEN 1 ELSE 0 END) AS active_courses,
       COALESCE(SUM(c.duration_hours), 0) AS assigned_hours
FROM instructors AS i
LEFT JOIN courses AS c ON c.instructor_id = i.id
GROUP BY i.id, i.full_name, i.specialization
ORDER BY course_count DESC, i.full_name ASC;

-- BR-03: Student performance
-- Ranked by the sum of recorded totals across courses. Each course is out of 300. Average percentage allows comparison across different course counts. Missing grades are excluded, not treated as zero. Recorded grades on Dropped enrollments remain historical results.
SELECT s.id AS student_id, s.full_name AS student_name,
       COUNT(g.id) AS graded_courses,
       SUM(g.total_marks) AS total_marks,
       ROUND(AVG(g.total_marks) / 3, 2) AS average_percentage
FROM students AS s
INNER JOIN enrollments AS e ON e.student_id = s.id
INNER JOIN grades AS g ON g.enrollment_id = e.id
GROUP BY s.id, s.full_name
ORDER BY total_marks DESC, average_percentage DESC, s.full_name ASC;

-- BR-04: Active students
-- Students whose current status is Active. This count is independent of their enrollment status.
SELECT COUNT(*) AS active_students
FROM students
WHERE status = 'Active';

-- BR-05: Enrollment status
-- Every enrollment is counted once. All three statuses remain visible even when their count is zero.
SELECT statuses.status, COUNT(e.id) AS enrollment_count
FROM (
    SELECT 'Enrolled' AS status, 1 AS sort_order
    UNION ALL SELECT 'Completed', 2
    UNION ALL SELECT 'Dropped', 3
) AS statuses
LEFT JOIN enrollments AS e ON e.status = statuses.status
GROUP BY statuses.status, statuses.sort_order
ORDER BY statuses.sort_order;

-- BR-06: Courses without enrollments
-- Courses with no enrollment records in any status. A course with only Completed or Dropped records is not included.
SELECT c.id AS course_id, c.course_name, i.full_name AS instructor_name, c.status
FROM courses AS c
INNER JOIN instructors AS i ON i.id = c.instructor_id
LEFT JOIN enrollments AS e ON e.course_id = c.id
WHERE e.id IS NULL
ORDER BY c.course_name ASC;
