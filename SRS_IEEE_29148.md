# Software Requirements Specification (SRS)

# The Online Exam Proctoring System

# IEEE 29148-2018 (2nd Edition) Format (Custom Structure)

---

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to comprehensively define the requirements for the Online Exam Proctoring System, ensuring a clear and mutual understanding among all stakeholders—including developers, testers, project managers, institutional IT staff, compliance officers, and end users (students and administrators). This SRS serves several key objectives:

- **Foundation for Development:** Provides a detailed blueprint for the design, implementation, and testing of the system, reducing ambiguity and minimizing the risk of misinterpretation.
- **Stakeholder Agreement:** Acts as a formal agreement between stakeholders, capturing all functional and non-functional requirements, constraints, and expectations.
- **Project Management:** Supports planning, resource allocation, and progress tracking throughout the software lifecycle.
- **Quality Assurance:** Establishes the basis for validation, verification, and acceptance criteria, ensuring the delivered system meets user needs and regulatory standards.
- **Compliance and Audit:** Documents requirements for privacy, security, and legal compliance (e.g., GDPR, FERPA), supporting institutional audits and risk management.
- **Change Management:** Facilitates controlled evolution of the system by providing a reference for future enhancements, maintenance, and troubleshooting.

The Online Exam Proctoring System itself is intended to:

- Enable secure, scalable, and automated monitoring of online exams.
- Detect and record suspicious behaviors using AI-powered video, audio, and screen analysis.
- Provide real-time and post-exam evidence for review by authorized personnel.
- Protect the integrity of remote assessments while respecting user privacy and accessibility needs.

### 1.2 Scope

The scope of the Online Exam Proctoring System encompasses the design, development, deployment, and maintenance of a secure, real-time, AI-powered web application for monitoring online exams. The system is intended for use by educational institutions, universities, certification bodies, and other organizations conducting remote assessments. Key aspects of the scope include:

- **Supported Use Cases:**

  - Proctoring of scheduled online exams for students, including real-time and post-exam review.
  - Automated detection of suspicious behaviors (e.g., multiple faces, device usage, audio violations, screen switching).
  - Evidence collection (video, audio) and secure storage for later review by authorized personnel.
  - Administrative dashboard for managing exams, reviewing results, and generating reports.
  - User authentication and role-based access for students and administrators.

- **Deployment:**

  - Designed for deployment on local machines or local institutional networks only (no cloud deployment in current version).
  - Supports small-scale deployments, such as single class or department-level exam sessions.

- **Users:**

  - Students (exam takers), administrators (proctors, reviewers), IT/compliance staff, and developers/maintainers.

- **System Boundaries:**

  - Interfaces with webcams, microphones, and browsers on user devices. The system requires direct access to these peripherals for real-time monitoring and evidence collection. Supported browsers include Chrome, Firefox, and Edge on Windows OS. The application does not support mobile or tablet browsers in the current version.
  - Operates within the local network or on a standalone machine, with all data transmission and storage remaining within the local environment to ensure privacy and compliance.
  - Does not include exam content creation or grading functionality (focus is on proctoring and monitoring). The system is designed to work alongside existing exam delivery platforms, but does not itself deliver questions or evaluate answers.
  - Provides a web-based dashboard for administrators and proctors, accessible only within the local network or on the host machine.
  - All evidence (video, audio, screenshots) is stored locally, with access restricted to authorized users only. No data is transmitted to external servers or cloud services.
  - The system logs all access and actions for audit and compliance purposes, but does not monitor or control network traffic outside its own application scope.
  - User devices must meet minimum hardware requirements (webcam: UVC compatible, microphone: standard input, CPU: dual-core or better, RAM: 4GB+ recommended).
  - The system does not interact with or monitor other applications on the user's device, except for detecting screen/tab switching as part of proctoring.
  - No integration with third-party analytics, advertising, or tracking services is present; all processing is performed locally.

**Out of Scope:**

- Mobile/tablet support: The current version is designed and tested exclusively for desktop and laptop environments, due to hardware access limitations and security concerns on mobile platforms. Support for mobile/tablet devices may be considered in future releases if secure and reliable monitoring can be ensured.
- Third-party exam platforms: Direct integration with external exam delivery or learning management systems (LMS) is not included in this version. The system is intended to operate independently or alongside such platforms, but does not provide built-in APIs or plugins for third-party services. Future versions may include integration capabilities based on user demand and security evaluation.
- Manual proctoring: The system is designed for automated and semi-automated proctoring workflows only. It does not provide features for live human proctors to monitor students in real time, such as video conferencing or chat. All monitoring and evidence collection are performed by the system's AI modules, with post-exam review by authorized personnel.
- Exam content management: Creation, editing, and grading of exam questions are outside the scope of this system. The focus is solely on monitoring and proctoring during exam sessions.
- Cloud-based deployment: The current version does not support deployment on public or private cloud infrastructure. All components and data remain within the local network or host machine for privacy and compliance reasons.
- Analytics and advanced reporting: While basic reporting and evidence review are included, advanced analytics, dashboards, and statistical analysis features are not part of the initial release.

**Extensibility:**
The system is designed with a modular, loosely-coupled architecture, enabling rapid development and integration of new features without disrupting existing functionality. Key aspects of extensibility include:

- **Plugin Support:** New detection modules, analytics engines, or hardware integrations can be added as plugins or separate modules, minimizing the need to modify core code.
- **API and Integration Points:** Well-defined internal APIs and data interfaces allow for seamless integration with external systems, such as LMS platforms or institutional authentication services, in future versions.
- **Configurable Workflows:** System workflows (e.g., violation detection, evidence storage, reporting) are designed to be configurable, supporting custom rules or additional steps as requirements evolve.
- **Example Future Enhancements:**
  - Additional detection modules (e.g., eye tracking, keystroke analysis, environmental sound detection, behavioral biometrics)
  - Advanced analytics, customizable dashboards, and real-time alerting
  - Deeper integration with learning management systems (LMS) or exam delivery platforms for unified user experience
  - Support for new hardware (e.g., biometric devices, multi-camera setups)
  - Expanded accessibility features (screen reader support, localization, alternative input methods)
  - Cloud or hybrid deployment options for scalability and remote access
  - Automated compliance reporting and audit trail exports

These enhancements can be incorporated with minimal changes to the core system, ensuring long-term adaptability, maintainability, and scalability as user needs and technology evolve.

### 1.3 Product Overview

#### 1.3.1 Product Perspective

- Python Flask backend (REST API, business logic)
- Computer vision/audio modules (OpenCV, MediaPipe, YOLO, PyAudio)
- MySQL database (user, result, violation data)
  This document specifies the requirements for the Online Exam Proctoring System, a comprehensive solution for secure, automated, and scalable online exam monitoring. The SRS is intended to:
- Serve as a contract between stakeholders and developers.
- Guide the design, implementation, and validation of the system.
- Ensure compliance with institutional, legal, and technical standards.

#### 1.3.2 Product Functions

The Online Exam Proctoring System is a secure, real-time, AI-powered web application for monitoring online exams, designed for educational institutions, universities, and certification bodies. It provides:

- Automated detection of suspicious behaviors (face, audio, screen, device, multi-person)
- Real-time and post-exam evidence collection
- Admin dashboard for review and reporting
- Secure storage and privacy compliance
  The system is intended for deployment in small environments.
- User authentication (student/admin login)
- Exam session management
- Real-time video and audio monitoring
- Face detection and verification
  The system is modular and extensible, integrating:
- **Python Flask backend:** REST API, business logic, session management, security.
- **Computer vision/audio modules:** OpenCV (video), MediaPipe (face/landmarks), YOLO (object/device detection), PyAudio (audio capture/analysis).
- **MySQL database:** User, result, violation, and audit tables.
- **Web-based frontend:** Responsive UI (HTML/CSS/JS, Bootstrap), real-time feedback, evidence playback.
  The system can be deployed on institutional servers or cloud infrastructure.
- Audio violation detection (voice recording)
- Violation evidence recording (video/audio clips)
  **Authentication & Authorization:**
- Secure login for students and admins (role-based access)
- Password hashing, session management, brute-force protection

**Exam Session Management:**

- Exam scheduling, start/pause/resume/submit
- Session time tracking, user state

**Real-Time Monitoring:**

- **Video Monitoring:**

  - Face detection and verification: Uses computer vision (OpenCV, MediaPipe) to ensure the registered student is present throughout the exam. Alerts and records evidence if the face is not detected or does not match the registered user.
  - Head movement tracking: Monitors for excessive or suspicious head movements (e.g., looking away from the screen repeatedly), which may indicate cheating attempts. Events are logged and video clips are saved as evidence.
  - Multiple person detection: Detects the presence of more than one person in the camera frame using AI models (e.g., YOLO). Triggers a violation and records video evidence if additional faces or bodies are detected.
  - Device detection: Identifies unauthorized electronic devices (e.g., phones, tablets) visible in the camera frame. Detected events are logged and video evidence is captured for review.

- **Audio Monitoring:**

  - Voice activity detection: Monitors for unexpected speech or conversation during the exam. Uses audio analysis (PyAudio) to detect and log voice activity, flagging possible collaboration or external assistance.
  - Noise detection: Identifies unusual background noises (e.g., other people talking, electronic device sounds) that may indicate a breach of exam conditions. Audio clips are recorded as evidence.
  - Conversation detection: Attempts to distinguish between the student speaking to themselves and speaking to others, flagging suspicious interactions for review.

- **Screen Monitoring:**
  - Tab/app switch detection: Monitors browser and system events to detect when the user switches away from the exam window or opens unauthorized applications. Each event is logged with a timestamp.
  - Window focus monitoring: Ensures the exam window remains the active window; loss of focus is recorded as a potential violation.
  - Shortcut monitoring: Detects the use of keyboard shortcuts (e.g., copy, paste, print screen) that may be used to cheat or capture exam content. Such actions are logged and may trigger alerts.

All real-time monitoring modules operate in parallel, with detected violations immediately logged and associated evidence (video/audio clips, screenshots, event logs) securely stored for post-exam review by administrators.

**Violation Detection & Logging:**

- Automatic detection of suspicious events
- Evidence recording (video/audio clips, screenshots)
- Timestamped violation logs, trust score computation

**Admin Dashboard:**

- Results and violation review, evidence playback/download
- Trust score and summary report generation
- Student management (CRUD), audit logs

**System Management:**

- Resource cleanup, error handling, logging, configuration
- Requires webcam and microphone
- Tested on Windows OS, Chrome/Firefox/Edge
  **Students:** - Use a webcam/microphone, follow exam rules, interact with a simple UI. - User Story: "As a student, I want to take my exam online and be monitored fairly, so I can focus on my test."
  **Administrators:** - Manage exams, review results/violations, download evidence, manage users. - User Story: "As an admin, I want to detect and review suspicious activity, so I can ensure exam integrity."
  **Developers/Maintainers:** - Maintain, update, and extend the system, ensure compliance and performance. - User Story: "As a developer, I want modular code and clear documentation, so I can add features and fix bugs easily."
  **IT/Compliance:** - Oversee deployment, privacy, and legal compliance.

- SRS: Software Requirements Specification
  **Limitations:**
- Requires webcam and microphone (hardware dependency)
- Tested on Windows OS, Chrome/Firefox/Edge (browser/OS dependency)
- Real-time processing (≤1s delay per event)
- Privacy and data protection compliance required (GDPR, FERPA)
- Not designed for mobile/tablet use in current version
- FD: Face Detection
- SD: Screen Detection

### 1.4 Definitions (see also 5.2)

- ED: Electronic Device
- DB: Database
- JSON: JavaScript Object Notation
- Proctoring: Monitoring of exam takers to prevent cheating
- Violation: Any suspicious or unauthorized activity detected during an exam

#### 3.1.1 User Authentication

- Secure login (username/password, role-based)
- Passwords hashed (bcrypt or equivalent)
- SQL injection and brute-force protection
- Session timeout, logout on browser close
  **Rationale:** Prevent unauthorized access and protect user data.
  **Acceptance Criteria:** Only valid users can log in; all passwords are hashed; failed logins are logged.
  **Error Handling:** Invalid login attempts show a generic error; repeated failures may lock account.
- Evidence: Video/audio clips or logs supporting a detected violation

#### 3.1.2 Exam Session Management

- Exam scheduling, start/pause/resume/submit
- Session time, user/device/IP logging
- Prevent multiple concurrent sessions
- Display exam instructions/rules
  **Rationale:** Ensure exam integrity and traceability.
  **Acceptance Criteria:** Only one session per user; all sessions logged; instructions shown before start.
  **Error Handling:** Attempts to start multiple sessions are blocked; session interruptions are logged.

## 2. References

#### 3.1.3 Video and Audio Monitoring

- Real-time webcam and microphone capture (≤1s delay)
- Evidence clips for violations
- Feedback if camera/mic disconnected
  **Rationale:** Detect and record suspicious activity.
  **Acceptance Criteria:** All events are timestamped; evidence is available for review.
  **Error Handling:** Hardware disconnects prompt user and log event.
- ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes — Requirements engineering
- IEEE Std 830-1998 (for comparison)

#### 3.1.4 Detection Modules

- Face detection/verification, head movement, multiple person, device, audio violations, screen monitoring
- All detection events logged with timestamp/type/evidence
  **Rationale:** Provide comprehensive monitoring.
  **Acceptance Criteria:** All detection modules work in parallel; events are logged and reviewable.
  **Error Handling:** Detection failures are logged; fallback to manual review if needed.
- OpenCV, MediaPipe, YOLO, PyAudio, Flask, MySQL documentation

#### 3.1.5 Violation Logging and Reporting

- Log all violations with timestamp, user, evidence
- Admin dashboard for review, download, trust score
  **Rationale:** Enable post-exam review and evidence-based decisions.
  **Acceptance Criteria:** All violations are visible to admins; evidence is downloadable.
  **Error Handling:** Corrupt/missing evidence is flagged.

## 3. Requirements

#### 3.1.6 Data Management

- Store results/violations in JSON and DB
- Handle file errors, missing/corrupt data
- Secure download/deletion of evidence
  **Rationale:** Ensure data integrity and recoverability.
  **Acceptance Criteria:** No data loss; all evidence is retrievable.
  **Error Handling:** Data errors trigger alerts and recovery procedures.

### 3.1 Functions

#### 3.1.7 Session and Resource Management

- Efficient camera/audio resource use; release after exam
- Log all resource allocation/errors
  **Rationale:** Prevent resource leaks and ensure system stability.
  **Acceptance Criteria:** No resource leaks; all resources released after use.
  **Error Handling:** Resource errors are logged and trigger cleanup.
- Detailed requirements are listed below.

#### 3.1.8 Error Handling and Feedback

- Clear error messages for all user/system errors
- Log all critical errors for admin review
  **Rationale:** Improve user experience and system maintainability.
  **Acceptance Criteria:** All errors are logged and actionable.
  **Error Handling:** User-facing errors are non-technical; logs contain full details.

...existing content from Functional Requirements (User Authentication)...

#### 3.1.9 Audit and Compliance

- Log all admin actions; provide audit trails
  **Rationale:** Support institutional/legal compliance.
  **Acceptance Criteria:** All admin actions are traceable.
  **Error Handling:** Audit log failures are flagged for IT review.

#### Exam Session Management

#### 3.1.10 Backup and Recovery

- Regular backup of results, violations, evidence
- Recovery procedure for lost/corrupt data
  **Rationale:** Ensure business continuity.
  **Acceptance Criteria:** Backups are restorable; recovery is documented.
  **Error Handling:** Backup failures trigger alerts.

#### Video and Audio Monitoring

### 3.2 Performance Requirements

- Real-time processing (≤1s delay per frame/event)
- Support ≥20 concurrent sessions on standard hardware
- Store/retrieve evidence files within 2 seconds
- 99% uptime during exam periods
  **Rationale:** Maintain exam integrity and user experience.
  **Acceptance Criteria:** System meets all timing and concurrency targets in load tests.
  ...existing content from Functional Requirements (Video and Audio Monitoring)...

### 3.3 Usability Requirements

- Intuitive, accessible UI (WCAG 2.1 compliance recommended)
- Clear feedback for all user actions
- Help/documentation available from UI
  **Rationale:** Reduce user error and support accessibility.
  **Acceptance Criteria:** Users can complete all tasks without training; accessibility audit passes.

...existing content from Functional Requirements (Detection Modules)...

### 3.4 Interface Requirements

- Web UI: Login, exam, admin dashboard, results, violation review
- Responsive design for desktop/laptop
- Real-time video/audio feedback, evidence playback
- Error/help/accessibility features
- Hardware: Webcam (UVC, 720p+), Microphone
- Software: MySQL DB, file system, OpenCV, MediaPipe, YOLO, PyAudio
- Communication: HTTP/HTTPS (REST API), JSON
  **Rationale:** Ensure interoperability and ease of integration.
  **Acceptance Criteria:** All interfaces are documented and pass integration tests.

#### Violation Logging and Reporting

### 3.5 Logical Database Requirements

- All results, violations, and evidence metadata stored in both JSON and DB
- Evidence files (video/audio) stored in file system with unique names
- All data backed up regularly
- Sample schema: - users(id, name, email, password_hash, role, created_at) - results(id, user_id, exam_id, score, trust_score, created_at) - violations(id, result_id, type, timestamp, evidence_link, mark) - audit_log(id, admin_id, action, timestamp, details)
  **Rationale:** Support traceability, reporting, and recovery.
  **Acceptance Criteria:** All data is queryable and restorable.

...existing content from Functional Requirements (Data Management)...

### 3.6 Software System Attributes

- **Reliability:** Recovers from hardware/software failures; all critical operations logged; automated tests for all features.
- **Availability:** 99% uptime during exam periods; scheduled maintenance announced.
- **Security:** Data encrypted at rest/in transit; passwords hashed; web vulnerabilities prevented; access control enforced.
- **Usability:** Intuitive, accessible UI; clear feedback; help available.
- **Maintainability:** Modular, documented codebase; easy updates/bug fixes.
- **Portability:** Minimal changes for Windows deployment; Linux/Mac support possible.
- **Scalability:** Supports more users/exams with hardware upgrades.
- **Legal/Ethical:** Complies with privacy, copyright, and data protection laws.
  **Rationale:** Ensure system is robust, secure, and future-proof.
  **Acceptance Criteria:** All attributes are validated by tests, audits, and user feedback.

#### Session and Resource Management

### 3.7 Supporting Information

- See Appendices for glossary, references, traceability, bug log, and additional diagrams.

#### Error Handling and Feedback

...existing content from Functional Requirements (Error Handling and Feedback)...

### 4.1 Functions

- Verified by code review, unit/integration testing, user acceptance testing.
- Example test case: Attempt login with valid/invalid credentials; verify session creation and error handling.

### 4.2 Performance Requirements

- Verified by load testing (simulate ≥20 concurrent sessions), real-time monitoring, and timing analysis.
- Example: Measure evidence file retrieval time under load.

### 4.3 Usability Requirements

- Verified by user surveys, accessibility audits, UI walkthroughs, and task completion rates.
- Example: Users complete exam start/submit without external help.

### 4.4 Interface Requirements

- Verified by integration testing, API validation, and hardware compatibility checks.
- Example: Test all REST endpoints and device connections.

### 4.5 Logical Database Requirements

- Verified by schema review, data integrity checks, backup/restore tests, and sample queries.
- Example: Restore from backup and verify all data is present.

### 4.6 Software System Attributes

- Verified by code analysis, automated tests, security audits, and user feedback.
- Example: Penetration test for SQL injection; review for modularity.

### 4.7 Supporting Information

- Verified by documentation review, stakeholder feedback, and traceability matrix.

...existing content from Non-Functional Requirements (Usability)...

### 3.4 Interface Requirements

### 5.1 Assumptions and Dependencies

- Users have required hardware/software and stable network connection.
- Institutional support for deployment, privacy, and compliance.
- Third-party libraries (OpenCV, YOLO, Flask, etc.) are maintained and compatible.

### 3.5 Logical Database Requirements

### 5.2 Acronyms and Abbreviations

- See Section 1.4 Definitions.
- Evidence files (video/audio) shall be stored in the file system with unique names.
- All data shall be backed up regularly.

### 3.6 Software System Attributes

...existing content from Quality Requirements...

### 3.7 Supporting Information

- See Appendices for glossary, references, traceability, and bug log.

---

## 4. Verification

### 4.1 Functions

- Each functional requirement shall be verified by code review, unit/integration testing, and user acceptance testing.

### 4.2 Performance Requirements

- Performance shall be verified by load testing and real-time monitoring during exam sessions.

### 4.3 Usability Requirements

- Usability shall be verified by user surveys, accessibility audits, and UI walkthroughs.

### 4.4 Interface Requirements

- Interface requirements shall be verified by integration testing and API validation.

### 4.5 Logical Database Requirements

- Database requirements shall be verified by schema review, data integrity checks, and backup/restore tests.

### 4.6 Software System Attributes

- Reliability, maintainability, and security shall be verified by code analysis, automated tests, and security audits.

### 4.7 Supporting Information

- Supporting information shall be verified by documentation review and stakeholder feedback.

---

## 5. Appendices

### 5.1 Assumptions and Dependencies

- Users have required hardware/software and stable network connection.
- Institutional support for deployment and compliance.

### 5.2 Acronyms and Abbreviations

- See Section 1.4 Definitions.

---

_This SRS follows the ISO/IEC/IEEE 29148:2018 (2nd Edition) standard and documents all current features and requirements of the Online Exam Proctoring System as of August 2025._
