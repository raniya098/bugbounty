import os
import tempfile
import unittest
from app import create_app
from app.models import init_and_seed_db
from config import Config

class TestConfig(Config):
    TESTING = True

class EventHubCleanTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        TestConfig.DATABASE_PATH = self.db_path
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            init_and_seed_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def login(self, email, password="Password123!"):
        return self.client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

    def test_home_and_events_load(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        res_events = self.client.get("/events")
        self.assertEqual(res_events.status_code, 200)

    def test_valid_registration_and_login(self):
        res = self.client.post("/register", data={
            "name": "Charlie Test",
            "email": "charlie@eventhub.local",
            "phone": "555-0300",
            "password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"Account created successfully", res.data)

    def test_over_limit_booking_rejected(self):
        self.login("bob@eventhub.local")
        res = self.client.post("/book/1", data={"ticket_type": "Standard", "quantity": 5}, follow_redirects=True)
        self.assertIn(b"You may book between 1 and 4 tickets", res.data)

    def test_other_users_ticket_denied(self):
        self.login("alice@eventhub.local")
        # Ticket #3 belongs to Bob
        res = self.client.get("/tickets/3")
        self.assertEqual(res.status_code, 403)

    def test_participant_blocked_from_organizer_and_admin(self):
        self.login("alice@eventhub.local")
        self.assertEqual(self.client.get("/organizer/").status_code, 403)
        self.assertEqual(self.client.get("/admin/").status_code, 403)

if __name__ == "__main__":
    unittest.main()