# Hospital Management System (HMS)

A clean, robust, and accessible Hospital Management System built with **Python 3**, **Flask (>=3.1,<4.0)**, and **SQLite (sqlite3)**. Built as a college Project-Based Learning (PBL) application.

> **Note**: This system uses fictional patient data only. It is not intended for real clinical medical records.

---

## System Modules

### Module 1: Patient Registration and Management (Epic SCRUM-9)
- **Registration (SCRUM-7)**: Registers new patients with full demographics and automatically assigns an immutable formatted unique ID (`PAT-00001`, `PAT-00002`, ...).
- **Directory & Search (SCRUM-8)**: Lists all registered patients (newest first) with case-insensitive search by Patient ID or Name (with SQL wildcard protection).
- **Validation (SCRUM-11)**: Strict server-side validation:
  - Full Name: required, max 100 characters, letters only (with spaces, hyphens, and apostrophes).
  - Date of Birth: required, format `YYYY-MM-DD`, between 1900 and today.
  - Gender: required, choice of `Female`, `Male`, or `Other`.
  - Phone Number: required, sanitized of spaces/dashes/brackets, 10 to 15 digits with optional leading `+`, non-repetitive.
  - Email: optional, validated format up to 254 characters.
  - Address: required, max 300 characters.
  - Duplicate Protection: Rejects duplicate submissions with identical Name, DOB, and Phone.
- **Edit & Update (SCRUM-12)**: Allows updating patient demographics and contact details while preserving validation integrity.
- **Deletion Lock**: Patients with scheduled appointments cannot be deleted until appointments are cancelled.

### Module 2: Appointment Management (Epic SCRUM-10)
- **Doctor Roster**: Pre-seeded roster of medical specialists (Cardiology, General Physician, Paediatrics, Orthopaedic Surgery, Dermatology).
- **Appointment Scheduling (SCRUM-13, SCRUM-14)**: Books consultation appointments for registered patients (`PAT-xxxxx`) across 30-minute intervals between 09:00 and 16:30.
- **Conflict Prevention (SCRUM-15)**: Database-level unique constraint preventing double-booking for the same doctor, date, and time.
- **Appointment Directory & Cancellation (SCRUM-16)**: Chronologically ordered consultations with cancellation support.

---

## Database Architecture

Connections run with `PRAGMA foreign_keys = ON;`. The database path is resolved at call time via the `HMS_DATABASE` environment variable, defaulting to `hospital.db`.

```sql
CREATE TABLE patients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_code  TEXT UNIQUE,
    full_name     TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender        TEXT NOT NULL,
    phone         TEXT NOT NULL,
    email         TEXT,
    address       TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE doctors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    specialization TEXT NOT NULL
);

CREATE TABLE appointments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL REFERENCES patients(id),
    doctor_id        INTEGER NOT NULL REFERENCES doctors(id),
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    reason           TEXT,
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, appointment_date, appointment_time)
);
```

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Bhumika197/hms.git
cd hms
```

### 2. Create virtual environment
```bash
python -m venv .venv

# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## Running the Automated Test Suite

Run the full 53-test `unittest` test suite with isolated temporary databases:

```bash
python -m unittest discover -s tests -v
```

Execution results:
```
Ran 53 tests in 2.9s
OK (100% Passed)
```

Log artifact: [`docs/test_run.txt`](docs/test_run.txt)

---

## Documentation Library

- [`docs/requirements.md`](docs/requirements.md): System functional specifications and Jira user stories.
- [`docs/test_cases.md`](docs/test_cases.md): 53 test cases with inputs, expected and actual results.
- [`docs/black_box_tests.md`](docs/black_box_tests.md): Boundary Value Analysis (BVA) and Equivalence Partitioning (EP).
- [`docs/white_box_tests.md`](docs/white_box_tests.md): Branch coverage analysis and basis path verification.
- [`docs/bug_log.md`](docs/bug_log.md): Defect report, severity, steps to reproduce, and retest evidence.
- [`docs/demo_script.md`](docs/demo_script.md): 10-step viva presentation script with spoken lines.
