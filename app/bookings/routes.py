import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
    g,
    session,
)
from werkzeug.exceptions import HTTPException

from app.database import get_db
from app.models import log_action
from app.security import login_required, check_ownership
from app.time_utils import current_event_time, parse_event_time

bookings_bp = Blueprint("bookings", __name__)

# Prices are in Indian rupees. Every ticket costs at least ₹200.
TICKET_PRICES = {
    "Student": 200,
    "Standard": 299,
    "VIP": 799,
}


@bookings_bp.route("/book/<int:event_id>", methods=["POST"])
@login_required
def create_booking(event_id):
    db = get_db()

    ticket_type = request.form.get("ticket_type", "Standard").strip()
    if ticket_type not in TICKET_PRICES:
        ticket_type = "Standard"

    try:
        quantity = int(request.form.get("quantity", "1"))
    except ValueError:
        flash("Please enter a valid numeric ticket quantity.", "error")
        return redirect(url_for("events.event_detail", event_id=event_id))

    max_per_booking = current_app.config.get("MAX_TICKETS_PER_BOOKING", 4)
    max_per_user = current_app.config.get("MAX_TICKETS_PER_USER_PER_EVENT", 4)

    if quantity < 1 or quantity > max_per_booking:
        flash(
            f"You may book between 1 and {max_per_booking} tickets per transaction.",
            "error",
        )
        return redirect(url_for("events.event_detail", event_id=event_id))

    unit_price = TICKET_PRICES[ticket_type]

    try:
        # Lock the database transaction while checking availability and booking.
        db.execute("BEGIN IMMEDIATE")

        event = db.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

        if event is None:
            db.rollback()
            abort(404)

        try:
            event_is_upcoming = parse_event_time(event["date"]) > parse_event_time(current_event_time())
        except (TypeError, ValueError):
            event_is_upcoming = False
        if not event_is_upcoming:
            db.rollback()
            flash("Tickets cannot be booked for an event that has already started.", "error")
            return redirect(url_for("events.event_detail", event_id=event_id))

        user_existing = db.execute(
            """SELECT COALESCE(SUM(quantity), 0) AS total
               FROM bookings
               WHERE user_id = ? AND event_id = ? AND status = 'Confirmed'""",
            (g.user["id"], event_id),
        ).fetchone()["total"]

        if user_existing + quantity > max_per_user:
            db.rollback()
            flash(
                f"Booking limit reached: You already hold {user_existing} "
                f"ticket(s) for this event (maximum {max_per_user} allowed per user).",
                "error",
            )
            return redirect(url_for("events.event_detail", event_id=event_id))

        total_booked = db.execute(
            """SELECT COALESCE(SUM(quantity), 0) AS total
               FROM bookings
               WHERE event_id = ? AND status = 'Confirmed'""",
            (event_id,),
        ).fetchone()["total"]

        if total_booked + quantity > event["capacity"]:
            db.rollback()
            flash(
                "Not enough seats remaining for this event to complete your request.",
                "error",
            )
            return redirect(url_for("events.event_detail", event_id=event_id))

        cursor = db.execute(
            """INSERT INTO bookings
               (user_id, event_id, ticket_type, unit_price, currency, quantity, status)
               VALUES (?, ?, ?, ?, 'INR', ?, 'Confirmed')""",
            (g.user["id"], event_id, ticket_type, unit_price, quantity),
        )
        booking_id = cursor.lastrowid

        for _ in range(quantity):
            code = f"TKT-{uuid.uuid4().hex.upper()}"
            db.execute(
                """INSERT INTO tickets (booking_id, ticket_code, status)
                   VALUES (?, ?, 'Valid')""",
                (booking_id, code),
            )

        db.commit()

        log_action(
            g.user["id"],
            f"Created booking #{booking_id} "
            f"({quantity}x {ticket_type} @ ₹{unit_price:.2f}) "
            f"for event #{event_id}",
        )

        flash(
            "Tickets booked successfully! View your booking summary below.",
            "success",
        )
        return redirect(url_for("bookings.payment_confirmation", booking_id=booking_id))

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        current_app.logger.error(
            f"Booking transaction failed for user #{g.user['id']}: {e}"
        )
        flash(
            "An unexpected database error occurred during booking. Please try again.",
            "error",
        )
        return redirect(url_for("events.event_detail", event_id=event_id))


@bookings_bp.route("/bookings/<int:booking_id>/confirmation")
@login_required
def confirmation(booking_id):
    db = get_db()

    booking = db.execute(
        """SELECT b.*, e.title AS event_title, e.date AS event_date, e.venue,
                  u.name AS user_name, u.email AS user_email
           FROM bookings b
           JOIN events e ON b.event_id = e.id
           JOIN users u ON b.user_id = u.id
           WHERE b.id = ?""",
        (booking_id,),
    ).fetchone()

    if booking is None:
        abort(404)

    check_ownership(booking["user_id"])
    unit_price = booking["unit_price"]
    total_price = unit_price * booking["quantity"]

    tickets = db.execute(
        "SELECT * FROM tickets WHERE booking_id = ? ORDER BY id ASC",
        (booking_id,),
    ).fetchall()

    return render_template(
        "confirmation.html",
        booking=booking,
        tickets=tickets,
        unit_price=unit_price,
        total_price=total_price,
    )


@bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    db = get_db()
    booking = db.execute(
        """SELECT b.id, b.user_id, b.status, e.date AS event_date
           FROM bookings b JOIN events e ON e.id = b.event_id
           WHERE b.id = ?""",
        (booking_id,),
    ).fetchone()
    if booking is None:
        abort(404)
    check_ownership(booking["user_id"])

    if booking["status"] != "Confirmed":
        flash("This booking is not active and cannot be cancelled.", "error")
        return redirect(url_for("auth.dashboard"))
    try:
        event_is_upcoming = parse_event_time(booking["event_date"]) > parse_event_time(current_event_time())
    except (TypeError, ValueError):
        event_is_upcoming = False
    if not event_is_upcoming:
        flash("Bookings can only be cancelled before the event starts.", "error")
        return redirect(url_for("auth.dashboard"))

    db.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = ?", (booking_id,))
    db.execute(
        "UPDATE tickets SET status = 'Cancelled' WHERE booking_id = ? AND status = 'Valid'",
        (booking_id,),
    )
    db.commit()
    log_action(g.user["id"], f"Cancelled booking #{booking_id}")
    flash("Booking cancelled. The seats are available again.", "success")
    return redirect(url_for("auth.dashboard"))


@bookings_bp.route("/payment/<int:booking_id>", methods=["GET", "POST"])
@login_required
def payment_confirmation(booking_id):
    """Show a payment confirmation screen for an existing booking.

    This is intentionally a confirmation step rather than a real payment
    gateway. The confirmed state is kept in the user's session until a
    payment provider is connected.
    """
    db = get_db()
    booking = db.execute(
        """SELECT b.*, e.title AS event_title, e.date AS event_date, e.venue
           FROM bookings b
           JOIN events e ON e.id = b.event_id
           WHERE b.id = ?""",
        (booking_id,),
    ).fetchone()

    if booking is None:
        abort(404)

    check_ownership(booking["user_id"])
    total_price = booking["unit_price"] * booking["quantity"]

    if request.method == "POST":
        session[f"payment_confirmed_{booking_id}"] = True

    return render_template(
        "payment_confirmation.html",
        booking=booking,
        total_price=total_price,
        payment_confirmed=session.get(f"payment_confirmed_{booking_id}", False),
    )
