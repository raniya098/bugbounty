import os
import subprocess
import sys

AUTH_ROUTES_PY = """from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from app.models import log_action
from app.security import login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with that email address already exists.", "error")
            return render_template("register.html")

        cursor = db.execute(
            "INSERT INTO users (name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, 'participant')",
            (name, email, phone, generate_password_hash(password))
        )
        db.commit()
        log_action(cursor.lastrowid, f"Registered participant account: {email}")
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        log_action(user["id"], "Logged in")
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    if g.user:
        log_action(g.user["id"], "Logged out")
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    # Always scope to the server-authenticated session user (never trust request args)
    auth_user_id = g.user["id"]
    db = get_db()

    # 1. Booking history for the logged-in user
    bookings = db.execute(
        \"\"\"SELECT b.id, b.event_id, b.ticket_type, b.quantity, b.status, b.created_at,
                  e.title AS event_title, e.date AS event_date, e.venue,
                  c.name AS category_name
           FROM bookings b
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ?
           ORDER BY b.created_at DESC, b.id DESC\"\"\",
        (auth_user_id,)
    ).fetchall()

    # 2. Upcoming events the user has confirmed bookings for (ordered by event date)
    upcoming_events = db.execute(
        \"\"\"SELECT e.id AS event_id, e.title AS event_title, e.date AS event_date, e.venue,
                  c.name AS category_name,
                  SUM(b.quantity) AS user_tickets_for_event,
                  MIN(b.id) AS primary_booking_id
           FROM bookings b
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ? AND b.status = 'Confirmed'
           GROUP BY e.id, e.title, e.date, e.venue, c.name
           ORDER BY e.date ASC\"\"\",
        (auth_user_id,)
    ).fetchall()

    # 3. Actual ticket count derived from the tickets table
    ticket_stats = db.execute(
        \"\"\"SELECT COUNT(t.id) AS total_tickets,
                  COALESCE(SUM(CASE WHEN t.status = 'Valid' THEN 1 ELSE 0 END), 0) AS active_tickets
           FROM tickets t
           JOIN bookings b ON t.booking_id = b.id
           WHERE b.user_id = ?\"\"\",
        (auth_user_id,)
    ).fetchone()

    total_tickets = ticket_stats["total_tickets"] if ticket_stats else 0
    active_tickets = ticket_stats["active_tickets"] if ticket_stats else 0

    return render_template(
        "participant_dashboard.html",
        bookings=bookings,
        upcoming_events=upcoming_events,
        total_bookings=len(bookings),
        total_tickets=total_tickets,
        active_tickets=active_tickets
    )
"""

TICKETS_ROUTES_PY = """from flask import Blueprint, render_template, abort, g
from app.database import get_db
from app.security import login_required, check_ownership

tickets_bp = Blueprint("tickets", __name__)

@tickets_bp.route("/my-tickets")
@login_required
def my_tickets():
    # Strictly use the authenticated user's session ID on the server
    auth_user_id = g.user["id"]
    db = get_db()
    tickets = db.execute(
        \"\"\"SELECT t.id, t.booking_id, t.ticket_code, t.status,
                  b.ticket_type, b.status AS booking_status, b.created_at AS booked_at,
                  e.id AS event_id, e.title AS event_title, e.date AS event_date, e.venue,
                  c.name AS category_name
           FROM tickets t
           JOIN bookings b ON t.booking_id = b.id
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ?
           ORDER BY e.date ASC, t.id ASC\"\"\",
        (auth_user_id,)
    ).fetchall()
    return render_template("my_tickets.html", tickets=tickets)

@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    db = get_db()
    ticket = db.execute(
        \"\"\"SELECT t.id, t.booking_id, t.ticket_code, t.status,
                  b.user_id, b.ticket_type, b.created_at AS booked_at,
                  e.id AS event_id, e.title AS event_title, e.date AS event_date, e.venue,
                  u.name AS holder_name, u.email AS holder_email
           FROM tickets t
           JOIN bookings b ON t.booking_id = b.id
           JOIN events e ON b.event_id = e.id
           JOIN users u ON b.user_id = u.id
           WHERE t.id = ?\"\"\",
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        abort(404)

    # Enforce strict server-side ownership check
    check_ownership(ticket["user_id"])

    return render_template("ticket_detail.html", ticket=ticket)
"""

PARTICIPANT_DASHBOARD_HTML = """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>Participant Dashboard</h1>
        <p class="section-subtitle">Welcome, {{ g.user['name'] }} &mdash; view your profile, upcoming events, and booking history</p>
    </div>
    <div class="action-group">
        <a href="{{ url_for('tickets.my_tickets') }}" class="btn btn-secondary">View My Tickets ({{ total_tickets }})</a>
        <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Browse Events</a>
    </div>
</div>

<!-- Derived Summary Counts from Actual Database Records -->
<div class="stats-grid">
    <div class="card stat-card">
        <span class="badge">Total Tickets</span>
        <div class="stat-value">{{ total_tickets }}</div>
        <p class="meta">{{ active_tickets }} active entry pass{% if active_tickets != 1 %}es{% endif %} issued to your account</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Upcoming Events</span>
        <div class="stat-value">{{ upcoming_events | length }}</div>
        <p class="meta">Distinct events you are registered to attend</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Total Bookings</span>
        <div class="stat-value">{{ total_bookings }}</div>
        <p class="meta">Completed booking transactions on record</p>
    </div>
</div>

<div class="dashboard-layout">
    <!-- Left Column: Scoped Participant Profile -->
    <div class="card">
        <h3>My Profile</h3>
        <p class="meta">Account details for your current session</p>
        <div class="detail-list">
            <div class="detail-row">
                <strong>Full Name</strong>
                <span>{{ g.user['name'] }}</span>
            </div>
            <div class="detail-row">
                <strong>Email Address</strong>
                <span>{{ g.user['email'] }}</span>
            </div>
            <div class="detail-row">
                <strong>Phone</strong>
                <span>{{ g.user['phone'] if g.user['phone'] else 'Not provided' }}</span>
            </div>
            <div class="detail-row">
                <strong>Account Role</strong>
                <span class="badge">{{ g.user['role'] }}</span>
            </div>
        </div>
        <a href="{{ url_for('tickets.my_tickets') }}" class="btn btn-secondary btn-block">Go to My Tickets</a>
    </div>

    <!-- Right Column: Upcoming Events & Booking History -->
    <div>
        <!-- Upcoming Registered Events -->
        <div class="card">
            <div class="section-header" style="margin-bottom: 0.75rem;">
                <div>
                    <h3>Upcoming Registered Events</h3>
                    <p class="meta">Events with confirmed passes under your account</p>
                </div>
            </div>

            {% if upcoming_events %}
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Event</th>
                            <th>Category</th>
                            <th>Date &amp; Time</th>
                            <th>Venue</th>
                            <th>Your Tickets</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ev in upcoming_events %}
                        <tr>
                            <td>
                                <a href="{{ url_for('events.event_detail', event_id=ev['event_id']) }}">
                                    <strong>{{ ev['event_title'] }}</strong>
                                </a>
                            </td>
                            <td><span class="badge">{{ ev['category_name'] }}</span></td>
                            <td>{{ ev['event_date'] }}</td>
                            <td>{{ ev['venue'] }}</td>
                            <td><strong>{{ ev['user_tickets_for_event'] }}</strong> pass{% if ev['user_tickets_for_event'] != 1 %}es{% endif %}</td>
                            <td>
                                <div class="action-group">
                                    <a href="{{ url_for('events.event_detail', event_id=ev['event_id']) }}" class="btn btn-secondary btn-sm">Event Page</a>
                                    <a href="{{ url_for('tickets.my_tickets') }}" class="btn btn-primary btn-sm">My Passes</a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="empty-state">
                <h4>No Upcoming Events</h4>
                <p class="meta">You do not have any upcoming event registrations yet.</p>
                <div style="margin-top: 1rem;">
                    <a href="{{ url_for('events.list_events') }}" class="btn btn-primary btn-sm">Explore Upcoming Events</a>
                </div>
            </div>
            {% endif %}
        </div>

        <!-- Complete Booking History -->
        <div class="card">
            <div class="section-header" style="margin-bottom: 0.75rem;">
                <div>
                    <h3>Booking History</h3>
                    <p class="meta">All booking references and receipts associated with your account</p>
                </div>
            </div>

            {% if bookings %}
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Booking Ref</th>
                            <th>Event</th>
                            <th>Event Date</th>
                            <th>Tier &amp; Qty</th>
                            <th>Status</th>
                            <th>Booked On</th>
                            <th>Receipt</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for b in bookings %}
                        <tr>
                            <td><code>#{{ b['id'] }}</code></td>
                            <td>
                                <a href="{{ url_for('events.event_detail', event_id=b['event_id']) }}">
                                    <strong>{{ b['event_title'] }}</strong>
                                </a>
                            </td>
                            <td>{{ b['event_date'] }}</td>
                            <td>{{ b['quantity'] }} &times; {{ b['ticket_type'] }}</td>
                            <td><span class="badge">{{ b['status'] }}</span></td>
                            <td>{{ b['created_at'] }}</td>
                            <td>
                                <a href="{{ url_for('bookings.confirmation', booking_id=b['id']) }}" class="btn btn-secondary btn-sm">
                                    View Receipt
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="empty-state">
                <h4>No Booking History Found</h4>
                <p class="meta">Once you book tickets for an event, your booking reference and receipt will appear here.</p>
                <div style="margin-top: 1rem;">
                    <a href="{{ url_for('events.list_events') }}" class="btn btn-primary btn-sm">Book Your First Event</a>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
"""

MY_TICKETS_HTML = """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>My Tickets</h1>
        <p class="section-subtitle">
            Showing <strong>{{ tickets | length }}</strong> ticket{% if (tickets | length) != 1 %}s{% endif %} issued to {{ g.user['name'] }}
        </p>
    </div>
    <div class="action-group">
        <a href="{{ url_for('auth.dashboard') }}" class="btn btn-secondary">Participant Dashboard</a>
        <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Book More Events</a>
    </div>
</div>

<div class="card">
    {% if tickets %}
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Ticket Code</th>
                    <th>Booking Ref</th>
                    <th>Event Name</th>
                    <th>Event Date &amp; Venue</th>
                    <th>Ticket Type</th>
                    <th>Ticket Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for t in tickets %}
                <tr>
                    <td>#{{ t['id'] }}</td>
                    <td><code>{{ t['ticket_code'] }}</code></td>
                    <td>
                        <a href="{{ url_for('bookings.confirmation', booking_id=t['booking_id']) }}" title="View Booking Confirmation #{{ t['booking_id'] }}">
                            <code>BK-{{ t['booking_id'] }}</code>
                        </a>
                    </td>
                    <td>
                        <a href="{{ url_for('events.event_detail', event_id=t['event_id']) }}">
                            <strong>{{ t['event_title'] }}</strong>
                        </a>
                    </td>
                    <td>{{ t['event_date'] }} &bull; {{ t['venue'] }}</td>
                    <td>{{ t['ticket_type'] }}</td>
                    <td><span class="badge">{{ t['status'] }}</span></td>
                    <td>
                        <div class="action-group">
                            <a href="{{ url_for('tickets.ticket_detail', ticket_id=t['id']) }}" class="btn btn-primary btn-sm">View Pass</a>
                            <a href="{{ url_for('bookings.confirmation', booking_id=t['booking_id']) }}" class="btn btn-secondary btn-sm">Receipt</a>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state">
        <h3>No Tickets Issued Yet</h3>
        <p class="meta">You currently have no tickets under your account. Browse upcoming events to reserve your seat.</p>
        <div style="margin-top: 1.25rem;">
            <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Explore Events &amp; Book Tickets</a>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
"""

TEST_TICKETS_DASHBOARD_PY = """import os
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
"""

with open("app/auth/routes.py", "w", encoding="utf-8") as f:
    f.write(AUTH_ROUTES_PY.lstrip())
print("Updated app/auth/routes.py with derived ticket counts and upcoming events query")

with open("app/tickets/routes.py", "w", encoding="utf-8") as f:
    f.write(TICKETS_ROUTES_PY.lstrip())
print("Updated app/tickets/routes.py with booking reference and strict user scoping")

with open("app/templates/participant_dashboard.html", "w", encoding="utf-8") as f:
    f.write(PARTICIPANT_DASHBOARD_HTML.lstrip())
print("Updated app/templates/participant_dashboard.html with KPI stats, upcoming events, booking history, and empty states")

with open("app/templates/my_tickets.html", "w", encoding="utf-8") as f:
    f.write(MY_TICKETS_HTML.lstrip())
print("Updated app/templates/my_tickets.html with booking reference, ticket status, and empty state")

os.makedirs("tests", exist_ok=True)
with open("tests/test_tickets_dashboard.py", "w", encoding="utf-8") as f:
    f.write(TEST_TICKETS_DASHBOARD_PY.lstrip())
print("Created tests/test_tickets_dashboard.py")

print("\nRunning full automated test suite...")
res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
sys.exit(res.returncode)