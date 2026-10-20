import os
from flask import Flask, render_template
from config import Config
from app.database import close_db, get_db
from app.security import load_logged_in_user

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    app.teardown_appcontext(close_db)
    app.before_request(load_logged_in_user)

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
               ORDER BY e.date ASC LIMIT 3"""
        ).fetchall()
        return render_template("index.html", featured_events=featured_events)

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found_page(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("500.html"), 500

    return app