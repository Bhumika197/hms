import os
import tempfile
import unittest
from app import app, init_db, get_db_connection


class TestDefectReproduction(unittest.TestCase):
    """Test suite specifically targeting edge case quality defects."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.environ['HMS_DATABASE'] = self.db_path
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_defect_1_name_accepting_symbols_and_numbers(self):
        """Test whether full name containing symbols and numbers (e.g. 'R2D2!!') is rejected."""
        resp = self.client.post('/patients/new', data={
            'full_name': 'R2D2!!',
            'date_of_birth': '1995-03-20',
            'gender': 'Other',
            'phone': '9876543210',
            'email': 'r2d2@droid.com',
            'address': 'Tatooine Sector 4'
        })
        self.assertEqual(resp.status_code, 400, "Should reject name containing numbers and symbols like 'R2D2!!'")
        self.assertIn(b'letters, spaces, hyphens', resp.data)

    def test_defect_2_search_wildcard_percent_and_underscore(self):
        """Test whether search treats '%' and '_' as literal characters instead of SQL wildcards."""
        # Register two patients without '%' in their name
        self.client.post('/patients/new', data={
            'full_name': 'Alice Regular',
            'date_of_birth': '1990-01-01',
            'gender': 'Female',
            'phone': '9876543210',
            'email': 'alice@example.com',
            'address': '101 First Avenue, Springfield'
        })
        self.client.post('/patients/new', data={
            'full_name': 'Bob Normal',
            'date_of_birth': '1988-02-02',
            'gender': 'Male',
            'phone': '9876543211',
            'email': 'bob@example.com',
            'address': '202 Second Avenue, Springfield'
        })

        # Searching for '%' should NOT return any patients because neither has '%' in their name or code
        resp = self.client.get('/patients?q=%')
        self.assertNotIn(b'Alice Regular', resp.data, "Search query '%' must not act as a wildcard matching all patients")
        self.assertNotIn(b'Bob Normal', resp.data, "Search query '%' must not act as a wildcard matching all patients")

    def test_defect_3_phone_with_all_identical_digits(self):
        """Test whether invalid dummy phone numbers like '0000000000' are rejected."""
        resp = self.client.post('/patients/new', data={
            'full_name': 'Frank Castle',
            'date_of_birth': '1982-11-15',
            'gender': 'Male',
            'phone': '0000000000',
            'email': 'frank@punisher.com',
            'address': 'Hell Kitchen, NY'
        })
        self.assertEqual(resp.status_code, 400, "Should reject dummy phone number '0000000000'")
        self.assertIn(b'valid phone number', resp.data)

    def test_defect_4_duplicate_patient_registration(self):
        """Test whether registering identical patient (same name, DOB, and phone) is prevented."""
        patient_data = {
            'full_name': 'Bruce Wayne',
            'date_of_birth': '1980-05-27',
            'gender': 'Male',
            'phone': '9876543210',
            'email': 'bruce@wayne.com',
            'address': '1007 Mountain Drive, Gotham'
        }
        resp1 = self.client.post('/patients/new', data=patient_data)
        self.assertEqual(resp1.status_code, 302)

        # Attempt to register the exact same patient again
        resp2 = self.client.post('/patients/new', data=patient_data)
        self.assertEqual(resp2.status_code, 400, "Should reject duplicate patient registration")
        self.assertIn(b'A patient with this name, date of birth, and phone number is already registered', resp2.data)


if __name__ == '__main__':
    unittest.main()
