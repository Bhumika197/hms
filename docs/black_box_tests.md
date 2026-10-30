# Hospital Management System (HMS) - Black-Box Testing Specification

**Test Techniques Applied**: Boundary Value Analysis (BVA), Equivalence Partitioning (EP), and State Transition Testing.

---

## 1. Boundary Value Analysis (BVA)

Boundary Value Analysis tests inputs at the extreme outer edges, exact boundary transitions, and immediate invalid values outside acceptable partitions.

### 1.1 Phone Number Length (Permitted: 10 to 15 digits)
- **Lower Edge Invalid (9 digits)**: `"123456789"` -> **Rejected (HTTP 400)** *(TC-07)*
- **Lower Boundary Valid (10 digits)**: `"1234567890"` -> **Accepted (HTTP 302)** *(TC-08)*
- **Upper Boundary Valid (15 digits)**: `"123456789012345"` -> **Accepted (HTTP 302)** *(TC-09)*
- **Upper Edge Invalid (16 digits)**: `"1234567890123456"` -> **Rejected (HTTP 400)** *(TC-10)*

### 1.2 Patient Date of Birth (Permitted: 1900-01-01 to Today)
- **Lower Edge Invalid (Before 1900)**: `"1899-12-31"` -> **Rejected (HTTP 400)** *(TC-15)*
- **Lower Boundary Valid**: `"1900-01-01"` -> **Accepted (HTTP 302)**
- **Upper Boundary Valid**: `Today's Date` -> **Accepted (HTTP 302)**
- **Upper Edge Invalid (Future Date)**: `Tomorrow's Date` -> **Rejected (HTTP 400)** *(TC-14)*

### 1.3 Full Name Length (Permitted: 1 to 100 characters)
- **Minimum Boundary (1 char)**: `"A"` -> **Accepted (HTTP 302)**
- **Maximum Boundary (100 chars)**: `'A' * 100` -> **Accepted (HTTP 302)** *(TC-19)*
- **Upper Edge Invalid (101 chars)**: `'A' * 101` -> **Rejected (HTTP 400)** *(TC-20)*

### 1.4 Appointment Date (Permitted: Today and Future)
- **Past Date Invalid**: `Yesterday's Date` -> **Rejected (HTTP 400)** *(TC-38)*
- **Current Day Boundary**: `Today's Date` -> **Accepted (HTTP 302)** *(TC-39)*
- **Future Date Valid**: `Tomorrow's Date` -> **Accepted (HTTP 302)**

### 1.5 Address Character Length (Permitted: 15 to 300 characters)
- **Lower Edge Invalid (14 chars)**: ""12345678901234"" -> **Rejected (HTTP 400)** *(TC-54)*
- **Lower Boundary Valid (15 chars)**: ""123456789012345"" -> **Accepted (HTTP 302)** *(TC-55)*
- **Upper Boundary Valid (300 chars)**: 'A' * 300 -> **Accepted (HTTP 302)**
- **Upper Edge Invalid (301 chars)**: 'A' * 301 -> **Rejected (HTTP 400)**

### 1.6 Clinic Operating Time Slots (Permitted: 09:00 to 16:30)
- **Opening Time Slot Boundary**: `"09:00"` -> **Accepted (HTTP 302)** *(TC-43)*
- **Closing Time Slot Boundary**: `"16:30"` -> **Accepted (HTTP 302)** *(TC-43)*
- **Pre-Opening Invalid Slot**: `"08:30"` -> **Rejected (HTTP 400)** *(TC-42)*
- **Post-Closing Invalid Slot**: `"17:00"` -> **Rejected (HTTP 400)**

---

## 2. Equivalence Partitioning (EP)

Equivalence Partitioning divides the input domain into classes of valid and invalid data where all values within a class are expected to be treated equivalently.

### 2.1 Gender Classification
- **Valid Class 1**: `"Female"` -> Accepted *(TC-01)*
- **Valid Class 2**: `"Male"` -> Accepted *(TC-31)*
- **Valid Class 3**: `"Other"` -> Accepted *(TC-28)*
- **Invalid Class**: Non-standard strings (`"Unknown"`, `"Robot"`, `"N/A"`) -> Rejected with *"Gender must be one of Female, Male, Other"* *(TC-16)*

### 2.2 Electronic Mail Formatting
- **Valid RFC Format**: `"patient@hospital.org"`, `"name.surname@domain.co.uk"` -> Accepted *(TC-01)*
- **Valid Empty Option**: `""` (omitted) -> Accepted with database value stored as `NULL` *(TC-18)*
- **Invalid Syntax**: `"not-an-email"`, `"missing@domain"`, `"@domain.com"` -> Rejected with *"Invalid email format."* *(TC-17)*

### 2.3 International Telecom Formats
- **Standard Digits**: `"9876543210"` -> Cleaned and accepted *(TC-08)*
- **International Leading Plus**: `"+19876543210"` -> Sanitized while retaining leading `+` *(TC-11)*
- **Invalid Alphabetic Injection**: `"987654ABCD"` -> Rejected with *"Phone number cannot contain letters."* *(TC-12)*
- **Formatting Characters**: `"(555) 234-5678"` -> Stripped of parentheses and spaces -> `"5552345678"` *(TC-13)*

### 2.4 Patient Existence for Appointment Booking
- **Valid Existing Patient Code**: Registered in SQLite (`"PAT-00001"`) -> Proceed to appointment booking *(TC-32)*
- **Invalid Unknown Patient Code**: Not present in SQLite (`"PAT-99999"`) -> Rejected with *"Unknown patient ID."* *(TC-33)*

### 2.5 Attending Physician Selection
- **Valid Rostered Doctor**: ID corresponding to seeded doctors (1 through 5) -> Consultation allocated *(TC-32)*
- **Invalid Doctor ID**: Out-of-bounds integer (`9999`) -> Rejected with *"Selected doctor does not exist."* *(TC-36)*

---

## 3. Summary of Black-Box Verification Coverage

| Feature Tested | BVA Coverage | EP Coverage | Total Test Cases | Result |
|---|:---:|:---:|:---:|:---:|
| Patient Full Name | 100, 101 chars | Letters vs symbols/numbers | 4 | **100% Pass** |
| Date of Birth | 1899, 1900, Today, Tomorrow | Valid YYYY-MM-DD vs invalid | 4 | **100% Pass** |
| Phone Number | 9, 10, 15, 16 digits | Formatting, international, alpha | 7 | **100% Pass** |
| Gender Identity | — | Female, Male, Other vs Invalid | 2 | **100% Pass** |
| Email Address | Max length 254 | Valid, malformed, empty | 3 | **100% Pass** |
| Address | Max length 300 | Valid string vs empty | 2 | **100% Pass** |
| Directory Search | — | Exact ID, partial name, literal wildcards | 3 | **100% Pass** |
| Appointment Slot | 09:00, 16:30 | 16 valid slots vs unlisted | 4 | **100% Pass** |
| Appointment Date | Yesterday, Today | Valid vs malformed date string | 3 | **100% Pass** |
| Doctor Allocation | Valid roster IDs | Existing vs non-existent | 2 | **100% Pass** |
| Concurrency Guard | Same doc/time/date | Colliding slot vs distinct doc slot | 2 | **100% Pass** |

