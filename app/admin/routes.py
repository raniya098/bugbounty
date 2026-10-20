from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.database import get_db
from app.models import log_action
from app.security import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@role_required("admin")
def panel():
    db = get_db()
    users = db.execute("SELECT id, name, email, phone, role FROM users ORDER BY id ASC").fetchall()
    events = db.execute(
        """SELECT e.*, u.name AS organizer_name, c.name AS category_name,
                  COALESCE((SELECT SUM(quantity) FROM bookings b WHERE b.event_id = e.id AND b.status = 'Confirmed'), 0) AS booked_count
           FROM events e
           JOIN users u ON e.organizer_id = u.id
           JOIN event_categories c ON e.category_id = c.id
           ORDER BY e.date ASC"""
    ).fetchall()
    logs = db.execute(
        """SELECT l.*, u.email AS user_email
           FROM audit_logs l
           LEFT JOIN users u ON l.user_id = u.id
           ORDER BY l.timestamp DESC LIMIT 30"""
    ).fetchall()
    return render_template("admin_panel.html", users=users, events=events, logs=logs)

@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@role_required("admin")
def update_role(user_id):
    new_role = request.form.get("role", "").strip()
    if new_role not in ("participant", "organizer", "admin"):
        flash("Invalid role specified.", "error")
        return redirect(url_for("admin.panel"))

    db = get_db()
    target = db.execute("SELECT id, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if target is None:
        abort(404)

    if target["role"] == "admin" and new_role != "admin":
        admin_count = db.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'admin'"
        ).fetchone()[0]
        if admin_count <= 1:
            flash("The last administrator cannot be removed or demoted.", "error")
            return redirect(url_for("admin.panel"))

    if target["role"] == "organizer" and new_role != "organizer":
        organizer_count = db.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'organizer'"
        ).fetchone()[0]
        if organizer_count <= 1:
            flash(
                "Keep one organizer account active. Assign Organizer to another user to replace this account.",
                "error",
            )
            return redirect(url_for("admin.panel"))

    previous_organizers = []
    if new_role == "organizer":
        previous_organizers = db.execute(
            "SELECT id FROM users WHERE role = 'organizer' AND id != ?",
            (user_id,),
        ).fetchall()
        if previous_organizers:
            old_ids = [row["id"] for row in previous_organizers]
            placeholders = ", ".join("?" for _ in old_ids)
            db.execute(
                f"UPDATE events SET organizer_id = ? WHERE organizer_id IN ({placeholders})",
                (user_id, *old_ids),
            )
            db.execute(
                f"UPDATE users SET role = 'participant' WHERE id IN ({placeholders})",
                old_ids,
            )

    if target["role"] == new_role and not previous_organizers:
        flash(f"User #{user_id} already has the {new_role} role.", "success")
        return redirect(url_for("admin.panel"))

    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    db.commit()
    log_action(g.user["id"], f"Updated user #{user_id} role to {new_role}")
    if new_role == "organizer" and previous_organizers:
        flash(
            f"User #{user_id} is now the only organizer. Existing events were transferred to this account.",
            "success",
        )
    else:
        flash(f"User #{user_id} role updated to {new_role}.", "success")
    return redirect(url_for("admin.panel"))
