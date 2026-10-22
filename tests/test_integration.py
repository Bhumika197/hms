import os
import tempfile
import unittest
from datetime import date, timedelta
from app import app, init_db, get_db_connection


class TestIntegration(unittest.TestCase):
    """Integration test suite covering inter-module rules and full workflows."""

    def setUp(self):
        """Set up an isolated temporary database for each integration test."""
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

    def test_patient_with_appointments_cannot_be_deleted(self):
        """Integration: Test that a patient with booked appointments cannot be deleted."""
        # 1. Register patient
        self.client.post('/patients/new', data={
            'full_name': 'Clara Oswald',
            'date_of_birth': '1986-11-23',
            'gender': 'Female',
            'phone': '9876543210',
            'email': 'clara@tardis.org',
            'address': 'London, UK'
        })

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, patient_code FROM patients WHERE full_name = 'Clara Oswald'")
        patient = cur.fetchone()
        patient_id = patient['id']
        patient_code = patient['patient_code']
        conn.close()

        # 2. Book appointment
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.client.post('/appointments/new', data={
            'patient_code': patient_code,
            'doctor_id': '1',
            'appointment_date': tomorrow,
            'appointment_time': '10:30',
            'reason': 'Health Review'
        })

        # 3. Attempt to delete patient
        del_resp = self.client.post(f'/patients/{patient_id}/delete', follow_redirects=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertIn(b'Cannot delete a patient who has appointments. Cancel the appointments first.', del_resp.data)

        # 4. Verify patient still exists in database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        still_exists = cur.fetchone()
        conn.close()
        self.assertIsNotNone(still_exists)

    def test_cancel_appointment_allows_subsequent_patient_deletion(self):
        """Integration: Test that cancelling all appointments unlocks patient deletion."""
        # 1. Register patient
        self.client.post('/patients/new', data={
            'full_name': 'Rory Williams',
            'date_of_birth': '1989-05-01',
            'gender': 'Male',
            'phone': '9876543211',
            'email': 'rory@example.com',
            'address': 'Leadworth, UK'
        })

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, patient_code FROM patients WHERE full_name = 'Rory Williams'")
        patient = cur.fetchone()
        patient_id = patient['id']
        patient_code = patient['patient_code']

        # 2. Book appointment
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        cur.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
            VALUES (?, 1, ?, '11:00', 'Checkup')
        """, (patient_id, tomorrow))
        apt_id = cur.lastrowid
        conn.commit()
        conn.close()

        # 3. Cancel appointment
        cancel_resp = self.client.post(f'/appointments/{apt_id}/cancel', follow_redirects=True)
        self.assertEqual(cancel_resp.status_code, 200)
        self.assertIn(b'Appointment cancelled successfully', cancel_resp.data)

        # 4. Now patient deletion succeeds
        del_resp = self.client.post(f'/patients/{patient_id}/delete', follow_redirects=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertIn(b'deleted successfully', del_resp.data)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient_after = cur.fetchone()
        conn.close()
        self.assertIsNone(patient_after)

    def test_end_to_end_patient_registration_and_appointment_workflow(self):
        """Integration: Full E2E flow from patient registration to doctor appointment lookup."""
        # 1. Register patient
        reg_resp = self.client.post('/patients/new', data={
            'full_name': 'Donna Noble',
            'date_of_birth': '1979-06-24',
            'gender': 'Female',
            'phone': '9876543222',
            'email': 'donna@chiswick.org',
            'address': 'Chiswick, London'
        }, follow_redirects=True)
        self.assertEqual(reg_resp.status_code, 200)
        self.assertIn(b'PAT-00001', reg_resp.data)

        # 2. Schedule appointment
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        book_resp = self.client.post('/appointments/new', data={
            'patient_code': 'PAT-00001',
            'doctor_id': '2',  # Dr. Michael Chang - General Physician
            'appointment_date': tomorrow,
            'appointment_time': '15:30',
            'reason': 'Annual Wellness Physical'
        }, follow_redirects=True)
        self.assertEqual(book_resp.status_code, 200)
        self.assertIn(b'Appointment booked successfully', book_resp.data)

        # 3. Verify joined presentation on appointments list page
        apt_list_resp = self.client.get('/appointments')
        self.assertEqual(apt_list_resp.status_code, 200)
        self.assertIn(b'PAT-00001', apt_list_resp.data)
        self.assertIn(b'Donna Noble', apt_list_resp.data)
        self.assertIn(b'Dr. Michael Chang', apt_list_resp.data)
        self.assertIn(b'General Physician', apt_list_resp.data)
        self.assertIn(b'15:30', apt_list_resp.data)

    def test_root_redirect_and_navigation_links(self):
        """Integration: Test root path redirect to /patients and navigation bar elements."""
        root_resp = self.client.get('/', follow_redirects=False)
        self.assertEqual(root_resp.status_code, 302)
        self.assertEqual(root_resp.headers['Location'], '/patients')

        # Check navigation in /patients
        page_resp = self.client.get('/patients')
        self.assertIn(b'href="/patients"', page_resp.data)
        self.assertIn(b'href="/appointments"', page_resp.data)

    def test_404_page_not_found(self):
        """Integration: Test application returns custom 404 page for nonexistent paths."""
        resp = self.client.get('/nonexistent-path-abc')
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b'404 - Page Not Found', resp.data)


if __name__ == '__main__':
    unittest.main()
