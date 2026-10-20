from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, g
from app.database import get_db
from app.models import log_action
from app.security import role_required
from app.time_utils import current_event_time, normalize_event_time, parse_event_time

organizer_bp = Blueprint("organizer", __name__, url_prefix="/organizer")


def _is_future_event_date(value):
    try:
        return parse_event_time(value) > parse_event_time(current_event_time())
    except (TypeError, ValueError):
        return False

@organizer_bp.route("/")
@role_required("organizer", "admin")
def dashboard():
    db = get_db()
    if g.user["role"] == "admin":
        events = db.execute(
            """SELECT e.*, c.name AS category_name, u.name AS organizer_name,
                      COALESCE((SELECT SUM(quantity) FROM bookings b WHERE b.event_id = e.id AND b.status = 'Confirmed'), 0) AS booked_count
               FROM events e
               JOIN event_categories c ON e.category_id = c.id
               JOIN users u ON e.organizer_id = u.id
               ORDER BY e.date ASC"""
        ).fetchall()
    else:
        events = db.execute(
            """SELECT e.*, c.name AS category_name, u.name AS organizer_name,
                      COALESCE((SELECT SUM(quantity) FROM bookings b WHERE b.event_id = e.id AND b.status = 'Confirmed'), 0) AS booked_count
               FROM events e
               JOIN event_categories c ON e.category_id = c.id
               JOIN users u ON e.organizer_id = u.id
               WHERE e.organizer_id = ?
               ORDER BY e.date ASC""",
            (g.user["id"],)
        ).fetchall()

    return render_template("organizer_dashboard.html", events=events)

@organizer_bp.route("/events/new", methods=["GET", "POST"])
@role_required("organizer", "admin")
def create_event():
    db = get_db()
    categories = db.execute("SELECT * FROM event_categories ORDER BY name ASC").fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        date = request.form.get("date", "").strip()
        venue = request.form.get("venue", "").strip()
        category_id = request.form.get("category_id", "").strip()
        capacity_raw = request.form.get("capacity", "50").strip()

        if not title or not description or not date or not venue or not category_id.isdigit():
            flash("Please fill in all required event fields.", "error")
            return render_template("event_form.html", categories=categories, event=None)

        category_exists = db.execute(
            "SELECT 1 FROM event_categories WHERE id = ?", (int(category_id),)
        ).fetchone()
        if not category_exists:
            flash("Please choose a valid event category.", "error")
            return render_template("event_form.html", categories=categories, event=None)

        if not _is_future_event_date(date):
            flash("Choose a future date and time (India time).", "error")
            return render_template("event_form.html", categories=categories, event=None)
        date = normalize_event_time(date)

        try:
            capacity = int(capacity_raw)
            if capacity < 1:
                raise ValueError
        except ValueError:
            flash("Capacity must be a positive number.", "error")
            return render_template("event_form.html", categories=categories, event=None)

        cursor = db.execute(
            """INSERT INTO events (title, description, date, venue, category_id, organizer_id, capacity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, date, venue, int(category_id), g.user["id"], capacity)
        )
        db.commit()
        log_action(g.user["id"], f"Created event #{cursor.lastrowid}: {title}")
        flash("Event created successfully!", "success")
        return redirect(url_for("organizer.dashboard"))

    return render_template("event_form.html", categories=categories, event=None)

@organizer_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@role_required("organizer", "admin")
def edit_event(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        abort(404)

    if g.user["role"] != "admin" and event["organizer_id"] != g.user["id"]:
        abort(403)

    categories = db.execute("SELECT * FROM event_categories ORDER BY name ASC").fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        date = request.form.get("date", "").strip()
        venue = request.form.get("venue", "").strip()
        category_id = request.form.get("category_id", "").strip()
        capacity_raw = request.form.get("capacity", "50").strip()

        if not title or not description or not date or not venue or not category_id.isdigit():
            flash("All fields are required.", "error")
            return render_template("event_form.html", categories=categories, event=event)

        category_exists = db.execute(
            "SELECT 1 FROM event_categories WHERE id = ?", (int(category_id),)
        ).fetchone()
        if not category_exists:
            flash("Please choose a valid event category.", "error")
            return render_template("event_form.html", categories=categories, event=event)

        normalized_date = normalize_event_time(date) if _is_future_event_date(date) else None
        if date != event["date"] and normalized_date is None:
            flash("Choose a future date and time (India time).", "error")
            return render_template("event_form.html", categories=categories, event=event)
        if normalized_date is not None:
            date = normalized_date

        try:
            capacity = int(capacity_raw)
            if capacity < 1:
                raise ValueError
        except ValueError:
            flash("Capacity must be a positive integer.", "error")
            return render_template("event_form.html", categories=categories, event=event)

        confirmed_count = db.execute(
            """SELECT COALESCE(SUM(quantity), 0) AS total
               FROM bookings WHERE event_id = ? AND status = 'Confirmed'""",
            (event_id,),
        ).fetchone()["total"]
        if capacity < confirmed_count:
            flash(
                f"Capacity cannot be lower than the {confirmed_count} tickets already booked.",
                "error",
            )
            return render_template("event_form.html", categories=categories, event=event)

        db.execute(
            """UPDATE events
               SET title = ?, description = ?, date = ?, venue = ?, category_id = ?, capacity = ?
               WHERE id = ?""",
            (title, description, date, venue, int(category_id), capacity, event_id)
        )
        db.commit()
        log_action(g.user["id"], f"Edited event #{event_id}: {title}")
        flash("Event updated successfully!", "success")
        return redirect(url_for("organizer.dashboard"))

    return render_template("event_form.html", categories=categories, event=event)

@organizer_bp.route("/events/<int:event_id>/registrations")
@role_required("organizer", "admin")
def event_registrations(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        abort(404)

    if g.user["role"] != "admin" and event["organizer_id"] != g.user["id"]:
        abort(403)

    registrations = db.execute(
        """SELECT b.id AS booking_id, b.ticket_type, b.quantity, b.status, b.created_at,
                  u.name AS participant_name, u.email AS participant_email
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           WHERE b.event_id = ?
           ORDER BY b.created_at DESC""",
        (event_id,)
    ).fetchall()

    return render_template("organizer_registrations.html", event=event, registrations=registrations)


@organizer_bp.route("/events/<int:event_id>/check-in", methods=["POST"])
@role_required("organizer", "admin")
def check_in_ticket(event_id):
    db = get_db()
    event = db.execute(
        "SELECT id, organizer_id, date FROM events WHERE id = ?", (event_id,)
    ).fetchone()
    if event is None:
        abort(404)
    if g.user["role"] != "admin" and event["organizer_id"] != g.user["id"]:
        abort(403)

    ticket_code = request.form.get("ticket_code", "").strip().upper()
    ticket = db.execute(
        """SELECT t.id, t.status FROM tickets t
           JOIN bookings b ON b.id = t.booking_id
           WHERE t.ticket_code = ? AND b.event_id = ? AND b.status = 'Confirmed'""",
        (ticket_code, event_id),
    ).fetchone()
    if ticket is None:
        flash("No valid ticket with that code was found for this event.", "error")
    elif ticket["status"] != "Valid":
        flash(f"This ticket cannot be checked in (status: {ticket['status']}).", "error")
    else:
        cursor = db.execute(
            "UPDATE tickets SET status = 'Checked In' WHERE id = ? AND status = 'Valid'",
            (ticket["id"],),
        )
        if cursor.rowcount == 1:
            db.commit()
            log_action(g.user["id"], f"Checked in ticket {ticket_code} for event #{event_id}")
            flash("Ticket checked in successfully.", "success")
        else:
            db.rollback()
            flash("This ticket was just checked in and can only be used once.", "error")

    return redirect(url_for("organizer.event_registrations", event_id=event_id))
