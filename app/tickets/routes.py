from flask import Blueprint, render_template, abort, g
from app.database import get_db
from app.security import login_required

tickets_bp = Blueprint("tickets", __name__)

@tickets_bp.route("/my-tickets")
@login_required
def my_tickets():
    # Strictly use the authenticated user's session ID on the server
    auth_user_id = g.user["id"]
    db = get_db()
    tickets = db.execute(
        """SELECT t.id, t.booking_id, t.ticket_code, t.status,
                  b.ticket_type, b.status AS booking_status, b.created_at AS booked_at,
                  e.id AS event_id, e.title AS event_title, e.date AS event_date, e.venue,
                  c.name AS category_name
           FROM tickets t
           JOIN bookings b ON t.booking_id = b.id
           JOIN events e ON b.event_id = e.id
           JOIN event_categories c ON e.category_id = c.id
           WHERE b.user_id = ?
           ORDER BY e.date ASC, t.id ASC""",
        (auth_user_id,)
    ).fetchall()
    return render_template("my_tickets.html", tickets=tickets)

@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    db = get_db()
    ticket = db.execute(
        """SELECT t.id, t.booking_id, t.ticket_code, t.status,
                  b.user_id, b.ticket_type, b.created_at AS booked_at,
                  e.id AS event_id, e.title AS event_title, e.date AS event_date, e.venue,
                  u.name AS holder_name, u.email AS holder_email
           FROM tickets t
           JOIN bookings b ON t.booking_id = b.id
           JOIN events e ON b.event_id = e.id
           JOIN users u ON b.user_id = u.id
           WHERE t.id = ?""",
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        abort(404)

    # Intentional IDOR vulnerability for the Bug Hunt event: ownership is not checked.

    return render_template("ticket_detail.html", ticket=ticket)
