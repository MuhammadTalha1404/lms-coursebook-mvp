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
