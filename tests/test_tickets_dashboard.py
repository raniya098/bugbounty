import os
import tempfile
import unittest
from app import create_app
from app.models import init_and_seed_db
from config import Config

class TestConfig(Config):
    TESTING = True

class EventHubTicketsAndDashboardTestCase(unittest.TestCase):
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

    def test_alice_dashboard_and_my_tickets_scoped(self):
        # Alice (user_id=4) has 1 booking (2 VIP tickets) for Event #1 ("NextGen Web Engineering Conference")
        self.login("alice@eventhub.local")

        dash = self.client.get("/dashboard")
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b"Alice Participant", dash.data)
        self.assertIn(b"NextGen Web Engineering Conference", dash.data)
        # Bob's event ("Defensive Application Security Summit") must NOT appear in Alice's dashboard
        self.assertNotIn(b"Defensive Application Security Summit", dash.data)
        # Sensitive fields like password_hash must never be rendered
        self.assertNotIn(b"scrypt:", dash.data)
        self.assertNotIn(b"pbkdf2:", dash.data)

        tickets = self.client.get("/my-tickets")
        self.assertEqual(tickets.status_code, 200)
        self.assertIn(b"NextGen Web Engineering Conference", tickets.data)
        self.assertIn(b"BK-1", tickets.data)
        self.assertNotIn(b"Defensive Application Security Summit", tickets.data)

    def test_bob_dashboard_and_my_tickets_scoped(self):
        # Bob (user_id=5) has 1 booking (1 Standard ticket) for Event #2 ("Defensive Application Security Summit")
        self.login("bob@eventhub.local")

        dash = self.client.get("/dashboard")
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b"Bob Participant", dash.data)
        self.assertIn(b"Defensive Application Security Summit", dash.data)
        self.assertNotIn(b"NextGen Web Engineering Conference", dash.data)

        tickets = self.client.get("/my-tickets")
        self.assertEqual(tickets.status_code, 200)
        self.assertIn(b"Defensive Application Security Summit", tickets.data)
        self.assertIn(b"BK-2", tickets.data)
        self.assertNotIn(b"NextGen Web Engineering Conference", tickets.data)

    def test_browser_supplied_user_id_ignored_and_ownership_enforced(self):
        self.login("alice@eventhub.local")
        # Attempting to pass ?user_id=5 in URL must still only show Alice's records
        res_dash = self.client.get("/dashboard?user_id=5")
        self.assertIn(b"Alice Participant", res_dash.data)
        self.assertNotIn(b"Defensive Application Security Summit", res_dash.data)

        res_tickets = self.client.get("/my-tickets?user_id=5")
        self.assertNotIn(b"Defensive Application Security Summit", res_tickets.data)

        # Attempting to view Bob's ticket (#3) or Bob's booking confirmation (#2) must return 403
        self.assertEqual(self.client.get("/tickets/3").status_code, 403)
        self.assertEqual(self.client.get("/bookings/2/confirmation").status_code, 403)

    def test_empty_state_for_new_user_with_no_bookings(self):
        self.client.post("/register", data={
            "name": "New Participant",
            "email": "newuser@eventhub.local",
            "phone": "555-0404",
            "password": "Password123!"
        }, follow_redirects=True)
        self.login("newuser@eventhub.local")

        dash = self.client.get("/dashboard")
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b"No Upcoming Events", dash.data)
        self.assertIn(b"No Booking History Found", dash.data)

        tickets = self.client.get("/my-tickets")
        self.assertEqual(tickets.status_code, 200)
        self.assertIn(b"No Tickets Issued Yet", tickets.data)

if __name__ == "__main__":
    unittest.main()
