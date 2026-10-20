import csv
from io import StringIO

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
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


def _get_managed_event(db, event_id):
    event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        abort(404)
    if g.user["role"] != "admin" and event["organizer_id"] != g.user["id"]:
        abort(403)
    return event


def _registration_filters():
    search = request.args.get("q", "").strip()[:100]
    status = request.args.get("status", "").strip()
    if status not in {"Confirmed", "Cancelled"}:
        status = ""
    return search, status


def _get_registration_rows(db, search="", status="", event_id=None, organizer_id=None):
    conditions = ["1 = 1"]
    params = []
    if event_id is not None:
        conditions.append("b.event_id = ?")
        params.append(event_id)
    if organizer_id is not None:
        conditions.append("e.organizer_id = ?")
        params.append(organizer_id)
    if status:
        conditions.append("b.status = ?")
        params.append(status)
    if search:
        conditions.append(
            "(CAST(b.id AS TEXT) LIKE ? OR u.name LIKE ? OR u.email LIKE ? "
            "OR COALESCE(u.phone, '') LIKE ? OR e.title LIKE ?)"
        )
        search_pattern = f"%{search}%"
        params.extend([search_pattern] * 5)

    rows = db.execute(
        f"""SELECT b.id AS booking_id, b.ticket_type, b.quantity, b.unit_price,
                      b.currency, b.status AS booking_status, b.created_at,
                      u.name AS participant_name, u.email AS participant_email,
                      COALESCE(u.phone, '') AS participant_phone,
                      e.id AS event_id, e.title AS event_title, e.date AS event_date,
                      e.venue AS event_venue,
                      t.id AS ticket_id, t.ticket_code, t.status AS ticket_status
               FROM bookings b
               JOIN users u ON u.id = b.user_id
               JOIN events e ON e.id = b.event_id
               LEFT JOIN tickets t ON t.booking_id = b.id
               WHERE {' AND '.join(conditions)}
               ORDER BY b.created_at DESC, b.id DESC, t.id ASC""",
        params,
    ).fetchall()

    bookings = {}
    for row in rows:
        booking = bookings.get(row["booking_id"])
        if booking is None:
            booking = {
                "booking_id": row["booking_id"],
                "ticket_type": row["ticket_type"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"],
                "currency": row["currency"],
                "booking_status": row["booking_status"],
                "created_at": row["created_at"],
                "participant_name": row["participant_name"],
                "participant_email": row["participant_email"],
                "participant_phone": row["participant_phone"],
                "event_id": row["event_id"],
                "event_title": row["event_title"],
                "event_date": row["event_date"],
                "event_venue": row["event_venue"],
                "total_price": row["unit_price"] * row["quantity"],
                "tickets": [],
            }
            bookings[row["booking_id"]] = booking
        if row["ticket_id"] is not None:
            booking["tickets"].append({
                "id": row["ticket_id"],
                "ticket_code": row["ticket_code"],
                "status": row["ticket_status"],
            })
    return list(bookings.values())


def _get_registration_stats(db, event_id=None, organizer_id=None):
    conditions = ["1 = 1"]
    params = []
    if event_id is not None:
        conditions.append("b.event_id = ?")
        params.append(event_id)
    if organizer_id is not None:
        conditions.append("e.organizer_id = ?")
        params.append(organizer_id)
    where_clause = " AND ".join(conditions)

    stats = dict(db.execute(
        f"""SELECT
                  COUNT(DISTINCT CASE WHEN b.status = 'Confirmed' THEN b.id END) AS confirmed_bookings,
                  COUNT(DISTINCT CASE WHEN b.status = 'Confirmed' THEN b.user_id END) AS attendees,
                  COALESCE(SUM(CASE WHEN b.status = 'Confirmed' THEN b.quantity ELSE 0 END), 0) AS tickets_sold,
                  COALESCE(SUM(CASE WHEN b.status = 'Confirmed' THEN b.quantity * b.unit_price ELSE 0 END), 0) AS confirmed_value
           FROM bookings b JOIN events e ON e.id = b.event_id
           WHERE {where_clause}""",
        params,
    ).fetchone())
    stats["checked_in"] = db.execute(
        f"""SELECT COUNT(*) AS total
           FROM tickets t JOIN bookings b ON b.id = t.booking_id
           JOIN events e ON e.id = b.event_id
           WHERE {where_clause} AND b.status = 'Confirmed' AND t.status = 'Checked In'""",
        params,
    ).fetchone()["total"]
    return stats


def _csv_cell(value):
    value = "" if value is None else str(value)
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _registration_csv_response(registrations, filename):
    output = StringIO(newline="")
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow([
        "Booking ID", "Attendee name", "Attendee email", "Attendee phone",
        "Event", "Event date", "Venue", "Ticket type", "Quantity",
        "Unit price", "Booking total", "Currency", "Booking status",
        "Booked at (UTC)", "Tickets and statuses",
    ])
    for booking in registrations:
        ticket_summary = "; ".join(
            f"{ticket['ticket_code']} ({ticket['status']})"
            for ticket in booking["tickets"]
        )
        writer.writerow([
            _csv_cell(booking["booking_id"]),
            _csv_cell(booking["participant_name"]),
            _csv_cell(booking["participant_email"]),
            _csv_cell(booking["participant_phone"]),
            _csv_cell(booking["event_title"]),
            _csv_cell(booking["event_date"]),
            _csv_cell(booking["event_venue"]),
            _csv_cell(booking["ticket_type"]),
            _csv_cell(booking["quantity"]),
            _csv_cell(booking["unit_price"]),
            _csv_cell(booking["total_price"]),
            _csv_cell(booking["currency"]),
            _csv_cell(booking["booking_status"]),
            _csv_cell(booking["created_at"]),
            _csv_cell(ticket_summary),
        ])
    response = Response(output.getvalue(), content_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


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

    search, status = _registration_filters()
    selected_event_id = None
    requested_event_id = request.args.get("event_id", "").strip()
    if requested_event_id.isdigit():
        candidate = int(requested_event_id)
        if any(event["id"] == candidate for event in events):
            selected_event_id = candidate

    organizer_id = g.user["id"] if g.user["role"] == "organizer" else None
    registrations = _get_registration_rows(
        db,
        search=search,
        status=status,
        event_id=selected_event_id,
        organizer_id=organizer_id,
    )
    registration_stats = _get_registration_stats(db, organizer_id=organizer_id)

    return render_template(
        "organizer_dashboard.html",
        events=events,
        registrations=registrations,
        registration_stats=registration_stats,
        search=search,
        selected_status=status,
        selected_event_id=selected_event_id,
    )

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
    event = _get_managed_event(db, event_id)
    search, status = _registration_filters()
    registrations = _get_registration_rows(
        db, search=search, status=status, event_id=event_id
    )
    stats = _get_registration_stats(db, event_id=event_id)

    return render_template(
        "organizer_registrations.html",
        event=event,
        registrations=registrations,
        stats=stats,
        search=search,
        selected_status=status,
    )


@organizer_bp.route("/events/<int:event_id>/registrations/export.csv")
@role_required("organizer", "admin")
def export_event_registrations(event_id):
    db = get_db()
    event = _get_managed_event(db, event_id)
    search, status = _registration_filters()
    registrations = _get_registration_rows(
        db, search=search, status=status, event_id=event_id
    )
    return _registration_csv_response(
        registrations, f"event-{event_id}-registrations.csv"
    )


@organizer_bp.route("/registrations/export.csv")
@role_required("organizer", "admin")
def export_all_registrations():
    db = get_db()
    search, status = _registration_filters()
    organizer_id = g.user["id"] if g.user["role"] == "organizer" else None
    requested_event_id = request.args.get("event_id", "").strip()
    event_id = int(requested_event_id) if requested_event_id.isdigit() else None
    if event_id is not None:
        owned_event = db.execute(
            "SELECT id FROM events WHERE id = ? AND (? IS NULL OR organizer_id = ?)",
            (event_id, organizer_id, organizer_id),
        ).fetchone()
        if owned_event is None:
            event_id = None

    registrations = _get_registration_rows(
        db,
        search=search,
        status=status,
        event_id=event_id,
        organizer_id=organizer_id,
    )
    return _registration_csv_response(
        registrations, "organizer-registrations.csv"
    )


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
