# Hospital Management System (HMS) - Genuine Defect Log

**Jira Project Key**: `SCRUM`  
**All Defects**: Discovered during exploratory and automated testing of Module 1 and Module 2.  
**Resolution**: 100% Fixed and Retested OK.

---

## Defect Summary Table

| Defect Key | Linked Epic / Story | Summary | Severity | Commit Fix | Retest Status |
|---|---|---|:---:|:---:|:---:|
| **BUG-01** | SCRUM-9 (SCRUM-11) | Patient full name accepted symbols and digits (`R2D2!!`) | Medium | `9367a86` | **Retested OK (TC-28)** |
| **BUG-02** | SCRUM-9 (SCRUM-8) | Search query treated `%` and `_` as SQL wildcards instead of literal characters | High | `9367a86` | **Retested OK (TC-29)** |
| **BUG-03** | SCRUM-9 (SCRUM-11) | Phone number validation accepted dummy repetitive digits (`0000000000`) | Low | `9367a86` | **Retested OK (TC-30)** |
| **BUG-04** | SCRUM-9 (SCRUM-7) | Duplicate patient registration allowed for identical Name, DOB, and Phone | High | `9367a86` | **Retested OK (TC-31)** |

---

## Detailed Bug Reports

### Bug 1: Patient Name Accepted Symbols and Numbers
- **Jira Key**: `SCRUM-Bug-1` / `BUG-01`
- **Epic**: `SCRUM-9` (Module 1: Patient Registration and Management)
- **Affects Story**: `SCRUM-11` (Patient Data Validation)
- **Summary**: Full name field allowed non-alphabetic characters such as digits and exclamation marks.
- **Steps to Reproduce**:
  1. Navigate to `/patients/new`.
  2. Fill in Legal Full Name as `"R2D2!!"`.
  3. Enter valid Date of Birth (`1995-03-20`), Gender (`Other`), Phone (`9876543210`), and Address.
  4. Submit form.
- **Expected Result**: Validation rejects `"R2D2!!"` with message: *"Full name can only contain letters, spaces, hyphens, and apostrophes."* (HTTP 400).
- **Actual Result**: Patient was accepted and assigned an ID.
- **Severity**: Medium
- **Fix Implementation**: Added regex rule `re.match(r"^[A-Za-z\s'\-]+$", name)` and validation test `test_defect_1_name_accepting_symbols_and_numbers` in `tests/test_defects.py`.
- **Status**: Fixed in commit `9367a86`, retested OK (TC-28 passed).

---

### Bug 2: Directory Search SQL Wildcard Leakage
- **Jira Key**: `SCRUM-Bug-2` / `BUG-02`
- **Epic**: `SCRUM-9` (Module 1: Patient Registration and Management)
- **Affects Story**: `SCRUM-8` (View and Search Patient Records)
- **Summary**: Querying `%` or `_` acted as SQL wildcard pattern matchers rather than literal characters.
- **Steps to Reproduce**:
  1. Register two patients without `%` in their name (e.g., Alice Regular, Bob Normal).
  2. Navigate to `/patients?q=%`.
- **Expected Result**: 0 results returned because no patient code or name contains a literal percent sign.
- **Actual Result**: SQL `LIKE ?` evaluated `%` as wildcard matching every record, dumping the entire patient directory.
- **Severity**: High (Information Disclosure)
- **Fix Implementation**: Sanitized search parameter by escaping `%` to `\%` and `_` to `\_` with explicit `ESCAPE '\'` in SQL queries.
- **Status**: Fixed in commit `9367a86`, retested OK (TC-29 passed).

---

### Bug 3: Acceptance of Dummy Repetitive Phone Numbers
- **Jira Key**: `SCRUM-Bug-3` / `BUG-03`
- **Epic**: `SCRUM-9` (Module 1: Patient Registration and Management)
- **Affects Story**: `SCRUM-11` (Patient Data Validation)
- **Summary**: Entering dummy repetitive digits such as `0000000000` was accepted because length was 10 digits.
- **Steps to Reproduce**:
  1. Navigate to `/patients/new`.
  2. Submit form with phone number `0000000000`.
- **Expected Result**: System rejects dummy non-telecom numbers.
- **Actual Result**: Accepted as a valid phone number.
- **Severity**: Low
- **Fix Implementation**: Added check `if len(set(cleaned_digits)) <= 1: errors['phone'] = "Please provide a valid phone number, not dummy repetitive digits."`.
- **Status**: Fixed in commit `9367a86`, retested OK (TC-30 passed).

---

### Bug 4: Duplicate Patient Profile Creation
- **Jira Key**: `SCRUM-Bug-4` / `BUG-04`
- **Epic**: `SCRUM-9` (Module 1: Patient Registration and Management)
- **Affects Story**: `SCRUM-7` (Patient Registration)
- **Summary**: The system created multiple active records for identical individuals submitting the same Name, Date of Birth, and Phone Number.
- **Steps to Reproduce**:
  1. Register patient "Bruce Wayne", DOB `1980-05-27`, Phone `9876543210`.
  2. Re-submit the exact same form.
- **Expected Result**: System detects collision and blocks duplicate registration citing existing patient ID.
- **Actual Result**: Duplicate record created with new ID `PAT-00002`.
- **Severity**: High (Data Integrity & Relational Collisions)
- **Fix Implementation**: Pre-insert database uniqueness check querying `WHERE LOWER(full_name) = LOWER(?) AND date_of_birth = ? AND phone = ?`.
- **Status**: Fixed in commit `9367a86`, retested OK (TC-31 passed).

