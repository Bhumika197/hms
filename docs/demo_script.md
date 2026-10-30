# Hospital Management System (HMS) - Viva Demo Presentation Script

A structured 10-step demonstration walkthrough for college Project-Based Learning (PBL) examination and viva. Each step includes an exact one-line script to say aloud to the examiner, followed by the exact screen action.

---

## 10-Step Viva Demo Script

### Step 1: Show Jira Backlog and Epics
- **Action**: Open Jira and show the Backlog view displaying Epic `SCRUM-9` (Module 1) and Epic `SCRUM-10` (Module 2) with all user stories organized underneath.
- **Spoken Line (Say out loud)**:  
  *"We organized the entire project in Jira into two main epics—Module 1 for Patient Management and Module 2 for Appointments—broken down into clear user stories and sub-tasks."*

---

### Step 2: Show Board and Sprint
- **Action**: Switch to the Active Sprint board in Jira showing all stories, tasks, code reviews, and test cases transitioned across columns to Done.
- **Spoken Line (Say out loud)**:  
  *"Our active sprint board tracks each story from planning through development, peer code review, and automated testing to completion with full evidence."*

---

### Step 3: Register a Patient (PAT- ID Appears)
- **Action**: In the web app, click **+ Register Patient**, enter patient details ("Eleanor Vance", DOB `1992-05-14`, Female, `9876543210`, address), and submit. Show that `PAT-00001` is automatically generated and displayed in the table.
- **Spoken Line (Say out loud)**:  
  *"When we register a new patient with validated demographics, the backend automatically assigns an immutable, zero-padded unique code like PAT-00001."*

---

### Step 4: Search by Name and ID
- **Action**: Type `PAT-00001` into the search bar, click Search (shows only that patient), then search by partial name `Eleanor` (shows case-insensitive match), then demonstrate wildcard safety.
- **Spoken Line (Say out loud)**:  
  *"The patient directory supports fast case-insensitive search by either Patient ID or partial name, protected against SQL wildcard injection."*

---

### Step 5: Book an Appointment
- **Action**: Click **Appointments** -> **+ Book Appointment**. Enter `PAT-00001`, select Dr. Michael Chang (General Physician), pick tomorrow's date, and select the `10:00` slot. Confirm booking.
- **Spoken Line (Say out loud)**:  
  *"Here we schedule a 30-minute consultation slot by linking the registered patient ID with our specialist doctor on tomorrow's roster."*

---

### Step 6: Book the Same Slot Again (Blocked)
- **Action**: Re-open the booking form, attempt to book Dr. Michael Chang for the exact same date and `10:00` time slot. Submit. Show the red error message: *"This doctor is already booked at the selected time."*
- **Spoken Line (Say out loud)**:  
  *"Attempting to double-book the same doctor at the same date and time is instantly rejected by our database-level unique constraint to guarantee zero scheduling conflicts."*

---

### Step 7: Show the Bug, Its Fix, and Retest
- **Action**: Open `docs/bug_log.md` and show the defect where search previously leaked records on `%` query, and explain the code fix in `app.py` escaping SQL wildcards, verified by `test_defect_2_search_wildcard_percent_and_underscore`.
- **Spoken Line (Say out loud)**:  
  *"During testing, we discovered that unescaped search wildcards leaked records; we fixed it with literal escaping and verified the fix with automated regression test TC-29."*

---

### Step 8: Run the Tests Live
- **Action**: Switch to the terminal and execute:  
  `python -m unittest discover -s tests -v`  
  Show all 53 tests executing and finishing with `OK`. Click the **📋 Test Cases (53)** button in the app header to show the examiner the in-app verification matrix.
- **Spoken Line (Say out loud)**:  
  *"Our automated test suite runs 53 comprehensive unit, boundary value, defect, and integration tests in under 3 seconds with a 100% pass rate."*

---

### Step 9: Show GitHub Commits with SCRUM Keys
- **Action**: Open git log or GitHub repository showing commit history with traceable Jira keys (e.g., `feat(module-1)`, `feat(module-2)`, `SCRUM-15 Block duplicate booking`).
- **Spoken Line (Say out loud)**:  
  *"Every commit in our GitHub repository is tagged with matching Jira SCRUM issue keys, creating full traceability between code changes, tests, and user stories."*

---

### Step 10: Show the Sprint Report
- **Action**: In Jira, navigate to Reports -> Sprint Report, demonstrating 100% completed story points with zero incomplete issues.
- **Spoken Line (Say out loud)**:  
  *"Our sprint report shows 100% completion of all committed scope across both modules, with every story backed by documented tests, passing code, and verified defect fixes."*

