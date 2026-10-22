# Hospital Management System (HMS) - Comprehensive Test Cases & Verification Report

## 1. Test Execution Summary
- **Execution Date**: October 23, 2026
- **Test Framework**: Python `unittest` standard module
- **Test Execution Command**: `python -m unittest discover -s tests -v`
- **Total Test Cases**: 53
- **Passed**: 53
- **Failed**: 0
- **Status**: 100% Passed (OK)

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
| **TC-32** | Module 2: Appointment Management | Valid appointment booking for registered patient | Patient: `PAT-00001`, Doctor: 1, Date: Tomorrow, Time: "10:00" | Appointment created, redirected to `/appointments` | HTTP 302, record stored in SQLite | **Pass** |
| **TC-33** | Module 2: Appointment Management | Booking with unknown patient ID | `patient_code: "PAT-99999"` | Rejected with "Unknown patient ID.", 0 appointments created | HTTP 400, error message displayed, 0 in DB | **Pass** |
| **TC-34** | Module 2: Appointment Management | Missing patient ID validation | `patient_code: ""` | Rejected with "Patient ID is required." | HTTP 400, error message displayed | **Pass** |
| **TC-35** | Module 2: Appointment Management | Missing doctor selection | `doctor_id: ""` | Rejected with "Please select a doctor." | HTTP 400, error message displayed | **Pass** |
| **TC-36** | Module 2: Appointment Management | Non-existent doctor ID selection | `doctor_id: "9999"` | Rejected with "Selected doctor does not exist." | HTTP 400, error message displayed | **Pass** |
| **TC-37** | Module 2: Appointment Management | Missing appointment date validation | `appointment_date: ""` | Rejected with "Appointment date is required." | HTTP 400, error message displayed | **Pass** |
| **TC-38** | Module 2: Appointment Management | Past appointment date boundary | `appointment_date: yesterday` | Rejected with "Appointment date cannot be in the past." | HTTP 400, error message displayed | **Pass** |
| **TC-39** | Module 2: Appointment Management | Today appointment date boundary | `appointment_date: today` | Accepted and scheduled | HTTP 302, appointment created | **Pass** |
| **TC-40** | Module 2: Appointment Management | Invalid date format validation | `appointment_date: "22-10-2026"` | Rejected with "Invalid date format. Use YYYY-MM-DD." | HTTP 400, error message displayed | **Pass** |
| **TC-41** | Module 2: Appointment Management | Missing appointment time slot | `appointment_time: ""` | Rejected with "Appointment time is required." | HTTP 400, error message displayed | **Pass** |
| **TC-42** | Module 2: Appointment Management | Invalid time slot partition | `appointment_time: "08:45"` | Rejected with "Invalid time slot." | HTTP 400, error message displayed | **Pass** |
| **TC-43** | Module 2: Appointment Management | Boundary time slots (opening & closing) | Slots `09:00` and `16:30` | Both boundary slots accepted | HTTP 302 for both boundary slots | **Pass** |
| **TC-44** | Module 2: Appointment Management | Duplicate booking conflict prevention | Same doctor, date, and time (`11:00`) booked twice | Blocked with "This doctor is already booked at the selected time." | HTTP 400, IntegrityError handled cleanly | **Pass** |
| **TC-45** | Module 2: Appointment Management | Same time slot with different doctor | Doctor 1 and Doctor 2 at same date and `14:00` | Both bookings accepted | HTTP 302 for both bookings | **Pass** |
| **TC-46** | Module 2: Appointment Management | Appointment list ordering | Bookings on day 2 (10:00), day 1 (14:00), day 1 (09:30) | Table displays chronologically (Date ASC, Time ASC) | HTTP 200, output order verified | **Pass** |
| **TC-47** | Module 2: Appointment Management | Cancel appointment | POST to `/appointments/<id>/cancel` | Appointment deleted from SQLite, redirected to list | HTTP 302, record removed from DB | **Pass** |
| **TC-48** | Module 2: Appointment Management | Cancel non-existent appointment | POST to `/appointments/9999/cancel` | Returns 404 Not Found error | HTTP 404, custom 404 page | **Pass** |
| **TC-49** | Integration Rule | Patient with appointments deletion block | Patient has booked appointment, POST `/patients/<id>/delete` | Delete blocked with "Cannot delete a patient who has appointments. Cancel the appointments first." | HTTP 200, patient remains in DB | **Pass** |
| **TC-50** | Integration Rule | Cancel appointment unlocks patient deletion | Cancel appointment first, then delete patient | Patient successfully deleted | HTTP 200, patient record deleted | **Pass** |
| **TC-51** | Integration Rule | End-to-end full booking lifecycle with join data | Register patient -> Book appointment with Doctor Chang (General Physician) | Appointments table shows patient ID, patient name, doctor name, specialization, time | HTTP 200, all joined fields present | **Pass** |
| **TC-52** | Integration Rule | Root redirect and navigation integration | GET `/` | Redirects to `/patients`, navigation shows Patients and Appointments links | HTTP 302 to `/patients`, links verified | **Pass** |
| **TC-53** | Integration Rule | Application 404 handling | GET `/nonexistent-path-abc` | Custom 404 page rendered with status code 404 | HTTP 404, custom error page | **Pass** |

---

## 3. Testing Techniques Breakdown

1. **Boundary Value Analysis (BVA)**:
   - Phone length boundaries at 9, 10, 15, and 16 digits (TC-07, TC-08, TC-09, TC-10).
   - Date of birth upper limit (today vs. tomorrow) and lower limit (1900 vs. 1899) (TC-14, TC-15).
   - Full name character length at 100 characters vs. 101 characters (TC-19, TC-20).
   - Appointment date boundaries (past vs. today) (TC-38, TC-39).
   - Appointment operating hour boundaries (opening 09:00 vs. closing 16:30) (TC-43).

2. **Equivalence Partitioning (EP)**:
   - Valid vs. invalid gender classes (`Female`, `Male`, `Other` vs. `Unknown`) (TC-16).
   - Valid email formatting vs. malformed email string vs. omitted optional email (TC-17, TC-18).
   - Valid alphanumeric formats and international leading `+` phone numbers (TC-11, TC-12).
   - Unknown patient ID partition on booking (TC-33).
   - Valid vs. invalid time slots (TC-41, TC-42).
   - Valid vs. non-existent doctor ID partition (TC-35, TC-36).

3. **Functional & Workflow Testing**:
   - Patient registration lifecycle, auto-generation of ID (`PAT-00001`) (TC-01).
   - Patient directory searching by ID and partial name (TC-22, TC-23).
   - Record editing and record deletion (TC-24, TC-26, TC-27).
   - Appointment booking, listing, and cancellation (TC-32, TC-46, TC-47).

4. **Integration & Business Rules**:
   - Foreign key constraint & deletion lock: Patient with appointments cannot be deleted (TC-49).
   - Workflow unlocking: Cancel appointment enables patient deletion (TC-50).
   - Multi-table relational joining: Patient, Doctor, Appointment fields rendered together (TC-51).
   - Routing and navigation integrity (TC-52, TC-53).

5. **Security & Defect Regression Testing**:
   - Name character integrity preventing symbols/numbers like "R2D2!!" (TC-28).
   - SQL wildcard character escaping in search queries (`%`, `_`) (TC-29).
   - Dummy repetitive phone number rejection (`0000000000`) (TC-30).
   - Duplicate medical profile detection (TC-31).
   - Double-booking concurrency/conflict rejection for the same doctor, date, and time (TC-44, TC-45).
