**Effective date: 16 September 2026**

**Operator: {{INSTITUTE_NAME}}**

This page describes the supplied project's default behavior. Before using real records, the institute must confirm its contact details, reasons for processing, access controls, retention periods and any notices required for its actual deployment. This template does not establish compliance with a specific jurisdiction.

### 1. Information entered into the application

Student records contain names, email addresses, optional phone numbers, institute enrollment dates and status. Instructor records contain names, email addresses, specializations and status. Course records contain course details, an instructor assignment, duration, fee and status. Enrollment records connect a student to a course and include a date and status. Grade records contain assignment, quiz and final-exam marks and their calculated total.

The database also stores record identifiers, creation and update timestamps and revision numbers. The application does not request identity documents, payment card details, health records, passwords for students or biometric information.

### 2. Why the application uses these records

Records support academic administration, course enrollment, assessment recording and the six management reports described in the project brief. The institute decides whether it has an appropriate basis to collect and use each record and should communicate that basis to the people concerned.

### 3. Storage and access

The application sends entered information to the MySQL server configured by the operator. The default local setup uses the user's own computer. A different deployment may use an institute server or hosting provider; the institute must identify those arrangements before publishing this notice.

The supplied project has no individual login or per-role permissions. Anyone with access to its running interface can view and modify records and download reports. Localhost binding limits access by default, but it is not a substitute for authentication in a network deployment. Database credentials are configuration secrets and should not be shared or committed to source control.

### 4. Browser operation and analytics

The browser exchanges form values and displayed data with the application while it is in use. Streamlit may use browser storage, session connections and security tokens for its interface and request protection. The project adds no advertising, marketing trackers or third-party analytics. Streamlit usage telemetry is disabled in the supplied configuration. Custom visual assets are included locally rather than loaded from an image or font service.

Hosting services, a reverse proxy, a database administrator or an institute's security systems may retain operational logs. Their practices are outside this project's configuration and must be reviewed for the actual deployment.

### 5. Reports, exports and sharing

Dashboard figures are calculated from database records. Some reports display named student or instructor information, not just aggregate figures. CSV export is initiated by an operator and saves data to that operator's device. Exported files are not automatically removed or protected by this application after download.

The project does not include automated email, external data sharing or advertising integrations. The institute remains responsible for any sharing it performs outside the application or adds through later integrations.

### 6. Retention and deletion

Records remain in MySQL until an authorized operator changes or deletes them, or a database administrator applies an approved retention process. There is no automatic expiry schedule in this project. Related records must be removed before a referenced record can be deleted. Backups and exported files may retain separate copies; their retention and deletion must be managed independently.

The institute must set a retention period appropriate to its own obligations before using live data. Sample data can be used for demonstrations without exposing actual students' information.

### 7. Corrections and requests

For access or correction requests, questions about records, or concerns about unauthorized disclosure: {{PRIVACY_CONTACT}}

The institute should verify a requester's authority before sharing or changing information and respond according to the requirements that apply to it. This application does not automate identity verification or privacy-request handling.

### 8. Deployment changes

If authentication, hosting, analytics, integrations, backups or data collection are changed, the institute should update this policy to match. Use encryption in transit and appropriate access controls for network deployments. No technical control in this project is a guarantee against every form of loss or unauthorized access.
