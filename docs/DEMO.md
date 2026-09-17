# End-to-end demonstration

Allow roughly seven minutes. Start the real application and verify the connection with `python scripts/doctor.py` beforehand. Do not use the static preview to claim a live-database demonstration.

## Opening: scope and database

Explain that the institute previously maintained separate spreadsheets. Coursebook puts students, instructors, courses, enrollments and marks in five related MySQL tables. Show the seven required navigation entries. Point out the sample-data banner if using the supplied fictional dataset.

Open MySQL Workbench and run `SHOW TABLES;`. Show the enrollment table's student/course unique key and a foreign key. Show the grade table's generated total. Explain that grades belong to an enrollment, not directly to an arbitrary student/course combination.

## Create a complete academic record

In Instructors, add **Demo Instructor**, specialization **Databases**, email **demo.instructor@example.test**, status **Active**.

In Courses, add **SQL Demo Course**, assign that instructor, enter a description, **12 hours**, fee **1500**, and status **Active**. The displayed currency comes from configuration.

In Students, add **Demo Student**, email **demo.student@example.test**, optional phone blank, today's institute enrollment date, status **Active**. Search for that email to demonstrate record lookup.

In Enrollments, select the new student and course, use today's date and status **Enrolled**. Try the same pair again and show the clear duplicate-enrollment error. The failed duplicate must not create a second row.

## Grade and update

In Grades, select the new enrollment and record assignment **82**, quiz **88** and final exam **91**. Show that the stored total is **261/300**, or **87%**. Those are arithmetic examples for this demo input, not fixed dashboard metrics.

Update the final exam to **95**. Show the new total **265/300**, or **88.33%**. Edit the enrollment to **Completed** and review the student's enrollment history.

## Reports

Return to Dashboard and refresh. The counts must come from MySQL. Open Reports and show BR-01 course popularity, BR-03 student performance and BR-05 enrollment status. Open View the SQL query and explain the joins, grouping and aggregation. Export one displayed report as CSV.

Show BR-06 with an additional course that has no enrollments. Explain that this report means no enrollment records in any status, not merely no currently Enrolled students.

## Deletion and closing

Try deleting the demo instructor while its course still exists. The interface should display a related-course count and disable the destructive action. Similarly, the course, student and enrollment remain protected while their dependent records exist.

Remove the demo grade first, then its enrollment, student, course and instructor. For each deletion, select the correct record, type DELETE and check the confirmation box. This demonstrates DELETE without losing unrelated records.

Close with the Terms & Conditions page, privacy policy and favicon. Explain that the brief treats login and roles as optional; the delivered default is local-only. A shared deployment needs institute-managed authentication, appropriate privacy details and tested backups.

## Questions to be ready for

**Why an enrollment table?** A student can take several courses and a course can have several students. The table resolves that many-to-many relationship and stores status and date.

**Why use DECIMAL for marks and fees?** The schema needs fixed decimal precision. The application does not store monetary values as floating-point columns.

**How are duplicates prevented?** Python provides clear validation messages, and database unique constraints remain the final protection against simultaneous duplicate submissions.

**Why do empty courses appear in workload/popularity reports?** LEFT JOIN retains the master record even when there is no matching child row.

**Why can the displayed total not be entered manually?** MySQL generates it from the three component marks, preventing inconsistent saved totals.

**What was verified during the build?** Read TEST_REPORT.md. Offline tests and design-preview checks were performed; actual MySQL/Streamlit checks are supplied for execution in the target environment.
