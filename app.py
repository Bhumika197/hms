import os
import re
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hospital-management-secret-key-pbl')

VALID_GENDERS = ('Female', 'Male', 'Other')
VALID_TIME_SLOTS = [
    f"{h:02d}:{m:02d}"
    for h in range(9, 17)
    for m in (0, 30)
    if not (h == 16 and m > 30)
]

SEED_DOCTORS = [
    ("Dr. Sarah Jenkins", "Cardiologist"),
    ("Dr. Michael Chang", "General Physician"),
    ("Dr. Anita Patel", "Paediatrician"),
    ("Dr. David Kim", "Orthopaedic Surgeon"),
    ("Dr. Elena Gomez", "Dermatologist"),
]


def get_db_path():
    """Read DB path at call time from HMS_DATABASE env var, defaulting to hospital.db."""
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')
    return os.environ.get('HMS_DATABASE', default_path)


def get_db_connection():
    """Establish a database connection with foreign keys enabled and Row factory."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize SQLite database tables and seed initial doctor data if empty."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT UNIQUE,
            full_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id),
            doctor_id INTEGER NOT NULL REFERENCES doctors(id),
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(doctor_id, appointment_date, appointment_time)
        );
    """)

    # Seed doctors if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM doctors")
    if cur.fetchone()['cnt'] == 0:
        cur.executemany(
            "INSERT INTO doctors (name, specialization) VALUES (?, ?)",
            SEED_DOCTORS
        )

    conn.commit()
    conn.close()


def clean_phone(phone_raw):
    """Strip spaces, dashes, brackets and dots from phone string."""
    if not phone_raw:
        return ""
    # strip spaces, dashes, brackets, dots
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone_raw.strip())
    return cleaned


def validate_patient(form_data):
    """Server-side validation for patient registration and edit."""
    errors = {}
    full_name = (form_data.get('full_name') or '').strip()
    date_of_birth = (form_data.get('date_of_birth') or '').strip()
    gender = (form_data.get('gender') or '').strip()
    phone_raw = (form_data.get('phone') or '').strip()
    email = (form_data.get('email') or '').strip()
    address = (form_data.get('address') or '').strip()

    # full_name validation
    if not full_name:
        errors['full_name'] = "Full name is required."
    elif len(full_name) > 100:
        errors['full_name'] = "Full name must not exceed 100 characters."
    elif not any(c.isalpha() for c in full_name):
        errors['full_name'] = "Full name must contain at least one letter."
    else:
        # Check that name only contains letters, spaces, hyphens, periods, and apostrophes
        name_clean = full_name.replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
        if not name_clean.isalpha():
            errors['full_name'] = "Full name can only contain letters, spaces, hyphens, and apostrophes."

    # date_of_birth validation
    if not date_of_birth:
        errors['date_of_birth'] = "Date of birth is required."
    else:
        try:
            dob_parsed = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            if dob_parsed > date.today():
                errors['date_of_birth'] = "Date of birth cannot be in the future."
            elif dob_parsed < date(1900, 1, 1):
                errors['date_of_birth'] = "Date of birth cannot be before 1900."
        except ValueError:
            errors['date_of_birth'] = "Invalid date format. Use YYYY-MM-DD."

    # gender validation
    if not gender:
        errors['gender'] = "Gender is required."
    elif gender not in VALID_GENDERS:
        errors['gender'] = "Gender must be one of Female, Male, Other."

    # phone validation
    cleaned_phone = clean_phone(phone_raw)
    if not phone_raw:
        errors['phone'] = "Phone number is required."
    else:
        # Check if contains letters
        if any(c.isalpha() for c in phone_raw):
            errors['phone'] = "Phone number cannot contain letters."
        else:
            # Must be 10 to 15 digits with an optional leading +
            phone_pattern = r'^\+?[0-9]{10,15}$'
            if not re.match(phone_pattern, cleaned_phone):
                errors['phone'] = "Phone must be 10 to 15 digits with an optional leading +."
            else:
                digits_only = re.sub(r'\D', '', cleaned_phone)
                if len(set(digits_only)) <= 1:
                    errors['phone'] = "Please provide a valid phone number, not dummy repetitive digits."

    # email validation (optional)
    if email:
        if len(email) > 254:
            errors['email'] = "Email must not exceed 254 characters."
        else:
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, email):
                errors['email'] = "Invalid email format."

    # address validation
    if not address:
        errors['address'] = "Address is required."
    elif len(address) > 300:
        errors['address'] = "Address must not exceed 300 characters."

    return errors, {
        'full_name': full_name,
        'date_of_birth': date_of_birth,
        'gender': gender,
        'phone': cleaned_phone if not errors.get('phone') else phone_raw,
        'email': email,
        'address': address
    }


def validate_appointment(form_data, conn):
    """Server-side validation for booking an appointment."""
    errors = {}
    patient_code = (form_data.get('patient_code') or '').strip().upper()
    doctor_id_raw = (form_data.get('doctor_id') or '').strip()
    appointment_date = (form_data.get('appointment_date') or '').strip()
    appointment_time = (form_data.get('appointment_time') or '').strip()
    reason = (form_data.get('reason') or '').strip()

    patient_record = None
    if not patient_code:
        errors['patient_code'] = "Patient ID is required."
    else:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE UPPER(patient_code) = ?", (patient_code,))
        patient_record = cur.fetchone()
        if not patient_record:
            errors['patient_code'] = "Unknown patient ID. Please check the ID or register the patient first."

    # Doctor validation
    doctor_id = None
    if not doctor_id_raw:
        errors['doctor_id'] = "Please select a doctor."
    else:
        try:
            doctor_id = int(doctor_id_raw)
            cur = conn.cursor()
            cur.execute("SELECT id FROM doctors WHERE id = ?", (doctor_id,))
            if not cur.fetchone():
                errors['doctor_id'] = "Selected doctor does not exist."
        except ValueError:
            errors['doctor_id'] = "Invalid doctor selection."

    # Date validation
    if not appointment_date:
        errors['appointment_date'] = "Appointment date is required."
    else:
        try:
            apt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            if apt_date < date.today():
                errors['appointment_date'] = "Appointment date cannot be in the past."
        except ValueError:
            errors['appointment_date'] = "Invalid date format. Use YYYY-MM-DD."

    # Time slot validation
    if not appointment_time:
        errors['appointment_time'] = "Appointment time is required."
    elif appointment_time not in VALID_TIME_SLOTS:
        errors['appointment_time'] = f"Invalid time slot. Allowed slots are every 30 minutes from 09:00 to 16:30."

    if reason and len(reason) > 500:
        errors['reason'] = "Reason must not exceed 500 characters."

    return errors, {
        'patient_code': patient_code,
        'doctor_id': doctor_id,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time,
        'reason': reason,
        'patient_id': patient_record['id'] if patient_record else None
    }


# ================= ROUTES =================

@app.route('/')
def index():
    return redirect(url_for('patients_list'))


@app.route('/patients')
def patients_list():
    init_db()
    conn = get_db_connection()
    q = (request.args.get('q') or '').strip()

    if q:
        # Escape SQL LIKE wildcards: \ % _
        escaped_q = q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        query = """
            SELECT * FROM patients
            WHERE patient_code LIKE ? ESCAPE '\\' OR full_name LIKE ? ESCAPE '\\'
            ORDER BY id DESC
        """
        cur = conn.cursor()
        search_pattern = f"%{escaped_q}%"
        cur.execute(query, (search_pattern, search_pattern))
        patients = cur.fetchall()
    else:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients ORDER BY id DESC")
        patients = cur.fetchall()

    conn.close()
    return render_template('patients.html', patients=patients, query=q)


@app.route('/patients/new', methods=['GET', 'POST'])
def patient_new():
    init_db()
    if request.method == 'POST':
        errors, cleaned_data = validate_patient(request.form)
        if errors:
            return render_template('patient_form.html', form=request.form, errors=errors, is_edit=False), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check for duplicate patient record (same full_name, date_of_birth, and phone)
        cur.execute("""
            SELECT id, patient_code FROM patients 
            WHERE LOWER(full_name) = LOWER(?) AND date_of_birth = ? AND phone = ?
        """, (cleaned_data['full_name'], cleaned_data['date_of_birth'], cleaned_data['phone']))
        existing = cur.fetchone()
        if existing:
            conn.close()
            errors['full_name'] = f"A patient with this name, date of birth, and phone number is already registered ({existing['patient_code']})."
            return render_template('patient_form.html', form=request.form, errors=errors, is_edit=False), 400

        cur.execute("""
            INSERT INTO patients (patient_code, full_name, date_of_birth, gender, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            '',
            cleaned_data['full_name'],
            cleaned_data['date_of_birth'],
            cleaned_data['gender'],
            cleaned_data['phone'],
            cleaned_data['email'] or None,
            cleaned_data['address']
        ))
        patient_id = cur.lastrowid
        patient_code = f"PAT-{patient_id:05d}"
        cur.execute("UPDATE patients SET patient_code = ? WHERE id = ?", (patient_code, patient_id))
        conn.commit()
        conn.close()

        flash(f"Patient registered successfully with ID: {patient_code}", "success")
        return redirect(url_for('patients_list'))

    return render_template('patient_form.html', form={}, errors={}, is_edit=False)


@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
def patient_edit(patient_id):
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cur.fetchone()

    if not patient:
        conn.close()
        abort(404)

    if request.method == 'POST':
        errors, cleaned_data = validate_patient(request.form)
        if errors:
            conn.close()
            return render_template('patient_form.html', form=request.form, errors=errors, is_edit=True, patient=patient), 400

        cur.execute("""
            SELECT id, patient_code FROM patients 
            WHERE LOWER(full_name) = LOWER(?) AND date_of_birth = ? AND phone = ? AND id != ?
        """, (cleaned_data['full_name'], cleaned_data['date_of_birth'], cleaned_data['phone'], patient_id))
        existing = cur.fetchone()
        if existing:
            conn.close()
            errors['full_name'] = f"Another patient with this name, date of birth, and phone number already exists ({existing['patient_code']})."
            return render_template('patient_form.html', form=request.form, errors=errors, is_edit=True, patient=patient), 400

        cur.execute("""
            UPDATE patients
            SET full_name = ?, date_of_birth = ?, gender = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
        """, (
            cleaned_data['full_name'],
            cleaned_data['date_of_birth'],
            cleaned_data['gender'],
            cleaned_data['phone'],
            cleaned_data['email'] or None,
            cleaned_data['address'],
            patient_id
        ))
        conn.commit()
        conn.close()

        flash(f"Patient {patient['patient_code']} updated successfully.", "success")
        return redirect(url_for('patients_list'))

    form_data = dict(patient)
    conn.close()
    return render_template('patient_form.html', form=form_data, errors={}, is_edit=True, patient=patient)


@app.route('/patients/<int:patient_id>/delete', methods=['POST'])
def patient_delete(patient_id):
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cur.fetchone()
    if not patient:
        conn.close()
        abort(404)

    # Integration rule: check if patient has appointments
    cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE patient_id = ?", (patient_id,))
    apt_count = cur.fetchone()['cnt']
    if apt_count > 0:
        conn.close()
        flash("Cannot delete a patient who has appointments. Cancel the appointments first.", "danger")
        return redirect(url_for('patients_list'))

    cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()

    flash(f"Patient {patient['patient_code']} deleted successfully.", "success")
    return redirect(url_for('patients_list'))


@app.route('/appointments')
def appointments_list():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    # View all appointments sorted by date then time
    cur.execute("""
        SELECT 
            a.id,
            a.appointment_date,
            a.appointment_time,
            a.reason,
            a.created_at,
            p.id AS patient_row_id,
            p.patient_code,
            p.full_name AS patient_name,
            d.id AS doctor_row_id,
            d.name AS doctor_name,
            d.specialization AS doctor_specialization
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    """)
    appointments = cur.fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)


@app.route('/appointments/new', methods=['GET', 'POST'])
def appointment_new():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, specialization FROM doctors ORDER BY name ASC")
    doctors = cur.fetchall()

    if request.method == 'POST':
        errors, cleaned_data = validate_appointment(request.form, conn)
        if errors:
            conn.close()
            return render_template(
                'appointment_form.html',
                form=request.form,
                errors=errors,
                doctors=doctors,
                time_slots=VALID_TIME_SLOTS
            ), 400

        try:
            cur.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cleaned_data['patient_id'],
                cleaned_data['doctor_id'],
                cleaned_data['appointment_date'],
                cleaned_data['appointment_time'],
                cleaned_data['reason'] or None
            ))
            conn.commit()
            conn.close()
            flash("Appointment booked successfully.", "success")
            return redirect(url_for('appointments_list'))
        except sqlite3.IntegrityError:
            conn.close()
            errors['time_slot'] = "This doctor is already booked at the selected time."
            return render_template(
                'appointment_form.html',
                form=request.form,
                errors=errors,
                doctors=doctors,
                time_slots=VALID_TIME_SLOTS
            ), 400

    conn.close()
    return render_template(
        'appointment_form.html',
        form={},
        errors={},
        doctors=doctors,
        time_slots=VALID_TIME_SLOTS
    )


@app.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def appointment_cancel(appointment_id):
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM appointments WHERE id = ?", (appointment_id,))
    appointment = cur.fetchone()
    if not appointment:
        conn.close()
        abort(404)

    cur.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()

    flash("Appointment cancelled successfully.", "success")
    return redirect(url_for('appointments_list'))


# Route aliases for compatibility across templates and tests
app.add_url_rule('/patients', endpoint='list_patients', view_func=patients_list)
app.add_url_rule('/patients/new', endpoint='create_patient', view_func=patient_new, methods=['GET', 'POST'])
app.add_url_rule('/patients/<int:patient_id>/edit', endpoint='edit_patient', view_func=patient_edit, methods=['GET', 'POST'])
app.add_url_rule('/patients/<int:patient_id>/delete', endpoint='delete_patient', view_func=patient_delete, methods=['POST'])
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
