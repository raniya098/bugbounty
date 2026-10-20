import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ON_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
DEFAULT_DATABASE_PATH = (
    os.path.join(os.environ.get("TMPDIR", "/tmp"), "eventhub.db")
    if ON_VERCEL
    else os.path.join(BASE_DIR, "instance", "eventhub.db")
)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", DEFAULT_DATABASE_PATH)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = bool(
        os.environ.get("VERCEL")
        or os.environ.get("VERCEL_ENV")
        or os.environ.get("FLASK_ENV") == "production"
    )
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12
    DEBUG = False
    MAX_TICKETS_PER_BOOKING = 4
    MAX_TICKETS_PER_USER_PER_EVENT = 4
