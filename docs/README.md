# Hospital Management System (HMS) - Documentation & Run Guide

A clean, robust, and accessible Hospital Management System built with **Python 3**, **Flask (>=3.1,<4.0)**, and **SQLite (sqlite3)**. Built as a college Project-Based Learning (PBL) application.

> **Note**: This system uses fictional patient data only. It is not intended for real clinical medical records.

---

## 1. System Modules & Features

### Module 1: Patient Registration and Management (Epic SCRUM-9)
- **Patient Registration (SCRUM-7)**: Full demographic intake with automatic generation of formatted unique patient IDs (`PAT-00001`, `PAT-00002`).
- **Directory & Search (SCRUM-8)**: Real-time search by Patient Code or partial Full Name with literal SQL wildcard escaping protection.
- **Server-Side Validation (SCRUM-11)**: Strict enforcement on names, DOB (1900-today), phone numbers (10-15 digits, non-repetitive), emails, and mandatory addresses.
- **Edit & Update (SCRUM-12)**: In-place editing of demographic records with validation preservation and duplicate collision checks.
- **Deletion Lock**: Patients with active appointments cannot be deleted (enforces referential integrity).

### Module 2: Appointment Management (Epic SCRUM-10)
- **Doctor Roster**: Pre-seeded medical specialists across 5 core departments (Cardiology, General Physician, Paediatrics, Orthopaedic Surgery, Dermatology).
- **Appointment Scheduling (SCRUM-13, SCRUM-14)**: 30-minute consultation slots between 09:00 and 16:30.
- **Concurrency & Conflict Prevention (SCRUM-15)**: Database-level `UNIQUE(doctor_id, appointment_date, appointment_time)` constraint blocks double-booking.
- **Appointment Directory & Cancellation (SCRUM-16)**: Chronologically ordered consultation schedule with instant cancellation support.

---

## 2. Installation & Quick Start

### Step 1: Clone Repository
```bash
git clone https://github.com/Bhumika197/hms.git
cd hms
```

### Step 2: Virtual Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows PowerShell:
.venv\Scripts\Activate.ps1

# Activate on macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## 3. Automated Test Suite Execution

Run the complete 53-test suite with isolated temporary SQLite databases:

```bash
python -m unittest discover -s tests -v
```

Execution results are preserved in [`docs/test_run.txt`](test_run.txt):
```
Ran 53 tests in ~2.9s
OK (100% Passed)
```

---

## 4. Documentation Index

- [`docs/requirements.md`](requirements.md): System functional specifications and Jira user stories.
- [`docs/test_cases.md`](test_cases.md): Full test execution table with expected vs actual results.
- [`docs/black_box_tests.md`](black_box_tests.md): Boundary Value Analysis (BVA) and Equivalence Partitioning (EP).
- [`docs/white_box_tests.md`](white_box_tests.md): Branch coverage and basis path verification.
- [`docs/bug_log.md`](bug_log.md): Defect logs, reproduction steps, severity, and commit fixes.
- [`docs/demo_script.md`](demo_script.md): 10-step viva presentation script with spoken lines.
