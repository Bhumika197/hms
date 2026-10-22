# Hospital Management System (HMS) - Test Cases & Verification Report

## 1. Test Execution Summary
- **Execution Date**: October 22, 2026
- **Test Framework**: Python `unittest` standard module
- **Test Execution Command**: `python -m unittest discover -s tests -v`
- **Total Test Cases**: 31
- **Passed**: 31
- **Failed**: 0
- **Status**: 100% Passed

---

## 2. Test Cases Table

| Test Case ID | Module | Test Scenario | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| **TC-01** | Module 1: Patient Registration | Valid patient registration and unique ID generation | Name: Eleanor Vance, DOB: 1992-05-14, Gender: Female, Phone: 9876543210, Email: eleanor@example.com, Address: 742 Evergreen Terrace | Record saved, redirected to `/patients`, unique ID `PAT-00001` assigned | HTTP 302, patient stored in SQLite, patient_code `PAT-00001` verified | **Pass** |
| **TC-02** | Module 1: Patient Registration | Validation for missing required full_name | `full_name: ""` | Form rejected with error "Full name is required." | HTTP 400, "Full name is required." rendered under field | **Pass** |
| **TC-03** | Module 1: Patient Registration | Validation for missing required date_of_birth | `date_of_birth: ""` | Form rejected with error "Date of birth is required." | HTTP 400, "Date of birth is required." rendered under field | **Pass** |
| **TC-04** | Module 1: Patient Registration | Validation for missing required gender | `gender: ""` | Form rejected with error "Gender is required." | HTTP 400, "Gender is required." rendered under field | **Pass** |
| **TC-05** | Module 1: Patient Registration | Validation for missing required phone number | `phone: ""` | Form rejected with error "Phone number is required." | HTTP 400, "Phone number is required." rendered under field | **Pass** |
| **TC-06** | Module 1: Patient Registration | Validation for missing required address | `address: ""` | Form rejected with error "Address is required." | HTTP 400, "Address is required." rendered under field | **Pass** |
| **TC-07** | Module 1: Patient Registration | Phone boundary analysis: 9 digits (below minimum) | `phone: "123456789"` | Form rejected with "Phone must be 10 to 15 digits with an optional leading +." | HTTP 400, error message displayed | **Pass** |
| **TC-08** | Module 1: Patient Registration | Phone boundary analysis: 10 digits (minimum length) | `phone: "1234567890"` | Registration succeeds | HTTP 302, record saved with 10-digit phone | **Pass** |
| **TC-09** | Module 1: Patient Registration | Phone boundary analysis: 15 digits (maximum length) | `phone: "123456789012345"` | Registration succeeds | HTTP 302, record saved with 15-digit phone | **Pass** |
| **TC-10** | Module 1: Patient Registration | Phone boundary analysis: 16 digits (above maximum) | `phone: "1234567890123456"` | Form rejected with "Phone must be 10 to 15 digits with an optional leading +." | HTTP 400, error message displayed | **Pass** |
| **TC-11** | Module 1: Patient Registration | International phone format with leading plus | `phone: "+19876543210"` | Registration succeeds | HTTP 302, record stored | **Pass** |
| **TC-12** | Module 1: Patient Registration | Phone input containing alphabetic letters | `phone: "987654ABCD"` | Form rejected with "Phone number cannot contain letters." | HTTP 400, error message displayed | **Pass** |
| **TC-13** | Module 1: Patient Registration | Phone formatting sanitization (spaces, dashes, brackets) | `phone: "(555) 234-5678"` | Sanitized to `5552345678` and stored cleanly | HTTP 302, stored phone is `5552345678` | **Pass** |
| **TC-14** | Module 1: Patient Registration | Date of birth boundary: future date | `date_of_birth: tomorrow` | Form rejected with "Date of birth cannot be in the future." | HTTP 400, error message displayed | **Pass** |
| **TC-15** | Module 1: Patient Registration | Date of birth boundary: date before year 1900 | `date_of_birth: "1899-12-31"` | Form rejected with "Date of birth cannot be before 1900." | HTTP 400, error message displayed | **Pass** |
| **TC-16** | Module 1: Patient Registration | Gender partition: invalid gender option | `gender: "Unknown"` | Form rejected with "Gender must be one of Female, Male, Other." | HTTP 400, error message displayed | **Pass** |
| **TC-17** | Module 1: Patient Registration | Email partition: malformed email format | `email: "not-an-email-at-all"` | Form rejected with "Invalid email format." | HTTP 400, error message displayed | **Pass** |
| **TC-18** | Module 1: Patient Registration | Email partition: optional field omitted | `email: ""` | Registration succeeds with email set to NULL | HTTP 302, record created | **Pass** |
| **TC-19** | Module 1: Patient Registration | Name length boundary: exactly 100 characters | `full_name: 'A' * 100` | Registration succeeds | HTTP 302, record created | **Pass** |
| **TC-20** | Module 1: Patient Registration | Name length boundary: 101 characters | `full_name: 'A' * 101` | Form rejected with "Full name must not exceed 100 characters." | HTTP 400, error message displayed | **Pass** |
| **TC-21** | Module 1: Patient Registration | Name character validation: no alphabetic letters | `full_name: "12345678"` | Form rejected with "Full name must contain at least one letter." | HTTP 400, error message displayed | **Pass** |
| **TC-22** | Module 1: Patient Management | Search directory by exact Patient ID | `q="PAT-00001"` | Returns only patient matching ID | HTTP 200, matching patient rendered in table | **Pass** |
| **TC-23** | Module 1: Patient Management | Search directory by partial name (case-insensitive) | `q="arth"` (Patient: "Arthur Dent") | Case-insensitive partial match displayed | HTTP 200, Arthur Dent displayed | **Pass** |
| **TC-24** | Module 1: Patient Management | Edit patient record with valid data | Full name updated from "Original Name" to "Updated Name" | Record updated in SQLite, redirected with flash message | HTTP 302, DB record updated | **Pass** |
| **TC-25** | Module 1: Patient Management | Edit patient validation failure | Empty full_name on edit submission | Form rejected, DB record remains unmodified | HTTP 400, original DB value unchanged | **Pass** |
| **TC-26** | Module 1: Patient Management | Delete patient record without appointments | POST to `/patients/<id>/delete` | Patient removed from SQLite, redirected to list | HTTP 302, patient record deleted | **Pass** |
| **TC-27** | Module 1: Patient Management | Access non-existent patient ID | GET `/patients/99999/edit` | Returns 404 Not Found error page | HTTP 404, custom 404 template rendered | **Pass** |
| **TC-28** | Module 1: Patient Registration | Defect Test: Name containing symbols and digits | `full_name: "R2D2!!"` | Form rejected with "Full name can only contain letters, spaces, hyphens, and apostrophes." | HTTP 400, error message displayed | **Pass** |
| **TC-29** | Module 1: Patient Management | Defect Test: Search treating `%` or `_` as literal characters | `q="%"` | SQL wildcards escaped; no unintended patients matched | HTTP 200, no unintended patients returned | **Pass** |
| **TC-30** | Module 1: Patient Registration | Defect Test: Dummy repetitive phone numbers | `phone: "0000000000"` | Form rejected with "Please provide a valid phone number, not dummy repetitive digits." | HTTP 400, error message displayed | **Pass** |
| **TC-31** | Module 1: Patient Registration | Defect Test: Duplicate patient registration prevention | Same name, date of birth, and phone number | Form rejected with warning citing existing patient code | HTTP 400, duplicate warning rendered | **Pass** |

---

## 3. Testing Techniques Employed

1. **Boundary Value Analysis (BVA)**:
   - Phone length boundaries at 9, 10, 15, and 16 digits (TC-07, TC-08, TC-09, TC-10).
   - Date of birth upper limit (today vs. tomorrow) and lower limit (1900 vs. 1899) (TC-14, TC-15).
   - Full name character length at 100 characters vs. 101 characters (TC-19, TC-20).

2. **Equivalence Partitioning (EP)**:
   - Valid vs. invalid gender classes (`Female`, `Male`, `Other` vs. `Unknown`) (TC-16).
   - Valid email formatting vs. malformed email string vs. omitted optional email (TC-17, TC-18).
   - Valid alphanumeric formats and international leading `+` phone numbers (TC-11, TC-12).

3. **Functional & Workflow Testing**:
   - Patient registration lifecycle, auto-generation of ID (`PAT-00001`) (TC-01).
   - Patient directory searching by ID and partial name (TC-22, TC-23).
   - Record editing and record deletion (TC-24, TC-26, TC-27).

4. **Input Validation & Data Sanitization**:
   - Enforcement of non-empty required fields (TC-02 to TC-06).
   - Stripping spaces, hyphens, brackets, and periods from phone numbers (TC-13).
   - Alphabetic name integrity validation (TC-21, TC-28).

5. **Security & Defect Regression Testing**:
   - SQL wildcard character escaping in search queries (TC-29).
   - Prevention of bogus repetitive phone entries (TC-30).
   - Duplicate medical profile prevention (TC-31).
