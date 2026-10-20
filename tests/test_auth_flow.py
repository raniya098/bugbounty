import os
import tempfile
import unittest
from app import create_app
from app.models import init_and_seed_db
from config import Config

class TestConfig(Config):
    TESTING = True

class EventHubAuthFlowTestCase(unittest.TestCase):
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

    def test_successful_registration_and_login(self):
        # Register new user
        res = self.client.post("/register", data={
            "name": "Diana Prince",
            "email": "diana@eventhub.local",
            "phone": "555-0999",
            "password": "SecurePassword123"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Account created successfully", res.data)

        # Login with new user
        res_login = self.client.post("/login", data={
            "email": "diana@eventhub.local",
            "password": "SecurePassword123"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Welcome back, Diana Prince", res_login.data)

    def test_invalid_credentials_prevent_enumeration(self):
        # Invalid password for existing account
        res = self.client.post("/login", data={
            "email": "alice@eventhub.local",
            "password": "WrongPassword!"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid email or password", res.data)
        # Does not reveal whether email exists or not (anti-enumeration)
        self.assertNotIn(b"Password incorrect", res.data)

    def test_logout_invalidates_session(self):
        # Login
        self.client.post("/login", data={
            "email": "alice@eventhub.local",
            "password": "Password123!"
        }, follow_redirects=True)

        # Access protected page
        res_dash = self.client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)

        # Logout
        res_out = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"You have been logged out", res_out.data)

        # Protected page should now redirect to login or deny access
        res_dash_after = self.client.get("/dashboard", follow_redirects=False)
        self.assertIn(res_dash_after.status_code, [302, 403])

if __name__ == "__main__":
    unittest.main()
