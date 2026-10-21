import os
import re
import sqlite3
from datetime import date, datetime

from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("HMS_SECRET_KEY", "dev-only-change-me")

VALID_GENDERS = {"Female", "Male", "Other"}
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def database_path():
    # Read at call time so tests can point to a temporary database.
    return os.environ.get("HMS_DATABASE", os.path.join(BASE_DIR, "hospital.db"))


class _Connection:
    """Context manager: commits on success, rolls back on error, always closes."""

    def __enter__(self):
        self.conn = sqlite3.connect(database_path())
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
        return False


def get_db():
    return _Connection()


def init_db():
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


@app.context_processor
def inject_today():
    return {"today": date.today().isoformat()}


def validate_patient(form):
    """Return (errors, cleaned_data)."""
    errors = {}

    full_name = " ".join(form.get("full_name", "").split())
    dob = form.get("date_of_birth", "").strip()
    gender = form.get("gender", "").strip()
    phone_raw = form.get("phone", "").strip()
    email = form.get("email", "").strip()
    address = form.get("address", "").strip()

    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) > 100:
        errors["full_name"] = "Full name must be 100 characters or fewer."
    elif not re.search(r"[A-Za-z]", full_name):
        errors["full_name"] = "Full name must contain letters."

    if not dob:
        errors["date_of_birth"] = "Date of birth is required."
    else:
        try:
            parsed = datetime.strptime(dob, "%Y-%m-%d").date()
            if parsed > date.today():
                errors["date_of_birth"] = "Date of birth cannot be in the future."
            elif parsed.year < 1900:
                errors["date_of_birth"] = "Enter a valid date of birth."
        except ValueError:
            errors["date_of_birth"] = "Enter a valid date (YYYY-MM-DD)."

    if gender not in VALID_GENDERS:
        errors["gender"] = "Select a valid gender."

    phone = re.sub(r"[\s\-()]", "", phone_raw)
    if not phone:
        errors["phone"] = "Mobile number is required."
    elif not PHONE_PATTERN.match(phone):
        errors["phone"] = "Enter a valid phone number (10 to 15 digits, optional leading +)."

    if email and (len(email) > 254 or not EMAIL_PATTERN.match(email)):
        errors["email"] = "Enter a valid email address."

    if not address:
        errors["address"] = "Address is required."
    elif len(address) > 300:
        errors["address"] = "Address must be 300 characters or fewer."

    data = {
        "full_name": full_name,
        "date_of_birth": dob,
        "gender": gender,
        "phone": phone,
        "email": email,
        "address": address,
    }
    return errors, data


@app.route("/")
def home():
    return redirect(url_for("list_patients"))


@app.route("/patients")
def list_patients():
    query = request.args.get("q", "").strip()
    with get_db() as db:
        if query:
            like = f"%{query}%"
            patients = db.execute(
                """SELECT * FROM patients
                   WHERE patient_code LIKE ? COLLATE NOCASE
                      OR full_name LIKE ? COLLATE NOCASE
                   ORDER BY id DESC""",
                (like, like),
            ).fetchall()
        else:
            patients = db.execute(
                "SELECT * FROM patients ORDER BY id DESC"
            ).fetchall()
    return render_template("patients.html", patients=patients, query=query)


@app.route("/patients/new", methods=["GET", "POST"])
def create_patient():
    if request.method == "POST":
        errors, data = validate_patient(request.form)

        if not errors:
            try:
                with get_db() as db:
                    cursor = db.execute(
                        """INSERT INTO patients
                           (full_name, date_of_birth, gender, phone, email, address)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (data["full_name"], data["date_of_birth"], data["gender"],
                         data["phone"], data["email"], data["address"]),
                    )
                    code = f"PAT-{cursor.lastrowid:05d}"
                    db.execute(
                        "UPDATE patients SET patient_code = ? WHERE id = ?",
                        (code, cursor.lastrowid),
                    )
                flash(f"Patient registered successfully. Patient ID: {code}", "success")
                return redirect(url_for("list_patients"))
            except sqlite3.IntegrityError:
                errors["general"] = "Unable to register this patient."

        return render_template(
            "patient_form.html", patient=None, values=request.form,
            errors=errors, page_title="Register Patient",
        ), 400

    return render_template(
        "patient_form.html", patient=None, values={},
        errors={}, page_title="Register Patient",
    )


@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    with get_db() as db:
        patient = db.execute(
            "SELECT * FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()

    if patient is None:
        abort(404)

    if request.method == "POST":
        errors, data = validate_patient(request.form)

        if not errors:
            try:
                with get_db() as db:
                    db.execute(
                        """UPDATE patients SET
                               full_name = ?, date_of_birth = ?, gender = ?,
                               phone = ?, email = ?, address = ?
                           WHERE id = ?""",
                        (data["full_name"], data["date_of_birth"], data["gender"],
                         data["phone"], data["email"], data["address"], patient_id),
                    )
                flash("Patient details updated successfully.", "success")
                return redirect(url_for("list_patients"))
            except sqlite3.IntegrityError:
                errors["general"] = "Unable to update this patient."

        return render_template(
            "patient_form.html", patient=patient, values=request.form,
            errors=errors, page_title="Edit Patient",
        ), 400

    return render_template(
        "patient_form.html", patient=patient, values=dict(patient),
        errors={}, page_title="Edit Patient",
    )


@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
def delete_patient(patient_id):
    with get_db() as db:
        cursor = db.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        deleted = cursor.rowcount

    if deleted == 0:
        abort(404)

    flash("Patient record deleted.", "success")
    return redirect(url_for("list_patients"))


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "base.html", standalone_message="404: Record or page not found."
    ), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
