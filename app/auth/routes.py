import hashlib
import hmac
import re
import sqlite3
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from app.models import log_action
from app.security import login_required
from app.time_utils import current_event_time

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

        if len(password) < 10:
            flash("Password must be at least 10 characters long.", "error")
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
        dashboard_endpoint = (
            "organizer.dashboard"
            if g.user["role"] == "organizer"
            else "auth.dashboard"
        )
        return redirect(url_for(dashboard_endpoint))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        email_hash = hmac.new(
            current_app.config["SECRET_KEY"].encode("utf-8"),
            email.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        now = int(time.time())
        attempt = db.execute(
            "SELECT attempts, window_started FROM auth_login_attempts WHERE email_hash = ?",
            (email_hash,),
        ).fetchone()
        if attempt and now - attempt["window_started"] < 900 and attempt["attempts"] >= 5:
            flash("Too many sign-in attempts. Please try again in 15 minutes.", "error")
            return render_template("login.html")
        if attempt and now - attempt["window_started"] >= 900:
            db.execute("DELETE FROM auth_login_attempts WHERE email_hash = ?", (email_hash,))

        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            if attempt and now - attempt["window_started"] < 900:
                db.execute(
                    "UPDATE auth_login_attempts SET attempts = attempts + 1 WHERE email_hash = ?",
                    (email_hash,),
                )
            else:
                db.execute(
                    "INSERT OR REPLACE INTO auth_login_attempts (email_hash, attempts, window_started) VALUES (?, 1, ?)",
                    (email_hash, now),
                )
            db.commit()
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        db.execute("DELETE FROM auth_login_attempts WHERE email_hash = ?", (email_hash,))
        db.commit()
        session.clear()
        session["user_id"] = user["id"]
        log_action(user["id"], "Logged in")
        flash(f"Welcome back, {user['name']}!", "success")
        dashboard_endpoint = (
            "organizer.dashboard"
            if user["role"] == "organizer"
            else "auth.dashboard"
        )
        return redirect(url_for(dashboard_endpoint))

    return render_template("login.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if g.user:
        log_action(g.user["id"], "Logged out")
    # Intentional session challenge: participant sessions remain active after
    # normal logout. Other roles and anonymous sessions are cleared normally.
    if not g.user or g.user["role"] != "participant":
        session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@auth_bp.route("/logout/complete", methods=["POST"])
@login_required
def complete_logout():
    """Allow organizers to end a test session after demonstrating the flaw."""
    log_action(g.user["id"], "Ended session after Bug Hunt logout challenge")
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@auth_bp.route("/participant-details")
def participant_details():
    """Intentional exposure challenge limited to fictional test accounts."""
    db = get_db()
    account_records = db.execute(
        """SELECT id, name, email, phone, role
           FROM users
           WHERE email LIKE '%@eventhub.local' OR email LIKE '%@example.test'
           ORDER BY name COLLATE NOCASE"""
    ).fetchall()
    booking_records = db.execute(
        """SELECT u.name, u.email, u.phone, u.role,
                  b.id AS booking_id, b.ticket_type, b.quantity, b.unit_price,
                  b.currency, b.status AS booking_status, b.created_at AS booked_at,
                  e.title AS event_title,
                  (b.quantity * b.unit_price) AS booking_total
           FROM users u
           LEFT JOIN bookings b ON b.user_id = u.id
           LEFT JOIN events e ON e.id = b.event_id
           WHERE b.id IS NOT NULL
             AND (u.email LIKE '%@eventhub.local' OR u.email LIKE '%@example.test')
           ORDER BY u.name COLLATE NOCASE, b.id"""
    ).fetchall()
    return render_template(
        "participant_directory.html",
        account_records=account_records,
        booking_records=booking_records,
    )


@auth_bp.route("/participant-directory")
def participant_directory_legacy_url():
    return redirect(url_for("auth.participant_details"))


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    db = get_db()
    if request.method == "POST":
        action = request.form.get("action", "profile")

        if action == "profile":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            if not name or len(name) > 100 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                flash("Enter a name (up to 100 characters) and a valid email address.", "error")
                return render_template("account.html")
            try:
                db.execute(
                    "UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?",
                    (name, email, phone, g.user["id"]),
                )
                db.commit()
            except sqlite3.IntegrityError:
                db.rollback()
                flash("That email address is already used by another account.", "error")
                return render_template("account.html")
            log_action(g.user["id"], "Updated account profile")
            flash("Your profile has been updated.", "success")
            return redirect(url_for("auth.account"))

        if action == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            user = db.execute(
                "SELECT password_hash FROM users WHERE id = ?", (g.user["id"],)
            ).fetchone()
            if not check_password_hash(user["password_hash"], current_password):
                flash("Your current password is incorrect.", "error")
            elif len(new_password) < 10:
                flash("Your new password must be at least 10 characters long.", "error")
            elif new_password != confirm_password:
                flash("The new passwords do not match.", "error")
            elif new_password == current_password:
                flash("Choose a new password that differs from your current one.", "error")
            else:
                db.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (generate_password_hash(new_password), g.user["id"]),
                )
                db.commit()
                log_action(g.user["id"], "Changed account password")
                flash("Your password has been changed.", "success")
                return redirect(url_for("auth.account"))
        else:
            flash("Choose a valid account action.", "error")

    return render_template("account.html")

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    # Always scope to the server-authenticated session user (never trust request args)
    auth_user_id = g.user["id"]
    db = get_db()

    # 1. Booking history for the logged-in user
    bookings = db.execute(
        """SELECT b.id, b.event_id, b.ticket_type, b.unit_price, b.currency,
                  b.quantity, b.status, b.created_at,
                  e.title AS event_title, e.date AS event_date, e.venue,
                  CASE WHEN replace(e.date, 'T', ' ') > ? THEN 1 ELSE 0 END AS can_cancel,
                  c.name AS category_name
           FROM bookings b
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ?
           ORDER BY b.created_at DESC, b.id DESC""",
        (current_event_time(), auth_user_id)
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
             AND replace(e.date, 'T', ' ') > ?
           GROUP BY e.id, e.title, e.date, e.venue, c.name
           ORDER BY replace(e.date, 'T', ' ') ASC""",
        (auth_user_id, current_event_time())
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
        active_tickets=active_tickets,
        now_event_time=current_event_time(),
    )
