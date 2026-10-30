# Hospital Management System (HMS) - Requirements Specification

**Project**: Hospital Management System (HMS)  
**Jira Project Key**: `SCRUM`  
**Cloud Instance**: `https://jiraprojectbasedlearning.atlassian.net`  
**Framework**: Python 3.12, Flask, SQLite3  

---

## 1. System Overview

The Hospital Management System (HMS) is a centralized, accessible web application designed to manage core outpatient hospital workflows. The system is partitioned into two functional modules operating on a relational SQLite database with strict foreign key constraints and server-side data validation.

---

## 2. Module 1: Patient Registration and Management
**Jira Epic**: `SCRUM-9`

### User Stories & Functional Requirements

#### User Story SCRUM-7: Patient Registration
*As a hospital receptionist or triage staff member, I want to register a new patient with their full demographic and contact details, so that an official hospital patient profile is created.*
- **FR-1.1**: The system must provide a registration form accepting Legal Full Name, Date of Birth, Gender, Phone Number, Email Address (optional), and Residential Address.
- **FR-1.2**: Upon successful validation, the system must auto-generate an immutable, formatted unique identifier in the format `PAT-00001`, `PAT-00002`, sequentially incrementing.
- **FR-1.3**: The record must be persisted to the SQLite `patients` table, and the user must be redirected to the Patient Directory (`/patients`) with a confirmation flash message.

#### User Story SCRUM-8: View and Search Patient Records
*As a healthcare worker, I want to view the list of registered patients and search by Patient ID or Name, so that I can quickly locate patient records.*
- **FR-2.1**: The system must render a patient directory displaying Patient ID, Full Name, Date of Birth, Gender, Phone Number, Email, and Address, ordered newest first (`id DESC`).
- **FR-2.2**: The directory must provide a search input supporting case-insensitive searching by exact Patient Code (e.g. `PAT-00001`) or partial Full Name (e.g. `Eleanor`).
- **FR-2.3**: The search implementation must escape SQL wildcard characters (`%`, `_`) to treat them as literal strings and prevent data leakage.

#### User Story SCRUM-11: Patient Data Validation
*As a data compliance officer, I want all submitted patient data to be strictly validated on the server, so that incomplete, malformed, or garbage records are rejected.*
- **FR-3.1 (Full Name)**: Required, maximum 100 characters. Must contain at least one alphabetic character and only allow letters, spaces, hyphens, and apostrophes. Numbers and arbitrary symbols (e.g., `R2D2!!`) are rejected.
- **FR-3.2 (Date of Birth)**: Required, format `YYYY-MM-DD`. Must be between January 1, 1900 and today's date. Future dates and dates prior to 1900 are rejected.
- **FR-3.3 (Gender)**: Required. Must belong to the closed set `('Female', 'Male', 'Other')`.
- **FR-3.4 (Phone Number)**: Required. Must be sanitized of spaces, hyphens, and parentheses. Must consist of 10 to 15 digits with an optional leading `+`. Repetitive dummy digits (e.g. `0000000000`) and alphabetic characters are rejected.
- **FR-3.5 (Email Address)**: Optional. If supplied, must conform to standard RFC email syntax up to 254 characters.
- **FR-3.6 (Address)**: Required, minimum 15 characters, maximum 300 characters. Submissions with fewer than 15 characters are rejected with 'Address must be at least 15 characters.'
- **FR-3.7 (Duplicate Prevention)**: The system must check for existing records matching `(full_name, date_of_birth, phone)` and reject duplicate registrations with HTTP 400.

#### User Story SCRUM-12: Edit Patient Details
*As a medical administrator, I want to edit an existing patient's details, so that patient records remain accurate when demographics or contact details change.*
- **FR-4.1**: The system must provide an edit view pre-populated with current record values.
- **FR-4.2**: The patient's unique `patient_code` is immutable and cannot be altered.
- **FR-4.3**: All validation rules apply during updates. Invalid submissions must not corrupt or overwrite stored database values.

---

## 3. Module 2: Appointment Management
**Jira Epic**: `SCRUM-10`

### User Stories & Functional Requirements

#### User Story SCRUM-13: Book Appointment for Registered Patient
*As a clinic coordinator, I want to book an appointment for an existing patient with an attending specialist, so that consultations are properly scheduled.*
- **FR-5.1**: The booking form requires a valid registered Patient ID (`PAT-xxxxx`).
- **FR-5.2**: The system must verify that the patient exists in the database. Unknown patient IDs must be rejected with HTTP 400.

#### User Story SCRUM-14: Doctor, Date, and Time Selection
*As a scheduling officer, I want to select an attending doctor, consultation date, and a specific 30-minute time slot, so that physician schedules are organized.*
- **FR-6.1**: The system seeds 5 attending specialists across core departments (Cardiology, General Medicine, Paediatrics, Orthopaedic Surgery, Dermatology).
- **FR-6.2**: Appointment dates must be in `YYYY-MM-DD` format and cannot be in the past. Today and future dates are permitted.
- **FR-6.3**: Consultation slots are restricted to 30-minute intervals between `09:00` and `16:30` inclusive (16 valid daily slots).

#### User Story SCRUM-15: Concurrency & Duplicate Booking Prevention
*As a clinic director, I want to prevent double-booking for the same doctor, date, and time, so that scheduling conflicts are physically impossible.*
- **FR-7.1**: The database enforces a `UNIQUE(doctor_id, appointment_date, appointment_time)` constraint on the `appointments` table.
- **FR-7.2**: Duplicate slot submissions must be caught cleanly and return an HTTP 400 validation error stating: *"This doctor is already booked at the selected time."*
- **FR-7.3**: The same time slot with a different doctor must be permitted.

#### User Story SCRUM-16: View and Cancel Appointments
*As clinic staff, I want to review the chronological consultation schedule and cancel visits if requested, so that outpatient calendars remain current.*
- **FR-8.1**: The appointments directory lists all scheduled visits ordered chronologically by `appointment_date ASC, appointment_time ASC`.
- **FR-8.2**: Each listing shows Patient Code, Patient Full Name, Attending Doctor, Specialization, Date, Time, and Consultation Reason.
- **FR-8.3**: Authorised staff can cancel an appointment via POST, immediately removing it from SQLite and releasing the slot.

---

## 4. Integration & Business Rules

1. **Referential Integrity & Patient Deletion Lock (TC-49)**:
   - A patient record with scheduled appointments **cannot be deleted**.
   - Attempting deletion returns an HTTP 200/400 flash error instructing the user to cancel pending appointments first.
2. **Deletion Lock Release (TC-50)**:
   - Once all appointments for a patient are cancelled, the patient record can be safely deleted.
3. **Database Configuration**:
   - SQLite3 database initialized with `PRAGMA foreign_keys = ON;`.
   - Dynamic path resolution via `HMS_DATABASE` environment variable defaulting to local `hospital.db`.

