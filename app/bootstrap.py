"""Create the Flask app and prepare its database for the current runtime."""

from app import create_app
from app.models import init_and_seed_db


def create_initialized_app():
    app = create_app()
    with app.app_context():
        init_and_seed_db()
    return app
