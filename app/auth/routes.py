from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
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
        """SELECT b.id, b.event_id, b.ticket_type, b.quantity, b.status, b.created_at,
                  e.title AS event_title, e.date AS event_date, e.venue,
                  c.name AS category_name
           FROM bookings b
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ?
           ORDER BY b.created_at DESC, b.id DESC""",
        (auth_user_id,)
    ).fetchall()

    # 2. Upcoming events the user has confirmed bookings for (ordered by event date)
    upcoming_events = db.execute(
        """SELECT e.id AS event_id, e.title AS event_title, e.date AS event_date, e.venue,
                  c.name AS category_name,
                  SUM(b.quantity) AS user_tickets_for_event,
                  MIN(b.id) AS primary_booking_id
           FROM bookings b
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ? AND b.status = 'Confirmed'
           GROUP BY e.id, e.title, e.date, e.venue, c.name
           ORDER BY e.date ASC""",
        (auth_user_id,)
    ).fetchall()

    # 3. Actual ticket count derived from the tickets table
    ticket_stats = db.execute(
        """SELECT COUNT(t.id) AS total_tickets,
                  COALESCE(SUM(CASE WHEN t.status = 'Valid' THEN 1 ELSE 0 END), 0) AS active_tickets
           FROM tickets t
           JOIN bookings b ON t.booking_id = b.id
           WHERE b.user_id = ?""",
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
