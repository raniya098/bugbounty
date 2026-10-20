import os
import tempfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "eventhub-secure-production-key-2026")
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        DATABASE_PATH = os.path.join(tempfile.gettempdir(), "eventhub.db")
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, "instance", "eventhub.db")
    MAX_TICKETS_PER_BOOKING = 4
    MAX_TICKETS_PER_USER_PER_EVENT = 4