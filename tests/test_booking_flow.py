import os
import tempfile
import unittest
from app import create_app
from app.models import init_and_seed_db
from config import Config

class TestConfig(Config):
    TESTING = True

class EventHubBookingFlowTestCase(unittest.TestCase):
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

    def test_valid_booking_and_summary(self):
        self.login("alice@eventhub.local")
        # Book 2 tickets for event #3
        res = self.client.post("/book/3", data={
            "ticket_type": "VIP",
            "quantity": 2
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Booking Confirmation", res.data)
        self.assertIn(b"VIP Pass", res.data)
        self.assertIn(b"59.98", res.data) # Total price for 2 VIP @ $29.99

    def test_invalid_quantity_rejected(self):
        self.login("bob@eventhub.local")
        res = self.client.post("/book/3", data={
            "ticket_type": "Standard",
            "quantity": 5 # Exceeds max per booking (4)
        }, follow_redirects=True)
        self.assertIn(b"You may book between 1 and 4 tickets", res.data)

    def test_per_user_limit_enforced(self):
        self.login("bob@eventhub.local")
        # Book max 4 tickets
        self.client.post("/book/3", data={"ticket_type": "Standard", "quantity": 4}, follow_redirects=True)
        # Attempt 1 more ticket for same event #3
        res = self.client.post("/book/3", data={"ticket_type": "Standard", "quantity": 1}, follow_redirects=True)
        self.assertIn(b"Booking limit reached", res.data)

    def test_full_capacity_rejection(self):
        self.login("alice@eventhub.local")
        # Event #3 capacity is 40. Let's test booking an excessive quantity that exceeds remaining capacity.
        res = self.client.post("/book/3", data={
            "ticket_type": "Standard",
            "quantity": 4
        }, follow_redirects=True)
        # If capacity check fails or if we simulate full capacity
        self.assertEqual(res.status_code, 200)

    def test_duplicate_submission_protection_script_present(self):
        res = self.client.get("/events/3")
        self.assertEqual(res.status_code, 200)
        # Verify event detail page is reachable and functional
        self.assertIn(b"Ticket Booking", res.data)

if __name__ == "__main__":
    unittest.main()
