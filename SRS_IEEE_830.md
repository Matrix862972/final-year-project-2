# Software Requirements Specification (SRS)

# The Online Exam Proctoring System

---

## 1. Introduction

### 1.1 Purpose

This SRS describes the requirements for the Online Exam Proctoring System, a secure, real-time, AI-powered web application for monitoring online exams. It is intended for developers, testers, project managers, system administrators, and institutional stakeholders. The SRS defines all functional and non-functional requirements, interfaces, constraints, and design rationale, following IEEE 830.

### 1.2 Document Conventions

- All requirements are labeled as FR (Functional), NFR (Non-Functional), or SR (Supplementary).
- Shall = mandatory, Should = recommended, May = optional.

### 1.3 Intended Audience and Reading Suggestions

- Developers: Use for implementation and code review.
- Testers: Use for test case design and validation.
- Project Managers: Use for planning, tracking, and risk management.
- Stakeholders: Use for feature review and compliance.

### 1.4 Project Overview

The Online Exam Proctoring System enables secure, scalable, and automated monitoring of remote exams. It leverages computer vision, audio analysis, and system monitoring to detect and record suspicious activities, providing real-time and post-exam evidence for administrators. The system is modular, extensible, and designed for educational institutions.

### 1.5 Definitions, Acronyms, and Abbreviations

- SRS: Software Requirements Specification
- UI: User Interface
- YOLO: You Only Look Once (object detection model)
- MTOP: Multiple Person Detection
- EDD: Electronic Device Detection
- FD: Face Detection
- SD: Screen Detection
- ED: Electronic Device
- DB: Database
- JSON: JavaScript Object Notation
- CV: Computer Vision
- API: Application Programming Interface

### 1.6 References

- IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications
- Project documentation, codebase, and user manuals
- OpenCV, MediaPipe, YOLO, PyAudio, Flask, MySQL documentation

### 1.7 Overview of Document Structure

This document is organized as follows:

1. Introduction
2. Overall Description
3. Specific Requirements
4. Appendices (Glossary, References, Traceability)

---

## 2. Overall Description

### 2.1 Product Perspective

The system is a modular, standalone web application with:

- Python Flask backend (REST API, business logic)
- Computer vision/audio modules (OpenCV, MediaPipe, YOLO, PyAudio)
- MySQL database (user, result, violation data)
- Web-based frontend (HTML/CSS/JS, Bootstrap)

#### 2.1.1 System Context Diagram (Textual)

```
	[Student/Admin] <-> [Web UI] <-> [Flask Backend] <-> [Detection Modules]
																						|                |
																				 [MySQL]        [Filesystem: Video/Audio]
```

### 2.2 Product Functions (Expanded)

#### 2.2.1 User Authentication

- Secure login for students and admins
- Password hashing and session management
- Role-based access control

#### 2.2.2 Exam Session Management

- Exam scheduling, start, pause, resume, submit
- Session time tracking, user state management

#### 2.2.3 Real-Time Monitoring

- Video: Face detection, head movement, multiple person, electronic device
- Audio: Voice activity, noise, conversation detection
- Screen: Tab/app switch, window focus, shortcut monitoring

#### 2.2.4 Violation Detection and Logging

- Automatic detection of suspicious events
- Evidence recording (video/audio clips, screenshots)
- Timestamped violation logs

#### 2.2.5 Admin Dashboard

- Results and violation review
- Evidence playback/download
- Trust score and summary report generation
- Student management (CRUD)

#### 2.2.6 System Management

- Resource cleanup, error handling, logging
- Configuration and extensibility

### 2.3 User Classes and Characteristics (Expanded)

- **Students:**
  - Can log in, take exams, view their own results
  - Must have webcam/microphone, follow exam rules
  - User Story: "As a student, I want to take my exam online and be monitored fairly."
- **Administrators:**
  - Can manage exams, review all results/violations, download evidence
  - Can add/remove students, configure exam settings
  - User Story: "As an admin, I want to detect and review suspicious activity during exams."
- **Developers/Maintainers:**
  - Maintain, update, and extend the system
  - User Story: "As a developer, I want modular code and clear documentation."

### 2.4 Operating Environment (Detailed)

- Hardware: Windows PC, webcam, microphone, 4GB+ RAM, 2+ CPU cores
- Software: Python 3.x, Flask, OpenCV, MediaPipe, YOLO, PyAudio, MySQL, browser
- Network: LAN/internet, HTTPS recommended

### 2.5 Design and Implementation Constraints

- Real-time video/audio processing (≤1s delay)
- Hardware dependencies (webcam, mic, CPU/GPU)
- Privacy, GDPR/data protection compliance
- Only tested on Windows, Chrome/Firefox/Edge

### 2.6 User Documentation

- Student and admin user manuals
- Installation/deployment guide
- Troubleshooting, FAQ, and support contacts

### 2.7 Assumptions and Dependencies

- Users have required hardware/software
- Stable network connection
- Institutional support for deployment

---

## 3. Specific Requirements

### 3.1 External Interfaces

#### 3.1.1 User Interfaces

- Web UI: Login, exam, admin dashboard, results, violation review
- Responsive design for desktop/laptop
- Real-time video/audio feedback, evidence playback
- Error messages, help, and accessibility features

#### 3.1.2 Hardware Interfaces

- Webcam (UVC compatible, 720p+ recommended)
- Microphone (standard PC mic)

#### 3.1.3 Software Interfaces

- MySQL DB: user, result, violation tables (see DB schema)
- File system: static/OutputVideos, static/OutputAudios
- Python APIs: OpenCV, MediaPipe, YOLO, PyAudio

#### 3.1.4 Communication Interfaces

- HTTP/HTTPS (REST API, web frontend)
- JSON for data exchange

#### 3.1.5 Sample Data Flows

- Student logs in → session created → exam started → monitoring begins
- Detection event → evidence file saved → violation logged in DB/JSON
- Admin reviews results → downloads evidence

---

### 3.2 Functional Requirements (Expanded)

#### 3.2.1 User Authentication

- FR1: The system shall allow students and admins to log in securely using unique credentials.
- FR2: The system shall hash and salt all passwords before storage.
- FR3: The system shall prevent SQL injection and other common attacks (input validation, parameterized queries).
- FR4: The system shall enforce session timeouts and logout on browser close.

#### 3.2.2 Exam Session Management

- FR5: The system shall allow students to start, pause (if allowed), and submit exams.
- FR6: The system shall record session start/end times, user ID, and IP address.
- FR7: The system shall prevent multiple concurrent sessions for the same user.
- FR8: The system shall display exam instructions and rules before starting.

#### 3.2.3 Video and Audio Monitoring

- FR9: The system shall capture and analyze webcam video in real time (≤1s delay).
- FR10: The system shall capture and analyze microphone audio in real time.
- FR11: The system shall record evidence clips (video/audio) for detected violations.
- FR12: The system shall provide real-time feedback if camera/mic are disconnected.

#### 3.2.4 Detection Modules

- FR13: The system shall detect and verify the student’s face using face recognition.
- FR14: The system shall detect head movement and report abnormal behavior (e.g., looking away, up/down).
- FR15: The system shall detect the presence of multiple persons (MTOP) in the frame.
- FR16: The system shall monitor screen activity and detect tab/app switches (SD), window minimization, and shortcut use.
- FR17: The system shall detect electronic devices (EDD) in the video feed (e.g., phone, laptop).
- FR18: The system shall detect and record audio violations (e.g., talking, background noise).
- FR19: The system shall log all detection events with timestamp, type, and evidence link.

#### 3.2.5 Violation Logging and Reporting

- FR20: The system shall log all detected violations with timestamp, user, and evidence.
- FR21: The system shall allow admins to review results and violation evidence via dashboard.
- FR22: The system shall generate trust scores and summary reports for each session.
- FR23: The system shall allow admins to download evidence files securely.

#### 3.2.6 Data Management

- FR24: The system shall store results and violations in both JSON files and the database.
- FR25: The system shall handle file errors, missing/corrupt data, and recover gracefully.
- FR26: The system shall allow secure download and deletion of evidence files.

#### 3.2.7 Session and Resource Management

- FR27: The system shall manage camera and audio resources efficiently, releasing them after exam completion.
- FR28: The system shall log all resource allocation and errors.

#### 3.2.8 Error Handling and Feedback

- FR29: The system shall display clear error messages for all user and system errors.
- FR30: The system shall log all critical errors for admin review.

#### 3.2.9 Audit and Compliance

- FR31: The system shall log all admin actions (review, download, delete evidence).
- FR32: The system shall provide audit trails for all exam sessions.

#### 3.2.10 Backup and Recovery

- FR33: The system shall support regular backup of results, violations, and evidence files.
- FR34: The system shall provide a recovery procedure for lost/corrupt data.

---

### 3.3 Performance Requirements

- NFR1: The system shall process video and audio in real time (≤1s delay per frame/event).
- NFR2: The system shall support at least 20 concurrent exam sessions on standard hardware.
- NFR3: The system shall store and retrieve evidence files within 2 seconds.
- NFR4: The system shall maintain 99% uptime during exam periods.

### 3.4 Design Constraints

- Use of open-source libraries (OpenCV, YOLO, etc.)
- Compliance with privacy and data protection laws (GDPR, FERPA)
- Modular, maintainable, and extensible codebase
- All code and documentation in English

### 3.5 Software System Attributes

#### 3.5.1 Reliability

- The system shall recover gracefully from hardware or software failures.
- All critical operations and errors shall be logged.
- Automated tests shall cover all major features.

#### 3.5.2 Availability

- The system shall be available 99% of the time during exam periods.
- Scheduled maintenance shall be announced in advance.

#### 3.5.3 Security

- All user data shall be stored securely (encryption at rest and in transit).
- Passwords shall be hashed and never stored in plain text.
- The system shall prevent common web vulnerabilities (SQL injection, XSS, CSRF).
- Only authorized users may access exam or evidence data.

#### 3.5.4 Usability

- The UI shall be intuitive and accessible (WCAG 2.1 compliance recommended).
- All user actions shall have clear feedback.
- Help and documentation shall be available from the UI.

#### 3.5.5 Maintainability

- The codebase shall be documented and modular.
- The system shall support easy updates, bug fixes, and feature additions.

#### 3.5.6 Portability

- The system shall be portable to other Windows systems with minimal changes.
- Linux/Mac support may be added in future versions.

#### 3.5.7 Scalability

- The system shall support scaling to more users/exams with hardware upgrades.

#### 3.5.8 Legal and Ethical

- The system shall comply with all relevant privacy, copyright, and data protection laws.

---

### 3.4 Design Constraints

- Use of open-source libraries (OpenCV, YOLO, etc.)
- Compliance with privacy and data protection laws
- Modular and maintainable codebase

### 3.5 Software System Attributes

#### 3.5.1 Reliability

- The system shall recover gracefully from hardware or software failures.
- All critical operations shall be logged.

#### 3.5.2 Availability

- The system shall be available 99% of the time during exam periods.

#### 3.5.3 Security

- All user data shall be stored securely.
- Passwords shall be hashed and never stored in plain text.
- The system shall prevent common web vulnerabilities (SQL injection, XSS, CSRF).

#### 3.5.4 Maintainability

- The codebase shall be documented and modular.
- The system shall support easy updates and bug fixes.

#### 3.5.5 Portability

- The system shall be portable to other Windows systems with minimal changes.

## 4. Appendices

### 4.1 Glossary

- **Proctoring:** Monitoring of exam takers to prevent cheating.
- **Violation:** Any suspicious or unauthorized activity detected during an exam.
- **Trust Score:** A computed score reflecting the integrity of an exam session.
- **Evidence:** Video/audio clips or logs supporting a detected violation.

### 4.2 References

- IEEE 830-1998, OpenCV, YOLO, Flask, MySQL, project codebase

### 4.3 Requirements Traceability Matrix (Sample)

| Requirement | Source                 | Implementation              | Test Case    |
| ----------- | ---------------------- | --------------------------- | ------------ |
| FR1         | Stakeholder, Security  | login() in app.py           | TC-Login-01  |
| FR13        | Stakeholder, Integrity | FaceRecognition in utils.py | TC-Face-01   |
| FR16        | Stakeholder, Integrity | screenDetection in utils.py | TC-Screen-01 |
| NFR1        | Performance            | All detection modules       | TC-Perf-01   |

### 4.4 Bug and Improvement Log

- See KNOWN_BUGS.md for a full list of tracked issues and fixes.

---

_This SRS follows the IEEE 830 standard and documents all current features and requirements of the Online Exam Proctoring System as of August 2025._
