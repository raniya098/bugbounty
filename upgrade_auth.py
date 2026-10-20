import os
import subprocess
import sys

REGISTER_HTML = """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <span class="badge">Join EventHub</span>
        <h2>Create Participant Account</h2>
        <p class="meta">Register to book events and manage your secure digital passes.</p>
    </div>

    <form method="POST" action="{{ url_for('auth.register') }}" class="form-stack" id="register-form" novalidate>
        <div class="form-group">
            <label for="name">Full Name *</label>
            <input type="text" id="name" name="name" placeholder="Jane Doe" required autocomplete="name">
        </div>

        <div class="form-group">
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" placeholder="jane@eventhub.local" required autocomplete="email">
        </div>

        <div class="form-group">
            <label for="phone">Phone Number (Optional)</label>
            <input type="tel" id="phone" name="phone" placeholder="555-0199" autocomplete="tel">
        </div>

        <div class="form-group">
            <label for="password">Password (min 6 characters) *</label>
            <div class="password-wrap" style="position: relative; display: flex; align-items: center;">
                <input type="password" id="password" name="password" minlength="6" required autocomplete="new-password" style="width: 100%; padding-right: 2.75rem;">
                <button type="button" id="toggle-password" aria-label="Show password" style="position: absolute; right: 0.75rem; background: none; border: none; cursor: pointer; color: var(--text-muted); font-size: 0.8rem; font-weight: 600;">Show</button>
            </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block" id="register-submit-btn">Register Account</button>
    </form>

    <hr class="divider">
    <p class="meta" style="text-align: center;">Already have an account? <a href="{{ url_for('auth.login') }}">Log in here</a></p>
</div>

<script>
document.addEventListener("DOMContentLoaded", () => {
    // Password toggle
    const pwdInput = document.getElementById("password");
    const toggleBtn = document.getElementById("toggle-password");
    if (pwdInput && toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const isPwd = pwdInput.type === "password";
            pwdInput.type = isPwd ? "text" : "password";
            toggleBtn.textContent = isPwd ? "Hide" : "Show";
        });
    }

    // Loading state
    const form = document.getElementById("register-form");
    const btn = document.getElementById("register-submit-btn");
    if (form && btn) {
        form.addEventListener("submit", () => {
            if (pwdInput.value.length >= 6) {
                btn.disabled = true;
                btn.textContent = "Creating Account...";
            }
        });
    }
});
</script>
{% endblock %}
"""

LOGIN_HTML = """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <span class="badge">Secure Portal</span>
        <h2>Sign In to EventHub</h2>
        <p class="meta">Access your dashboard, passes, and role permissions.</p>
    </div>

    <form method="POST" action="{{ url_for('auth.login') }}" class="form-stack" id="login-form">
        <div class="form-group">
            <label for="email">Email Address</label>
            <input type="email" id="email" name="email" placeholder="alice@eventhub.local" required autocomplete="email">
        </div>

        <div class="form-group">
            <label for="password">Password</label>
            <div class="password-wrap" style="position: relative; display: flex; align-items: center;">
                <input type="password" id="password" name="password" required autocomplete="current-password" style="width: 100%; padding-right: 2.75rem;">
                <button type="button" id="toggle-password" aria-label="Show password" style="position: absolute; right: 0.75rem; background: none; border: none; cursor: pointer; color: var(--text-muted); font-size: 0.8rem; font-weight: 600;">Show</button>
            </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block" id="login-submit-btn">Sign In</button>
    </form>

    <div class="hint-box">
        <p><strong>Authorized Lab Demo Testing (Click to auto-fill):</strong></p>
        <div class="demo-btn-group">
            <button type="button" class="demo-btn" data-demo-email="alice@eventhub.local">Alice (Participant)[cite: 3]</button>
            <button type="button" class="demo-btn" data-demo-email="bob@eventhub.local">Bob (Participant)[cite: 3]</button>
            <button type="button" class="demo-btn" data-demo-email="organizer@eventhub.local">Olivia (Organizer)[cite: 3]</button>
            <button type="button" class="demo-btn" data-demo-email="admin@eventhub.local">System Admin[cite: 3]</button>
        </div>
    </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", () => {
    // Password toggle
    const pwdInput = document.getElementById("password");
    const toggleBtn = document.getElementById("toggle-password");
    if (pwdInput && toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const isPwd = pwdInput.type === "password";
            pwdInput.type = isPwd ? "text" : "password";
            toggleBtn.textContent = isPwd ? "Hide" : "Show";
        });
    }

    // Loading state
    const form = document.getElementById("login-form");
    const btn = document.getElementById("login-submit-btn");
    if (form && btn) {
        form.addEventListener("submit", () => {
            btn.disabled = true;
            btn.textContent = "Signing In...";
        });
    }
});
</script>
{% endblock %}
"""

TEST_AUTH_FLOW_PY = """import os
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
"""

# 1. Update app/templates/register.html
with open("app/templates/register.html", "w", encoding="utf-8") as f:
    f.write(REGISTER_HTML.lstrip())
print("Updated app/templates/register.html with accessible form controls, show/hide password, and loading state")

# 2. Update app/templates/login.html
with open("app/templates/login.html", "w", encoding="utf-8") as f:
    f.write(LOGIN_HTML.lstrip())
print("Updated app/templates/login.html with secure anti-enumeration feedback, show/hide password, and lab demo controls")

# 3. Create tests/test_auth_flow.py
os.makedirs("tests", exist_ok=True)
with open("tests/test_auth_flow.py", "w", encoding="utf-8") as f:
    f.write(TEST_AUTH_FLOW_PY.lstrip())
print("Created tests/test_auth_flow.py")

print("\nRunning test suite including authentication flow tests...")
res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
sys.exit(res.returncode)