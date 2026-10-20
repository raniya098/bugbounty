from app import create_app
from app.models import init_and_seed_db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        init_and_seed_db()
    app.run(host="127.0.0.1", port=5000, debug=True)