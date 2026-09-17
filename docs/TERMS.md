**Effective date: 16 September 2026**

**Operator: {{INSTITUTE_NAME}}**

This is the policy template supplied with the Coursebook project. The institute must confirm its contact details, access arrangements and applicable requirements before publishing the application or entering real personal data. It is not a claim of legal compliance in a particular country.

### 1. Purpose of this workspace

Coursebook is an academic administration tool for maintaining student and instructor records, courses, enrollments and assessment results. It is intended for people authorized by the institute to manage those records. It does not provide teaching content, take payments or issue accredited qualifications.

### 2. Authorized use

Use the workspace only for institute-approved academic administration. Do not access, enter, change, export or remove information without permission. Do not attempt to bypass access controls, interfere with the database or use student contact details for unrelated purposes.

The supplied application has no individual user accounts or role-based permissions. Anyone who can access a running instance can use its administrative functions. The default configuration therefore limits the service to the local computer. Before providing network access, the institute must put appropriate authentication and access restrictions in place.

### 3. Accuracy and assessment records

The operator is responsible for checking information before saving it. Coursebook checks required fields, permitted statuses, duplicate email addresses, duplicate enrollments and assessment ranges. These checks do not establish that submitted information is factually correct.

In this project, assignment, quiz and final-exam marks are each recorded out of 100. Their unweighted total is out of 300. No institutional pass mark, letter grade or accreditation decision is implied. The institute must approve that convention or change the implementation before using another assessment scheme.

### 4. Changes and deletion

Updates affect the connected MySQL database. Deleting a record is permanent through the application and requires confirmation. Records with dependent records cannot be deleted until those dependencies are removed. A backup may allow an administrator to restore information, but the application does not provide an undo or automatic backup service.

Keep records when retention is required. Prefer a status change to deletion when maintaining a student's or course's history. The institute is responsible for retention schedules, backups and restoration procedures.

### 5. Exports and confidentiality

CSV exports contain the information in the selected view. Store exports securely and share them only with authorized recipients. Once a file has been downloaded, the application does not control its onward use, storage or deletion. Do not publish personal data or credentials in demonstrations, repositories or screenshots.

### 6. Availability and administration

Availability depends on the host computer, the Python application, MySQL and the network connection used for deployment. The institute manages access, maintenance, updates and recovery. This project does not promise uninterrupted operation or a support service. Test changes and database migrations before applying them to important records.

Fictional sample records are supplied for learning and demonstration. They are not evidence of an institute's actual enrollment, staff, revenue or student performance.

### 7. Questions and updates

For corrections, permission questions or suspected misuse: {{PRIVACY_CONTACT}}

The institute should update this page when the operator, functionality or access arrangements change, and communicate material changes to its users. Nothing on this page is intended to remove rights that cannot lawfully be excluded.
