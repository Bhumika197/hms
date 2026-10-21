# Hospital Management System: Patient Registration & Management

Module 1 of a Hospital Management System (college PBL project), built with Python, Flask and SQLite.
Uses fictional patient data only. Not for real medical records.

## Features
- Register patients with an auto-generated unique ID (`PAT-00001`, ...)
- View, search (by ID or name), edit and delete patient records
- Server-side validation: required fields, phone number, date of birth, email
- Automated tests (13 cases)

## Setup
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux:        source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Structure
```
app.py            Flask app, database, validation
templates/        HTML templates
tests/            Automated tests
requirements.txt  Dependencies
```
