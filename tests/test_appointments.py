import os
import tempfile
import unittest
from datetime import date, timedelta
from app import app, init_db, get_db_connection


class TestAppointmentManagement(unittest.TestCase):
    """Test suite for Module 2: Appointment Management."""

    def setUp(self):
        """Set up an isolated temporary database for each test and create a test patient."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.environ['HMS_DATABASE'] = self.db_path
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            init_db()

        # Seed a test patient
        self.client.post('/patients/new', data={
            'full_name': 'Test Subject',
            'date_of_birth': '1985-04-12',
            'gender': 'Male',
            'phone': '9876543210',
            'email': 'test@example.com',
            'address': '101 Healthcare Way'
        })
        self.patient_code = 'PAT-00001'

    def tearDown(self):
        """Clean up the temporary database after each test."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _book_appointment(self, **overrides):
        """Helper to post appointment booking data."""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        data = {
            'patient_code': self.patient_code,
            'doctor_id': '1',
            'appointment_date': tomorrow,
            'appointment_time': '10:00',
            'reason': 'Routine Cardiology Checkup'
        }
        data.update(overrides)
        return self.client.post('/appointments/new', data=data, follow_redirects=False)

    def test_valid_appointment_booking(self):
        """Functional: Test booking a valid appointment for a registered patient."""
        response = self._book_appointment()
        self.assertEqual(response.status_code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM appointments")
        apt = cur.fetchone()
        conn.close()

        self.assertIsNotNone(apt)
        self.assertEqual(apt['appointment_time'], '10:00')

    def test_unknown_patient_id_booking_rejected(self):
        """Equivalence Partitioning: Test booking with non-existent patient ID is rejected."""
        response = self._book_appointment(patient_code='PAT-99999')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Unknown patient ID', response.data)

        # Verify nothing was saved
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM appointments")
        count = cur.fetchone()['cnt']
        conn.close()
        self.assertEqual(count, 0)

    def test_missing_patient_id(self):
        """Validation: Test that omitting patient ID returns validation error."""
        response = self._book_appointment(patient_code='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Patient ID is required', response.data)

    def test_missing_doctor_selection(self):
        """Validation: Test that omitting doctor selection returns validation error."""
        response = self._book_appointment(doctor_id='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Please select a doctor', response.data)

    def test_nonexistent_doctor_id(self):
        """Equivalence Partitioning: Test that selecting invalid doctor ID returns error."""
        response = self._book_appointment(doctor_id='9999')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Selected doctor does not exist', response.data)

    def test_missing_appointment_date(self):
        """Validation: Test that omitting appointment date returns validation error."""
        response = self._book_appointment(appointment_date='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Appointment date is required', response.data)

    def test_past_appointment_date_rejected(self):
        """Boundary Value Analysis: Test that yesterday date is rejected."""
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = self._book_appointment(appointment_date=yesterday)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Appointment date cannot be in the past', response.data)

    def test_today_appointment_date_allowed(self):
        """Boundary Value Analysis: Test that today appointment date is accepted."""
        today = date.today().strftime('%Y-%m-%d')
        response = self._book_appointment(appointment_date=today)
        self.assertEqual(response.status_code, 302)

    def test_invalid_date_format(self):
        """Equivalence Partitioning: Test that non-standard date format is rejected."""
        response = self._book_appointment(appointment_date='22-10-2026')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid date format', response.data)

    def test_missing_time_slot(self):
        """Validation: Test that omitting appointment time slot returns validation error."""
        response = self._book_appointment(appointment_time='')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Appointment time is required', response.data)

    def test_invalid_time_slot(self):
        """Equivalence Partitioning: Test that an unlisted time slot is rejected."""
        response = self._book_appointment(appointment_time='08:45')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid time slot', response.data)

    def test_boundary_time_slots(self):
        """Boundary Value Analysis: Test opening 09:00 and closing 16:30 time slots."""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        res1 = self._book_appointment(appointment_date=tomorrow, appointment_time='09:00', doctor_id='1')
        self.assertEqual(res1.status_code, 302)

        res2 = self._book_appointment(appointment_date=tomorrow, appointment_time='16:30', doctor_id='1')
        self.assertEqual(res2.status_code, 302)

    def test_duplicate_booking_blocked(self):
        """Functional: Test that duplicate booking for same doctor, date and time is rejected."""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        # First booking succeeds
        first_res = self._book_appointment(appointment_date=tomorrow, appointment_time='11:00', doctor_id='1')
        self.assertEqual(first_res.status_code, 302)

        # Second booking with same doctor, date, and time must be rejected
        second_res = self._book_appointment(appointment_date=tomorrow, appointment_time='11:00', doctor_id='1')
        self.assertEqual(second_res.status_code, 400)
        self.assertIn(b'This doctor is already booked at the selected time.', second_res.data)

    def test_same_time_different_doctor_allowed(self):
        """Functional: Test that booking the same time slot with a different doctor is allowed."""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        res1 = self._book_appointment(appointment_date=tomorrow, appointment_time='14:00', doctor_id='1')
        self.assertEqual(res1.status_code, 302)

        # Book same slot with doctor 2
        res2 = self._book_appointment(appointment_date=tomorrow, appointment_time='14:00', doctor_id='2')
        self.assertEqual(res2.status_code, 302)

    def test_appointment_list_ordering(self):
        """Functional: Test that appointments list orders ascending by date then time."""
        day1 = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        day2 = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')

        # Insert out of order
        self._book_appointment(appointment_date=day2, appointment_time='10:00', doctor_id='1')
        self._book_appointment(appointment_date=day1, appointment_time='14:00', doctor_id='1')
        self._book_appointment(appointment_date=day1, appointment_time='09:30', doctor_id='2')

        response = self.client.get('/appointments')
        self.assertEqual(response.status_code, 200)

        # Check chronological sequence in HTML output
        pos_day1_early = response.data.find(b'09:30')
        pos_day1_late = response.data.find(b'14:00')
        pos_day2 = response.data.find(day2.encode('utf-8'))

        self.assertTrue(pos_day1_early < pos_day1_late < pos_day2)

    def test_cancel_appointment_success(self):
        """Functional: Test that cancelling an appointment deletes it from database."""
        self._book_appointment()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM appointments LIMIT 1")
        apt_id = cur.fetchone()['id']
        conn.close()

        response = self.client.post(f'/appointments/{apt_id}/cancel', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM appointments WHERE id = ?", (apt_id,))
        deleted = cur.fetchone()
        conn.close()
        self.assertIsNone(deleted)

    def test_cancel_nonexistent_appointment_returns_404(self):
        """Functional: Test that attempting to cancel non-existent appointment returns 404."""
        response = self.client.post('/appointments/9999/cancel')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
