from app import create_app
from app.models import init_and_seed_db

app = create_app()

with app.app_context():
    init_and_seed_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
