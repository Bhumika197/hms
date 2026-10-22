import os
import re
import sqlite3
from datetime import date, datetime

from flask import (Flask, abort, flash, redirect, render_template,
                   request, url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("HMS_SECRET_KEY", "hms-secret-key-college-pbl")

VALID_GENDERS = ("Female", "Male", "Other")
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def get_db_path():
    """Read database path at call time from HMS_DATABASE env var, defaulting to hospital.db."""
    return os.environ.get("HMS_DATABASE", os.path.join(BASE_DIR, "hospital.db"))


def database_path():
    """Alias for get_db_path."""
    return get_db_path()


class DatabaseConnection:
    """Context manager for SQLite connections: commits on success, rolls back on error, always closes."""

    def __init__(self, path=None):
        self.path = path or get_db_path()
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        return False


def get_db():
    return DatabaseConnection()


def get_db_connection():
    """Direct connection with foreign keys enabled and row factory (for standard scripts)."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize SQLite database tables for HMS Module 1: Patient Management."""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_code  TEXT UNIQUE,
                full_name     TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender        TEXT NOT NULL,
                phone         TEXT NOT NULL,
                email         TEXT,
                address       TEXT NOT NULL,
                created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def clean_phone(phone_raw):
    """Strip spaces, dashes, brackets and dots from phone string."""
    if not phone_raw:
        return ""
    return re.sub(r"[\s\-\(\)\.]", "", phone_raw.strip())


def validate_patient(form):
    """Server-side validation for patient registration and editing.
    Returns (errors_dict, cleaned_data_dict).
    """
    errors = {}

    full_name = " ".join((form.get("full_name") or "").split())
    dob = (form.get("date_of_birth") or "").strip()
    gender = (form.get("gender") or "").strip()
    phone_raw = (form.get("phone") or "").strip()
    email = (form.get("email") or "").strip()
    address = (form.get("address") or "").strip()

    # Full name validation
    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) > 100:
        errors["full_name"] = "Full name must not exceed 100 characters."
    elif not any(c.isalpha() for c in full_name):
        errors["full_name"] = "Full name must contain at least one letter."
    else:
        # Check that name contains only letters, spaces, hyphens, periods, or apostrophes
        name_clean = full_name.replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
        if not name_clean.isalpha():
            errors["full_name"] = "Full name can only contain letters, spaces, hyphens, and apostrophes."

    # Date of birth validation
    if not dob:
        errors["date_of_birth"] = "Date of birth is required."
    else:
        try:
            parsed = datetime.strptime(dob, "%Y-%m-%d").date()
            if parsed > date.today():
                errors["date_of_birth"] = "Date of birth cannot be in the future."
            elif parsed < date(1900, 1, 1):
                errors["date_of_birth"] = "Date of birth cannot be before 1900."
        except ValueError:
            errors["date_of_birth"] = "Invalid date format. Use YYYY-MM-DD."

    # Gender validation
    if not gender:
        errors["gender"] = "Gender is required."
    elif gender not in VALID_GENDERS:
        errors["gender"] = "Gender must be one of Female, Male, Other."

    # Phone validation
    phone = clean_phone(phone_raw)
    if not phone_raw:
        errors["phone"] = "Phone number is required."
    elif any(c.isalpha() for c in phone_raw):
        errors["phone"] = "Phone number cannot contain letters."
    elif not PHONE_PATTERN.match(phone):
        errors["phone"] = "Phone must be 10 to 15 digits with an optional leading +."
    else:
        digits_only = re.sub(r"\D", "", phone)
        if len(set(digits_only)) <= 1:
            errors["phone"] = "Please provide a valid phone number, not dummy repetitive digits."

    # Email validation (optional)
    if email:
        if len(email) > 254:
            errors["email"] = "Email must not exceed 254 characters."
        elif not EMAIL_PATTERN.match(email):
            errors["email"] = "Invalid email format."

    # Address validation
    if not address:
        errors["address"] = "Address is required."
    elif len(address) > 300:
        errors["address"] = "Address must not exceed 300 characters."

    cleaned_data = {
        "full_name": full_name,
        "date_of_birth": dob,
        "gender": gender,
        "phone": phone if not errors.get("phone") else phone_raw,
        "email": email,
        "address": address,
    }
    return errors, cleaned_data


# ================= ROUTES =================

@app.route("/")
def home():
    """Redirect root path to patient directory."""
    return redirect(url_for("list_patients"))


@app.route("/patients")
def list_patients():
    """List all registered patients (newest first) with search functionality."""
    init_db()
    query = (request.args.get("q") or "").strip()

    with get_db() as db:
        if query:
            # Escape SQL LIKE wildcards: \ % _
            escaped_q = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            sql = """
                SELECT * FROM patients
                WHERE patient_code LIKE ? ESCAPE '\\' COLLATE NOCASE
                   OR full_name LIKE ? ESCAPE '\\' COLLATE NOCASE
                ORDER BY id DESC
            """
            search_param = f"%{escaped_q}%"
            patients = db.execute(sql, (search_param, search_param)).fetchall()
        else:
            patients = db.execute(
                "SELECT * FROM patients ORDER BY id DESC"
            ).fetchall()

    return render_template("patients.html", patients=patients, query=query)


# Alias route endpoint for backwards compatibility
@app.route("/patients/list")
def patients_list():
    return redirect(url_for("list_patients"))


@app.route("/patients/new", methods=["GET", "POST"])
def create_patient():
    """Register a new patient and auto-generate PAT-00001 code."""
    init_db()
    if request.method == "POST":
        errors, data = validate_patient(request.form)

        if not errors:
            with get_db() as db:
                # Check for duplicate patient record
                existing = db.execute("""
                    SELECT id, patient_code FROM patients
                    WHERE LOWER(full_name) = LOWER(?) AND date_of_birth = ? AND phone = ?
                """, (data["full_name"], data["date_of_birth"], data["phone"])).fetchone()

                if existing:
                    errors["full_name"] = (
                        f"A patient with this name, date of birth, and phone number is already registered ({existing['patient_code']})."
                    )
                else:
                    try:
                        cursor = db.execute("""
                            INSERT INTO patients (patient_code, full_name, date_of_birth, gender, phone, email, address)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            "",
                            data["full_name"],
                            data["date_of_birth"],
                            data["gender"],
                            data["phone"],
                            data["email"] or None,
                            data["address"],
                        ))
                        patient_id = cursor.lastrowid
                        patient_code = f"PAT-{patient_id:05d}"
                        db.execute(
                            "UPDATE patients SET patient_code = ? WHERE id = ?",
                            (patient_code, patient_id),
                        )
                        flash(f"Patient registered successfully with ID: {patient_code}", "success")
                        return redirect(url_for("list_patients"))
                    except sqlite3.IntegrityError:
                        errors["general"] = "Unable to register patient due to a database integrity error."

        return render_template(
            "patient_form.html",
            form=request.form,
            errors=errors,
            is_edit=False,
            patient=None
        ), 400

    return render_template(
        "patient_form.html",
        form={},
        errors={},
        is_edit=False,
        patient=None
    )


# Alias route endpoint
@app.route("/patients/create", methods=["GET", "POST"])
def patient_new():
    return create_patient()


@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    """Edit demographic and contact details for an existing patient."""
    init_db()
    with get_db() as db:
        patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()

    if patient is None:
        abort(404)

    if request.method == "POST":
        errors, data = validate_patient(request.form)

        if not errors:
            with get_db() as db:
                # Check for duplicate patient record among other patients
                existing = db.execute("""
                    SELECT id, patient_code FROM patients
                    WHERE LOWER(full_name) = LOWER(?) AND date_of_birth = ? AND phone = ? AND id != ?
                """, (data["full_name"], data["date_of_birth"], data["phone"], patient_id)).fetchone()

                if existing:
                    errors["full_name"] = (
                        f"Another patient with this name, date of birth, and phone number already exists ({existing['patient_code']})."
                    )
                else:
                    try:
                        db.execute("""
                            UPDATE patients
                            SET full_name = ?, date_of_birth = ?, gender = ?, phone = ?, email = ?, address = ?
                            WHERE id = ?
                        """, (
                            data["full_name"],
                            data["date_of_birth"],
                            data["gender"],
                            data["phone"],
                            data["email"] or None,
                            data["address"],
                            patient_id,
                        ))
                        flash(f"Patient {patient['patient_code']} updated successfully.", "success")
                        return redirect(url_for("list_patients"))
                    except sqlite3.IntegrityError:
                        errors["general"] = "Unable to update patient record due to a database integrity error."

        return render_template(
            "patient_form.html",
            form=request.form,
            errors=errors,
            is_edit=True,
            patient=patient
        ), 400

    form_data = dict(patient)
    return render_template(
        "patient_form.html",
        form=form_data,
        errors={},
        is_edit=True,
        patient=patient
    )


# Alias route endpoint
@app.route("/patients/<int:patient_id>/update", methods=["GET", "POST"])
def patient_edit(patient_id):
    return edit_patient(patient_id)


@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
def delete_patient(patient_id):
    """Delete a patient record."""
    init_db()
    with get_db() as db:
        # Check if patient exists
        patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        if not patient:
            abort(404)

        # Check if foreign keys exist / appointment table exists
        cursor_tbl = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'"
        ).fetchone()
        if cursor_tbl:
            apt_count = db.execute(
                "SELECT COUNT(*) AS cnt FROM appointments WHERE patient_id = ?", (patient_id,)
            ).fetchone()["cnt"]
            if apt_count > 0:
                flash("Cannot delete a patient who has appointments. Cancel the appointments first.", "danger")
                return redirect(url_for("list_patients"))

        cursor = db.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        if cursor.rowcount == 0:
            abort(404)

    flash(f"Patient {patient['patient_code']} deleted successfully.", "success")
    return redirect(url_for("list_patients"))


# Alias route endpoint
@app.route("/patients/<int:patient_id>/remove", methods=["POST"])
def patient_delete(patient_id):
    return delete_patient(patient_id)


@app.errorhandler(404)
def page_not_found(error):
    """Render custom 404 page."""
    return render_template("404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
