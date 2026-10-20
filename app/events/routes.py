from flask import Blueprint, render_template, request, abort
from app.database import get_db

events_bp = Blueprint("events", __name__)

@events_bp.route("/events")
def list_events():
    db = get_db()
    search_query = request.args.get("q", "").strip()
    category_id = request.args.get("category", "").strip()

    sql = """
        SELECT e.*, c.name AS category_name, u.name AS organizer_name,
               COALESCE((SELECT SUM(quantity) FROM bookings b WHERE b.event_id = e.id AND b.status = 'Confirmed'), 0) AS booked_count
        FROM events e
        JOIN event_categories c ON e.category_id = c.id
        JOIN users u ON e.organizer_id = u.id
        WHERE 1=1
    """
    params = []

    if search_query:
        sql += " AND e.title LIKE ?"
        params.append(f"%{search_query}%")

    if category_id and category_id.isdigit():
        sql += " AND e.category_id = ?"
        params.append(int(category_id))

    sql += " ORDER BY e.date ASC"
    events = db.execute(sql, params).fetchall()
    categories = db.execute("SELECT * FROM event_categories ORDER BY name ASC").fetchall()

    return render_template(
        "events.html",
        events=events,
        categories=categories,
        search_query=search_query,
        selected_category=category_id
    )

@events_bp.route("/events/<int:event_id>")
def event_detail(event_id):
    db = get_db()
    event = db.execute(
        """SELECT e.*, c.name AS category_name, u.name AS organizer_name,
                  COALESCE((SELECT SUM(quantity) FROM bookings b WHERE b.event_id = e.id AND b.status = 'Confirmed'), 0) AS booked_count
           FROM events e
           JOIN event_categories c ON e.category_id = c.id
           JOIN users u ON e.organizer_id = u.id
           WHERE e.id = ?""",
        (event_id,)
    ).fetchone()

    if event is None:
        abort(404)

    remaining_seats = max(0, event["capacity"] - event["booked_count"])
    return render_template(
        "event_detail.html",
        event=event,
        remaining_seats=remaining_seats
    )