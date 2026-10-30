# Hospital Management System (HMS) - Real Test Cases & Execution Report

**Execution Command**: `python -m unittest discover -s tests -v`  
**Execution Timestamp**: October 30, 2026  
**Total Tests**: 55 | **Passed**: 55 | **Failed**: 0 | **Pass Rate**: 100%  
**Output Log**: [`docs/test_run.txt`](test_run.txt)

---

## Complete Test Cases Table

| ID | Story Key | Input / Scenario | Expected Result | ACTUAL Result | Status |
|---|---|---|---|---|:---:|
| **TC-01** | SCRUM-7 | Valid registration: Eleanor Vance, DOB 1992-05-14, Female, 9876543210, eleanor@example.com, address | HTTP 302, stored in DB, `patient_code` PAT-00001 assigned | HTTP 302, record stored with PAT-00001 | **Pass** |
| **TC-02** | SCRUM-11 | Missing required `full_name` ("") | HTTP 400, "Full name is required." | HTTP 400, "Full name is required." rendered | **Pass** |
| **TC-03** | SCRUM-11 | Missing required `date_of_birth` ("") | HTTP 400, "Date of birth is required." | HTTP 400, "Date of birth is required." rendered | **Pass** |
| **TC-04** | SCRUM-11 | Missing required `gender` ("") | HTTP 400, "Gender is required." | HTTP 400, "Gender is required." rendered | **Pass** |
| **TC-05** | SCRUM-11 | Missing required `phone` ("") | HTTP 400, "Phone number is required." | HTTP 400, "Phone number is required." rendered | **Pass** |
| **TC-06** | SCRUM-11 | Missing required `address` ("") | HTTP 400, "Address is required." | HTTP 400, "Address is required." rendered | **Pass** |
| **TC-07** | SCRUM-11 | Phone BVA: 9 digits (`123456789`) below minimum | HTTP 400, "Phone must be 10 to 15 digits" | HTTP 400, error message displayed | **Pass** |
| **TC-08** | SCRUM-11 | Phone BVA: 10 digits (`1234567890`) minimum boundary | HTTP 302, patient registered successfully | HTTP 302, record created in DB | **Pass** |
| **TC-09** | SCRUM-11 | Phone BVA: 15 digits (`123456789012345`) max boundary | HTTP 302, patient registered successfully | HTTP 302, record created in DB | **Pass** |
| **TC-10** | SCRUM-11 | Phone BVA: 16 digits (`1234567890123456`) above max | HTTP 400, "Phone must be 10 to 15 digits" | HTTP 400, error message displayed | **Pass** |
| **TC-11** | SCRUM-11 | Phone EP: International phone with leading plus (`+19876543210`) | HTTP 302, record stored | HTTP 302, record saved with + | **Pass** |
| **TC-12** | SCRUM-11 | Phone EP: Phone with alphabetic letters (`987654ABCD`) | HTTP 400, "Phone number cannot contain letters" | HTTP 400, error message displayed | **Pass** |
| **TC-13** | SCRUM-7 | Phone sanitization: Formatting spaces and brackets `(555) 234-5678` | Sanitized to digits `5552345678` and saved | HTTP 302, DB contains `5552345678` | **Pass** |
| **TC-14** | SCRUM-11 | DOB BVA: Date of birth tomorrow (future date) | HTTP 400, "Date of birth cannot be in the future" | HTTP 400, error message displayed | **Pass** |
| **TC-15** | SCRUM-11 | DOB BVA: Date of birth before 1900 (`1899-12-31`) | HTTP 400, "Date of birth cannot be before 1900" | HTTP 400, error message displayed | **Pass** |
| **TC-16** | SCRUM-11 | Gender EP: Invalid gender partition (`Unknown`) | HTTP 400, "Gender must be one of Female, Male, Other" | HTTP 400, error message displayed | **Pass** |
| **TC-17** | SCRUM-11 | Email EP: Malformed email string (`not-an-email`) | HTTP 400, "Invalid email format" | HTTP 400, error message displayed | **Pass** |
| **TC-18** | SCRUM-11 | Email EP: Optional email omitted ("") | HTTP 302, record saved with NULL email | HTTP 302, DB email is NULL | **Pass** |
| **TC-19** | SCRUM-11 | Name BVA: Exactly 100 alphabetic characters | HTTP 302, record saved | HTTP 302, record created | **Pass** |
| **TC-20** | SCRUM-11 | Name BVA: 101 characters exceeding boundary | HTTP 400, "Full name must not exceed 100 characters" | HTTP 400, error message displayed | **Pass** |
| **TC-21** | SCRUM-11 | Name character validation: digits only (`12345678`) | HTTP 400, "Full name must contain at least one letter" | HTTP 400, error message displayed | **Pass** |
| **TC-22** | SCRUM-8 | Search by exact Patient Code `q=PAT-00001` | HTTP 200, returns only patient matching ID | HTTP 200, matching patient rendered | **Pass** |
| **TC-23** | SCRUM-8 | Search by partial name case-insensitive `q=arth` | HTTP 200, matches "Arthur Dent" | HTTP 200, Arthur Dent displayed | **Pass** |
| **TC-24** | SCRUM-12 | Edit patient record with valid updated details | HTTP 302, database record updated | HTTP 302, SQLite row updated | **Pass** |
| **TC-25** | SCRUM-12 | Edit patient validation failure (empty full_name) | HTTP 400, original database values unmodified | HTTP 400, DB record unchanged | **Pass** |
| **TC-26** | SCRUM-8 | Delete patient without active appointments | HTTP 302, patient deleted from database | HTTP 302, row removed from SQLite | **Pass** |
| **TC-27** | SCRUM-8 | Access non-existent patient ID `/patients/99999/edit` | HTTP 404, custom 404 page rendered | HTTP 404, 404 template returned | **Pass** |
| **TC-28** | SCRUM-11 | Defect 1: Full name with symbols/numbers (`R2D2!!`) | HTTP 400, "letters, spaces, hyphens, and apostrophes" | HTTP 400, symbol name rejected | **Pass** |
| **TC-29** | SCRUM-8 | Defect 2: Search treating `%` or `_` as literal character | HTTP 200, `%` escapes wildcards; 0 records matched | HTTP 200, 0 unintended matches | **Pass** |
| **TC-30** | SCRUM-11 | Defect 3: Dummy repetitive phone (`0000000000`) | HTTP 400, "Please provide a valid phone number" | HTTP 400, dummy phone rejected | **Pass** |
| **TC-31** | SCRUM-7 | Defect 4: Duplicate patient registration attempt | HTTP 400, duplicate warning citing existing code | HTTP 400, duplicate blocked | **Pass** |
| **TC-32** | SCRUM-13 | Valid appointment booking for registered patient | HTTP 302, appointment stored in SQLite | HTTP 302, appointment created | **Pass** |
| **TC-33** | SCRUM-13 | Booking with unknown patient ID (`PAT-99999`) | HTTP 400, "Unknown patient ID.", 0 stored | HTTP 400, error displayed, 0 in DB | **Pass** |
| **TC-34** | SCRUM-13 | Missing patient ID validation | HTTP 400, "Patient ID is required." | HTTP 400, error message displayed | **Pass** |
| **TC-35** | SCRUM-14 | Missing doctor selection validation | HTTP 400, "Please select a doctor." | HTTP 400, error message displayed | **Pass** |
| **TC-36** | SCRUM-14 | Non-existent doctor ID (`9999`) | HTTP 400, "Selected doctor does not exist." | HTTP 400, error message displayed | **Pass** |
| **TC-37** | SCRUM-14 | Missing appointment date validation | HTTP 400, "Appointment date is required." | HTTP 400, error message displayed | **Pass** |
| **TC-38** | SCRUM-14 | BVA: Past appointment date (yesterday) | HTTP 400, "Appointment date cannot be in the past." | HTTP 400, error message displayed | **Pass** |
| **TC-39** | SCRUM-14 | BVA: Today appointment date | HTTP 302, appointment successfully scheduled | HTTP 302, appointment created | **Pass** |
| **TC-40** | SCRUM-14 | Invalid date format validation (`22-10-2026`) | HTTP 400, "Invalid date format. Use YYYY-MM-DD." | HTTP 400, error message displayed | **Pass** |
| **TC-41** | SCRUM-14 | Missing appointment time slot validation | HTTP 400, "Appointment time is required." | HTTP 400, error message displayed | **Pass** |
| **TC-42** | SCRUM-14 | Invalid time slot partition (`08:45`) | HTTP 400, "Invalid time slot." | HTTP 400, error message displayed | **Pass** |
| **TC-43** | SCRUM-14 | BVA: Boundary slots opening 09:00 & closing 16:30 | HTTP 302 for both boundary slots | HTTP 302 for both bookings | **Pass** |
| **TC-44** | SCRUM-15 | Duplicate booking conflict prevention (same doc/date/time) | HTTP 400, "This doctor is already booked at the selected time." | HTTP 400, conflict handled cleanly | **Pass** |
| **TC-45** | SCRUM-15 | Same time slot with different doctor | HTTP 302, both bookings accepted | HTTP 302 for both bookings | **Pass** |
| **TC-46** | SCRUM-16 | Appointment list ordering (Date ASC, Time ASC) | HTTP 200, rendered ascending chronologically | HTTP 200, order verified | **Pass** |
| **TC-47** | SCRUM-16 | Cancel existing appointment via POST | HTTP 302, appointment deleted from DB | HTTP 302, row removed from SQLite | **Pass** |
| **TC-48** | SCRUM-16 | Cancel non-existent appointment ID | HTTP 404, custom 404 page rendered | HTTP 404, 404 template returned | **Pass** |
| **TC-49** | Integration | Patient with active appointments deletion block | HTTP 200, deletion blocked with error | HTTP 200, patient remains in DB | **Pass** |
| **TC-50** | Integration | Cancel appointment unlocks patient deletion | HTTP 200, patient successfully deleted | HTTP 200, patient row deleted | **Pass** |
| **TC-51** | Integration | End-to-end full booking lifecycle with join data | HTTP 200, patient, doctor, specialization rendered | HTTP 200, all joined fields present | **Pass** |
| **TC-52** | Integration | Root redirect and navigation links integration | HTTP 302 to /patients, navbar links valid | HTTP 302 to /patients, verified | **Pass** |
| **TC-53** | Integration | Application 404 handling on unknown route | HTTP 404, custom 404 page rendered | HTTP 404, custom 404 template | **Pass** |


| **TC-54** | SCRUM-11 | Address BVA: 14 characters (12345678901234) below minimum | HTTP 400, "Address must be at least 15 characters." | HTTP 400, error message displayed | **Pass** |
| **TC-55** | SCRUM-11 | Address BVA: 15 characters (123456789012345) minimum boundary | HTTP 302, patient registered successfully | HTTP 302, record created in DB | **Pass** |