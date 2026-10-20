from functools import wraps
from flask import session, redirect, url_for, flash, abort, g
from app.database import get_db

def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT id, name, email, phone, role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash("Please log in to continue.", "error")
                return redirect(url_for("auth.login"))
            if g.user["role"] not in allowed_roles:
                abort(403)
            return view(**kwargs)
        return wrapped_view
    return decorator

def check_ownership(owner_user_id):
    """Ensures only the resource owner or an admin can access the record."""
    if g.user is None:
        abort(403)
    if g.user["role"] == "admin":
        return True
    if g.user["id"] != owner_user_id:
        abort(403)
    return True