import os
import tempfile
import unittest
from datetime import date, timedelta
from app import app, init_db, get_db_connection


class TestPatientManagement(unittest.TestCase):
    """Test suite for Module 1: Patient Registration and Management."""

    def setUp(self):
        """Set up an isolated temporary database for each test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.environ['HMS_DATABASE'] = self.db_path
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def tearDown(self):
        """Clean up the temporary database after each test."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _register_patient(self, **overrides):
        """Helper to post patient registration data."""
        data = {
            'full_name': 'Eleanor Vance',
            'date_of_birth': '1992-05-14',
            'gender': 'Female',
            'phone': '9876543210',
            'email': 'eleanor@example.com',
            'address': '742 Evergreen Terrace, Springfield'
        }
        data.update(overrides)
        return self.client.post('/patients/new', data=data, follow_redirects=False)

    def test_valid_patient_registration(self):
        """Functional: Test successful patient registration and PAT-00001 code generation."""
        response = self._register_patient()
        self.assertEqual(response.status_code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE full_name = 'Eleanor Vance'")
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['patient_code'], 'PAT-00001')
        self.assertEqual(row['gender'], 'Female')
        self.assertEqual(row['phone'], '9876543210')

    def test_missing_full_name(self):
        """Validation: Test that omitting full_name triggers required validation error."""
        response = self._register_patient(full_name='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Full name is required', response.data)

    def test_missing_date_of_birth(self):
        """Validation: Test that omitting date_of_birth triggers required validation error."""
        response = self._register_patient(date_of_birth='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Date of birth is required', response.data)

    def test_missing_gender(self):
        """Validation: Test that omitting gender triggers required validation error."""
        response = self._register_patient(gender='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Gender is required', response.data)

    def test_missing_phone(self):
        """Validation: Test that omitting phone number triggers required validation error."""
        response = self._register_patient(phone='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Phone number is required', response.data)

    def test_missing_address(self):
        """Validation: Test that omitting address triggers required validation error."""
        response = self._register_patient(address='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Address is required', response.data)

    def test_address_boundary_14_characters(self):
        """Boundary Value Analysis: Test that address below 15 characters is rejected."""
        response = self._register_patient(address='12345678901234')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Address must be at least 15 characters', response.data)

    def test_address_boundary_15_characters(self):
        """Boundary Value Analysis: Test that address with exactly 15 characters is accepted."""
        response = self._register_patient(address='123456789012345')
        self.assertEqual(response.status_code, 302)

    def test_phone_boundary_9_digits(self):
        """Boundary Value Analysis: Test that 9 digits phone number is rejected."""
        response = self._register_patient(phone='123456789')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Phone must be 10 to 15 digits', response.data)

    def test_phone_boundary_10_digits(self):
        """Boundary Value Analysis: Test that exactly 10 digits phone number is accepted."""
        response = self._register_patient(phone='1234567890')
        self.assertEqual(response.status_code, 302)

    def test_phone_boundary_15_digits(self):
        """Boundary Value Analysis: Test that exactly 15 digits phone number is accepted."""
        response = self._register_patient(phone='123456789012345')
        self.assertEqual(response.status_code, 302)

    def test_phone_boundary_16_digits(self):
        """Boundary Value Analysis: Test that 16 digits phone number is rejected."""
        response = self._register_patient(phone='1234567890123456')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Phone must be 10 to 15 digits', response.data)

    def test_phone_with_leading_plus(self):
        """Equivalence Partitioning: Test that valid phone with leading plus is accepted."""
        response = self._register_patient(phone='+19876543210')
        self.assertEqual(response.status_code, 302)

    def test_phone_with_letters(self):
        """Validation: Test that phone numbers containing alphabetic letters are rejected."""
        response = self._register_patient(phone='987654ABCD')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Phone number cannot contain letters', response.data)

    def test_phone_formatting_strips_spaces_and_dashes(self):
        """Functional: Test that phone formatting with spaces, brackets and dashes is cleaned."""
        response = self._register_patient(phone='(555) 234-5678')
        self.assertEqual(response.status_code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT phone FROM patients WHERE full_name = 'Eleanor Vance'")
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row['phone'], '5552345678')

    def test_date_of_birth_in_future(self):
        """Boundary Value Analysis: Test that future date of birth is rejected."""
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self._register_patient(date_of_birth=future_date)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Date of birth cannot be in the future', response.data)

    def test_date_of_birth_before_1900(self):
        """Boundary Value Analysis: Test that date of birth prior to 1900 is rejected."""
        response = self._register_patient(date_of_birth='1899-12-31')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Date of birth cannot be before 1900', response.data)

    def test_invalid_gender(self):
        """Equivalence Partitioning: Test that non-standard gender selection is rejected."""
        response = self._register_patient(gender='Unknown')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Gender must be one of Female, Male, Other', response.data)

    def test_invalid_email_format(self):
        """Equivalence Partitioning: Test that malformed email is rejected."""
        response = self._register_patient(email='not-an-email-at-all')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid email format', response.data)

    def test_optional_empty_email_allowed(self):
        """Equivalence Partitioning: Test that omitting optional email succeeds."""
        response = self._register_patient(email='')
        self.assertEqual(response.status_code, 302)

    def test_name_length_boundary_100_characters(self):
        """Boundary Value Analysis: Test that name with exactly 100 characters is accepted."""
        name_100 = 'A' * 100
        response = self._register_patient(full_name=name_100)
        self.assertEqual(response.status_code, 302)

    def test_name_length_boundary_101_characters(self):
        """Boundary Value Analysis: Test that name with 101 characters is rejected."""
        name_101 = 'A' * 101
        response = self._register_patient(full_name=name_101)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Full name must not exceed 100 characters', response.data)

    def test_name_must_contain_at_least_one_letter(self):
        """Validation: Test that name consisting solely of spaces or numbers is rejected."""
        response = self._register_patient(full_name='12345678')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Full name must contain at least one letter', response.data)

    def test_search_by_patient_id(self):
        """Functional: Test searching patient directory by exact and partial patient code."""
        self._register_patient(full_name='Patient One')
        self._register_patient(full_name='Patient Two')

        response = self.client.get('/patients?q=PAT-00001')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient One', response.data)
        self.assertNotIn(b'Patient Two', response.data)

    def test_search_by_name_case_insensitive_partial(self):
        """Functional: Test searching patient directory by name partial case-insensitive."""
        self._register_patient(full_name='Arthur Dent')
        self._register_patient(full_name='Ford Prefect')

        response = self.client.get('/patients?q=arth')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Arthur Dent', response.data)
        self.assertNotIn(b'Ford Prefect', response.data)

    def test_edit_patient_success(self):
        """Functional: Test updating existing patient record."""
        self._register_patient(full_name='Original Name')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM patients WHERE full_name = 'Original Name'")
        pid = cur.fetchone()['id']
        conn.close()

        update_data = {
            'full_name': 'Updated Name',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '9123456780',
            'email': 'updated@example.com',
            'address': 'New Address 101'
        }
        response = self.client.post(f'/patients/{pid}/edit', data=update_data, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE id = ?", (pid,))
        updated = cur.fetchone()
        conn.close()
        self.assertEqual(updated['full_name'], 'Updated Name')
        self.assertEqual(updated['gender'], 'Male')

    def test_edit_patient_validation_failure(self):
        """Validation: Test that invalid input during edit preserves record and shows error."""
        self._register_patient(full_name='Valid Before')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM patients WHERE full_name = 'Valid Before'")
        pid = cur.fetchone()['id']
        conn.close()

        update_data = {
            'full_name': '',  # Invalid
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '9123456780',
            'email': 'updated@example.com',
            'address': '742 Evergreen Terrace, Springfield'
        }
        response = self.client.post(f'/patients/{pid}/edit', data=update_data, follow_redirects=False)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Full name is required', response.data)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT full_name FROM patients WHERE id = ?", (pid,))
        unchanged = cur.fetchone()
        conn.close()
        self.assertEqual(unchanged['full_name'], 'Valid Before')

    def test_delete_patient_success(self):
        """Functional: Test deleting an existing patient without appointments."""
        self._register_patient(full_name='To Delete')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM patients WHERE full_name = 'To Delete'")
        pid = cur.fetchone()['id']
        conn.close()

        response = self.client.post(f'/patients/{pid}/delete', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE id = ?", (pid,))
        deleted = cur.fetchone()
        conn.close()
        self.assertIsNone(deleted)

    def test_patient_not_found_404(self):
        """Functional: Test that accessing or editing non-existent patient returns 404."""
        response = self.client.get('/patients/99999/edit')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
