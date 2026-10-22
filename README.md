# Hospital Management System (HMS)

A clean, robust, and accessible Hospital Management System built with **Python 3**, **Flask (>=3.1,<4.0)**, and **SQLite (sqlite3)**. Built as a college Project-Based Learning (PBL) application.

> **Note**: This system uses fictional patient data only. It is not intended for real clinical medical records.

---

## System Modules

### Module 1: Patient Registration and Management
- **Registration**: Registers new patients with full demographics and automatically assigns a formatted unique ID (`PAT-00001`, `PAT-00002`, ...).
- **Directory & Search**: Lists all registered patients (newest first) with case-insensitive search by Patient ID or Name (with SQL wildcard character protection).
- **Edit & Update**: Allows updating patient demographics and contact details while preventing duplicates.
- **Deletion**: Secure deletion of patient records.
- **Server-Side Validation**:
  - Full Name: required, max 100 characters, letters only (with spaces, hyphens, and apostrophes).
  - Date of Birth: required, format `YYYY-MM-DD`, between 1900 and today.
  - Gender: required, choice of `Female`, `Male`, or `Other`.
  - Phone Number: required, sanitized of spaces/dashes/brackets, 10 to 15 digits with optional leading `+`, non-repetitive.
  - Email: optional, validated format up to 254 characters.
  - Address: required, max 300 characters.

### Module 2: Appointment Management (Integration)
- **Doctor Roster**: Pre-seeded roster of medical specialists (Cardiology, General Physician, Paediatrics, Orthopaedic Surgery, Dermatology).
- **Appointment Scheduling**: Books consultation appointments for registered patients (`PAT-xxxxx`) across 30-minute intervals between 09:00 and 16:30.
- **Conflict Prevention**: Database-level unique constraint preventing double-booking for the same doctor, date, and time.
- **Referential Integrity**: Patients with scheduled appointments cannot be deleted until appointments are cancelled.

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

## Project Structure

```
hms/
├── app.py                 # Flask app, SQLite setup, validation & routes
├── requirements.txt       # Flask>=3.1,<4.0
├── README.md              # Project documentation & run guide
├── TEST_CASES.md          # 31 verified test cases with techniques
├── .gitignore             # .venv/, __pycache__/, *.db
├── templates/
│   ├── base.html          # Base layout, navbar, flash messages, footer
│   ├── patients.html      # Patient directory with search and actions
│   ├── patient_form.html  # Patient registration & edit form with inline errors
│   └── 404.html           # Custom 404 error page
├── static/
│   └── style.css          # Clean, modern stylesheet (plain CSS)
└── tests/
    ├── test_patients.py   # Module 1 test suite (27 unit & validation tests)
    └── test_defects.py    # Regression tests for identified quality defects
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

Run the full `unittest` test suite with isolated temporary databases:

```bash
python -m unittest discover -s tests -v
```
