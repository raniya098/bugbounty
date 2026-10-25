import os
import secrets
from hmac import compare_digest
from flask import Flask, abort, render_template, request, session
from config import Config
from app.database import close_db, get_db
from app.security import load_logged_in_user
from app.time_utils import current_event_time, format_event_time

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV") or os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError("Set a strong SECRET_KEY environment variable before production startup.")
        app.config["SECRET_KEY"] = "local-development-only-change-before-deploy"

    db_dir = os.path.dirname(app.config["DATABASE_PATH"])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    app.teardown_appcontext(close_db)
    app.before_request(load_logged_in_user)

    def csrf_token():
        token = session.get("_csrf_token")
        if token is None:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    app.jinja_env.globals["csrf_token"] = csrf_token
    app.add_template_filter(format_event_time, "event_datetime")

    @app.before_request
    def protect_state_changing_requests():
        if app.testing or request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        expected = session.get("_csrf_token", "")
        submitted = request.form.get("csrf_token", "")
        if not expected or not submitted or not compare_digest(expected, submitted):
            abort(400, description="The form expired. Reload the page and try again.")

    from app.auth.routes import auth_bp
    from app.events.routes import events_bp
    from app.bookings.routes import bookings_bp
    from app.tickets.routes import tickets_bp
    from app.organizer.routes import organizer_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(organizer_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        db = get_db()
        featured_events = db.execute(
            """SELECT e.*, c.name AS category_name, u.name AS organizer_name,
                      COALESCE((SELECT SUM(quantity) FROM bookings b WHERE b.event_id = e.id AND b.status = 'Confirmed'), 0) AS booked_count
               FROM events e
               JOIN event_categories c ON e.category_id = c.id
               JOIN users u ON e.organizer_id = u.id
               WHERE replace(e.date, 'T', ' ') >= ?
               ORDER BY replace(e.date, 'T', ' ') ASC LIMIT 3""",
            (current_event_time(),)
        ).fetchall()
        return render_template("index.html", featured_events=featured_events)

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("403.html"), 403

    @app.errorhandler(400)
    def bad_request_page(error):
        return render_template("400.html", error=error), 400

    @app.errorhandler(404)
    def not_found_page(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("500.html"), 500

    return app
