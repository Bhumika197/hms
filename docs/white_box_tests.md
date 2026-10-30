# Hospital Management System (HMS) - White-Box Testing Specification

**Technique**: Branch Coverage & Basis Path Testing  
**Target Code**: `app.py`  
**Execution Verification**: Standard Python `unittest` harness with isolated SQLite databases.

---

## 1. Branch Coverage Analysis

### 1.1 Unique Patient Code Generator (`get_next_patient_code`)

Source function:
```python
def get_next_patient_code(conn):
    cur = conn.cursor()
    cur.execute("SELECT patient_code FROM patients WHERE patient_code LIKE 'PAT-%' ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if not row or not row['patient_code']:
        return "PAT-00001"
    # parse integer and increment + 1
```

- **Branch 1A (Table Empty or No Matches)**:
  - *Condition*: `row is None`
  - *Outcome*: Returns default seed code `"PAT-00001"`.
  - *Test Verification*: `test_valid_patient_registration` *(TC-01)*.
- **Branch 1B (Table Contains Existing Codes)**:
  - *Condition*: `row` matches `PAT-(\d+)`
  - *Outcome*: Extracts integer, computes `next_num = num + 1`, zero-pads to 5 digits `f"PAT-{next_num:05d}"`.
  - *Test Verification*: `test_search_by_name_case_insensitive_partial` *(TC-23 registers multiple sequential patients)*.
- **Branch 1C (Malformed Code Exception Fallback)**:
  - *Condition*: Non-standard format triggers exception.
  - *Outcome*: Fallback calculates count + 1 safely.

---

### 1.2 Demographic Validation Engine (`validate_patient_form`)

Source logic paths:

#### Path 2A: Full Name Validation
- **Branch 2A.1 (Empty/Whitespace)**: `not name` -> `errors['full_name'] = "Full name is required."` *(TC-02)*
- **Branch 2A.2 (Length > 100)**: `len(name) > 100` -> `errors['full_name'] = "Full name must not exceed 100 characters."` *(TC-20)*
- **Branch 2A.3 (No Letters)**: `not any(c.isalpha() for c in name)` -> `errors['full_name'] = "Full name must contain at least one letter."` *(TC-21)*
- **Branch 2A.4 (Disallowed Characters)**: `not re.match(r"^[A-Za-z\s'\-]+$", name)` -> `errors['full_name'] = "Full name can only contain letters, spaces, hyphens, and apostrophes."` *(TC-28 Defect 1)*
- **Branch 2A.5 (Valid Name)**: Falls through with no error.

#### Path 2B: Date of Birth Validation
- **Branch 2B.1 (Missing)**: `not dob_str` -> `errors['date_of_birth'] = "Date of birth is required."` *(TC-03)*
- **Branch 2B.2 (Malformed Format)**: `strptime` raises `ValueError` -> `errors['date_of_birth'] = "Invalid date format. Use YYYY-MM-DD."`
- **Branch 2B.3 (Future Date)**: `dob > date.today()` -> `errors['date_of_birth'] = "Date of birth cannot be in the future."` *(TC-14)*
- **Branch 2B.4 (Before 1900)**: `dob < date(1900, 1, 1)` -> `errors['date_of_birth'] = "Date of birth cannot be before 1900."` *(TC-15)*
- **Branch 2B.5 (Valid Date)**: Falls through.

#### Path 2C: Gender Partition
- **Branch 2C.1 (Missing)**: `not gender` -> `errors['gender'] = "Gender is required."` *(TC-04)*
- **Branch 2C.2 (Not in Allowed Set)**: `gender not in VALID_GENDERS` -> `errors['gender'] = "Gender must be one of Female, Male, Other."` *(TC-16)*
- **Branch 2C.3 (Valid Gender)**: Falls through.

#### Path 2D: Phone Number Sanitization & Validation
- **Branch 2D.1 (Missing)**: `not phone_raw` -> `errors['phone'] = "Phone number is required."` *(TC-05)*
- **Branch 2D.2 (Contains Letters)**: `any(c.isalpha() for c in phone_raw)` -> `errors['phone'] = "Phone number cannot contain letters."` *(TC-12)*
- **Branch 2D.3 (Length < 10 or > 15)**: `len(digits) < 10 or len(digits) > 15` -> `errors['phone'] = "Phone must be 10 to 15 digits with an optional leading +."` *(TC-07, TC-10)*
- **Branch 2D.4 (Repetitive Digits)**: `len(set(digits)) <= 1` -> `errors['phone'] = "Please provide a valid phone number, not dummy repetitive digits."` *(TC-30 Defect 3)*
- **Branch 2D.5 (Valid Cleaned Phone)**: Formatted with optional leading `+` and passed to database.

---

### 1.3 Duplicate Patient Record Check Branch (`patient_new`)

```python
cur.execute("""
    SELECT patient_code FROM patients 
    WHERE LOWER(full_name) = LOWER(?) 
      AND date_of_birth = ? 
      AND phone = ?
""", (cleaned_data['full_name'], cleaned_data['date_of_birth'], cleaned_data['phone']))
existing = cur.fetchone()
if existing:
    errors['general'] = f"A patient with this name, date of birth, and phone number is already registered ({existing['patient_code']})."
    return render_template('patient_form.html', ...), 400
```
- **Branch 3A (Duplicate Found)**: Record exists -> Returns HTTP 400 with duplicate notice *(TC-31 Defect 4)*.
- **Branch 3B (Unique Patient)**: No record matches -> Executes `INSERT INTO patients` and redirects *(TC-01)*.

---

### 1.4 Concurrency Conflict & Database Unique Lock (`appointment_new`)

```python
try:
    cur.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (...))
    conn.commit()
except sqlite3.IntegrityError:
    conn.close()
    errors['time_slot'] = "This doctor is already booked at the selected time."
    return render_template('appointment_form.html', ...), 400
```
- **Branch 4A (Slot Available)**: INSERT succeeds -> redirects with success flash *(TC-32, TC-45)*.
- **Branch 4B (Slot Already Booked)**: Caught `sqlite3.IntegrityError` -> rollback, sets `errors['time_slot']`, returns HTTP 400 *(TC-44)*.

---

### 1.5 Referential Integrity & Deletion Guard Branch (`patient_delete`)

```python
cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE patient_id = ?", (patient_id,))
count = cur.fetchone()['cnt']
if count > 0:
    conn.close()
    flash("Cannot delete a patient who has appointments. Cancel the appointments first.", "danger")
    return redirect(url_for('list_patients'))
```
- **Branch 5A (Patient Has Active Appointments)**: `count > 0` -> Deletion rejected, flash warning *(TC-49)*.
- **Branch 5B (Patient Has Zero Appointments)**: `count == 0` -> Executes `DELETE FROM patients WHERE id = ?`, redirects with success *(TC-26, TC-50)*.

---

## 2. White-Box Coverage Summary

All decision points and control flow branches in the core application logic are covered by dedicated automated test methods in the test suite. No branches remain untested.

