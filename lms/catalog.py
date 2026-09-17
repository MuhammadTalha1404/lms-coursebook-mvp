"""Labels shared by record screens and the read-only design preview."""
SINGULAR = {"students":"student", "instructors":"instructor", "courses":"course", "enrollments":"enrollment", "grades":"grade"}
DESCRIPTIONS = {
    "students":"Manage student contact details and institute enrollment status.",
    "instructors":"Keep instructor details, specializations and availability in one place.",
    "courses":"Manage course information, fees, duration and instructor assignments.",
    "enrollments":"Connect students to courses and maintain their enrollment status.",
    "grades":"Record assessment marks and review automatically calculated totals.",
}
COLUMNS = {
    "students":{"id":"ID", "full_name":"Student", "email":"Email", "phone":"Phone", "enrollment_date":"Enrollment date", "status":"Status"},
    "instructors":{"id":"ID", "full_name":"Instructor", "specialization":"Specialization", "email":"Email", "status":"Status"},
    "courses":{"id":"ID", "course_name":"Course", "instructor_name":"Instructor", "duration_hours":"Hours", "fee":"Fee", "status":"Status"},
    "enrollments":{"id":"ID", "student_name":"Student", "course_name":"Course", "enrollment_date":"Enrollment date", "status":"Status"},
    "grades":{"id":"ID", "student_name":"Student", "course_name":"Course", "assignment_marks":"Assignment /100", "quiz_marks":"Quiz /100", "final_exam_marks":"Final /100", "total_marks":"Total /300", "percentage":"Percentage", "enrollment_status":"Enrollment status"},
}
