import uuid
import os
from werkzeug.security import generate_password_hash
from app.database import get_db

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT DEFAULT '',
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('participant', 'organizer', 'admin')) DEFAULT 'participant'
);

CREATE TABLE IF NOT EXISTS event_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    venue TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    organizer_id INTEGER NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity >= 1),
    FOREIGN KEY (category_id) REFERENCES event_categories (id),
    FOREIGN KEY (organizer_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    ticket_type TEXT NOT NULL DEFAULT 'Standard',
    unit_price INTEGER NOT NULL DEFAULT 299,
    currency TEXT NOT NULL DEFAULT 'INR',
    quantity INTEGER NOT NULL CHECK(quantity >= 1),
    status TEXT NOT NULL DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (event_id) REFERENCES events (id)
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    ticket_code TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'Valid',
    FOREIGN KEY (booking_id) REFERENCES bookings (id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS auth_login_attempts (
    email_hash TEXT PRIMARY KEY,
    attempts INTEGER NOT NULL,
    window_started INTEGER NOT NULL
);
"""

# Schedule and venue details below were filled in for the supplied event posters.
# Ticket prices use the existing Student/Standard/VIP price bands in bookings/routes.py.
POSTER_EVENTS = [
    (
        "OFFSCRIPT",
        "A creative speaking and performance event with short-form storytelling, spoken word, and live stage prompts.",
        "2026-11-02 10:00",
        "Main Auditorium, SNGCET Payyannur",
        "Cultural & Networking",
        80,
    ),
    (
        "REVERIQ",
        "A team-based logic challenge featuring riddles, pattern recognition, and rapid-fire questions.",
        "2026-11-03 10:00",
        "CSE Seminar Hall, SNGCET Payyannur",
        "Technology",
        80,
    ),
    (
        "THE EXPERT HOUR",
        "An interactive expert talk followed by audience questions and a short networking session.",
        "2026-11-04 11:00",
        "Seminar Hall 1, SNGCET Payyannur",
        "Workshop",
        100,
    ),
    (
        "WEB WEAVER",
        "A practical web design and development challenge to plan, build, and present a responsive website.",
        "2026-11-05 09:30",
        "Web Technology Lab, SNGCET Payyannur",
        "Technology",
        60,
    ),
    (
        "SKILLCRAFT",
        "A hands-on skill-building workshop with guided exercises and a short participant showcase.",
        "2026-11-06 13:00",
        "Innovation Lab, SNGCET Payyannur",
        "Workshop",
        50,
    ),
    (
        "QUIZ BUZZ",
        "A quiz competition for teams of two. Book two seats for a complete team. Prizes: ₹2,000 for first place and ₹1,000 for second place.",
        "2026-11-07 13:30",
        "S1 CSE A,B Classroom, SNGCET Payyannur",
        "Cultural & Networking",
        80,
    ),
    (
        "BUG HUNT",
        "A cybersecurity challenge where participants inspect intentionally vulnerable training applications and report their findings.",
        "2026-11-09 10:00",
        "Cyber Range Lab, SNGCET Payyannur",
        "Cybersecurity",
        60,
    ),
    (
        "EL DEBATO",
        "A debate contest with timed rounds, team arguments, rebuttals, and audience judging.",
        "2026-11-10 09:30",
        "Main Auditorium, SNGCET Payyannur",
        "Cultural & Networking",
        80,
    ),
    (
        "PROJECT EXIT",
        "A project showcase where teams demonstrate their work, explain design choices, and receive peer feedback.",
        "2026-11-11 14:00",
        "Project Studio, SNGCET Payyannur",
        "Technology",
        100,
    ),
    (
        "ARCADE ARMAGEDDON",
        "A campus arcade tournament with bracket-based video game challenges and a live finals round.",
        "2026-11-12 11:00",
        "Student Activity Centre, SNGCET Payyannur",
        "Cultural & Networking",
        100,
    ),
    (
        "COLD CASE",
        "A mystery-solving challenge where teams analyze clues, timelines, and case files to reach a conclusion.",
        "2026-11-13 10:00",
        "Seminar Hall 2, SNGCET Payyannur",
        "Cybersecurity",
        60,
    ),
    (
        "FESTIVAL OF FURY",
        "A high-energy campus festival featuring stage performances and team activities.",
        "2026-11-16 09:00",
        "Open-Air Stage, SNGCET Payyannur",
        "Cultural & Networking",
        150,
    ),
    (
        "NOVAHACK",
        "A campus hackathon for building and pitching practical software prototypes to a judging panel.",
        "2026-11-17 09:00",
        "Innovation Hub, SNGCET Payyannur",
        "AI & Data Science",
        100,
    ),
    (
        "TURING TRAIL",
        "A timed programming and problem-solving contest focused on algorithms and computational thinking.",
        "2026-11-18 09:00",
        "Computer Science Block, SNGCET Payyannur",
        "Technology",
        120,
    ),
    (
        "CLOUD COMPUTING WORKSHOP",
        "A hands-on introduction to cloud services: deploy a simple application, configure cloud storage, and explore scaling and access management.",
        "2026-11-19 10:00",
        "Cloud Computing Lab, SNGCET Payyannur",
        "Cloud Computing",
        80,
    ),
]


def _seed_poster_events(db):
    """Add the poster events once, assigning them to the current event owner."""
    owner = db.execute(
        "SELECT id FROM users WHERE role = 'organizer' ORDER BY id LIMIT 1"
    ).fetchone()
    if owner is None:
        owner = db.execute(
            "SELECT id FROM users WHERE role = 'admin' ORDER BY id LIMIT 1"
        ).fetchone()
    if owner is None:
        return

    category_ids = {
        row["name"]: row["id"]
        for row in db.execute("SELECT id, name FROM event_categories").fetchall()
    }

    for title, description, date, venue, category, capacity in POSTER_EVENTS:
        existing = db.execute(
            "SELECT id, date FROM events WHERE title = ? COLLATE NOCASE",
            (title,),
        ).fetchone()
        if existing is not None:
            # Move the existing demo EL DEBATO entry into the requested November schedule.
            # The date guard makes this a one-time update and preserves later organizer edits.
            if title == "EL DEBATO" and existing["date"] == "2026-10-29":
                db.execute(
                    """UPDATE events
                       SET description = ?, date = ?, venue = ?, category_id = ?,
                           organizer_id = ?, capacity = ?
                       WHERE id = ?""",
                    (
                        description,
                        date,
                        venue,
                        category_ids[category],
                        owner["id"],
                        capacity,
                        existing["id"],
                    ),
                )
            continue

        db.execute(
            """INSERT INTO events
               (title, description, date, venue, category_id, organizer_id, capacity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                title,
                description,
                date,
                venue,
                category_ids[category],
                owner["id"],
                capacity,
            ),
        )

def log_action(user_id, action):
    db = get_db()
    db.execute(
        "INSERT INTO audit_logs (user_id, action) VALUES (?, ?)",
        (user_id, action)
    )
    db.commit()

def init_and_seed_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)

    # Add price snapshots to databases created by older versions of EventHub.
    booking_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(bookings)").fetchall()
    }
    if "unit_price" not in booking_columns:
        db.execute("ALTER TABLE bookings ADD COLUMN unit_price INTEGER NOT NULL DEFAULT 0")
        db.execute(
            """UPDATE bookings
               SET unit_price = CASE ticket_type
                   WHEN 'Student' THEN 200
                   WHEN 'VIP' THEN 799
                   ELSE 299
               END"""
        )
    if "currency" not in booking_columns:
        db.execute("ALTER TABLE bookings ADD COLUMN currency TEXT NOT NULL DEFAULT 'INR'")
    db.commit()

    categories = [
        ("Technology",),
        ("Cybersecurity",),
        ("Workshop",),
        ("Cultural & Networking",),
        ("AI & Data Science",),
        ("Cloud Computing",),
    ]
    db.executemany("INSERT OR IGNORE INTO event_categories (name) VALUES (?)", categories)

    user_count = db.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
    on_serverless = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
    production = on_serverless or os.environ.get("FLASK_ENV") == "production"
    seed_demo_data = os.environ.get("SEED_DEMO_DATA", "false" if production else "true").lower() in {
        "1", "true", "yes"
    }
    if user_count == 0 and production and seed_demo_data:
        raise RuntimeError("Set SEED_DEMO_DATA=false in production; demo accounts use known passwords.")
    if user_count == 0 and not seed_demo_data:
        admin_email = os.environ.get("INITIAL_ADMIN_EMAIL", "").strip().lower()
        admin_password = os.environ.get("INITIAL_ADMIN_PASSWORD", "")
        if admin_email and len(admin_password) >= 10:
            db.execute(
                """INSERT INTO users (name, email, password_hash, role)
                   VALUES ('EventHub Admin', ?, ?, 'admin')""",
                (admin_email, generate_password_hash(admin_password)),
            )
        elif production:
            raise RuntimeError(
                "Set INITIAL_ADMIN_EMAIL and a 10+ character INITIAL_ADMIN_PASSWORD before initializing the production database."
            )

    if user_count == 0 and seed_demo_data:
        # Seed fictional test accounts (Password: Password123!)
        seed_users = [
            ("Admin User", "admin@eventhub.local", "555-0100", generate_password_hash("Password123!"), "admin"),
            ("Olivia Organizer", "organizer@eventhub.local", "555-0101", generate_password_hash("Password123!"), "organizer"),
            ("Oscar Participant", "oscar@eventhub.local", "555-0102", generate_password_hash("Password123!"), "participant"),
            ("Alice Participant", "alice@eventhub.local", "555-0201", generate_password_hash("Password123!"), "participant"),
            ("Bob Participant", "bob@eventhub.local", "555-0202", generate_password_hash("Password123!"), "participant"),
        ]
        db.executemany(
            "INSERT INTO users (name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            seed_users
        )

        # 15 sample events across different categories.
        events = [
        (
            "NextGen Web Engineering Conference",
            "A full-day symposium covering modern Python backends, database architecture, and UI design.",
            "2026-11-15 09:30",
            "Main Auditorium, Hall A",
            1, 2, 100
        ),
        (
            "Defensive Application Security Summit",
            "Learn secure coding practices, authentication hardening, and access control design patterns.",
            "2026-11-22 10:00",
            "Seminar Hall 2, Tech Park",
            2, 2, 60
        ),
        (
            "Hands-On Full-Stack Flask Workshop",
            "Interactive workshop building modular web applications with Flask Blueprints and SQLite.",
            "2026-12-05 14:00",
            "Innovation Lab 301",
            3, 2, 40
        ),
        (
            "Annual Campus Founder & Tech Mixer",
            "Connect with student builders, project organizers, and industry mentors over networking sessions.",
            "2026-12-12 17:00",
            "Student Center Terrace",
            4, 2, 120
        ),
        (
            "AI Agent Architecture & LLM Security",
            "Deep dive into building autonomous agents, prompt injection defense, and vector database management.",
            "2026-12-18 10:00",
            "Computer Science Block, Hall B",
            5, 2, 85
        ),
        (
            "Cloud Native Kubernetes Hardening",
            "Container security, pod security standards, and automated CI/CD security posture checks.",
            "2027-01-10 11:00",
            "Virtual / Tech Center Arena",
            6, 2, 150
        ),
        (
            "Penetration Testing 101 Bootcamp",
            "Introduction to network scanning, vulnerability discovery, and ethical hacking fundamentals.",
            "2027-01-15 09:00",
            "Cyber Range Lab 102",
            2, 2, 50
        ),
        (
            "Advanced UI/UX Design Masterclass",
            "Designing accessible, conversion-optimized interfaces using design systems and Figma.",
            "2027-01-20 14:30",
            "Design Studio 4",
            1, 2, 70
        ),
        (
            "Data Science & Predictive Analytics Hackathon",
            "Analyze large open datasets, build machine learning models, and present insights to judges.",
            "2027-02-02 09:00",
            "Innovation Hub Arena",
            5, 2, 110
        ),
        (
            "Serverless Architecture Deep Dive",
            "Building scalable event-driven microservices using AWS Lambda and serverless databases.",
            "2027-02-14 10:30",
            "Auditorium Block C",
            6, 2, 90
        ),
        (
            "Open Source Software Contributors Meetup",
            "Learn how to make your first GitHub pull request, write documentation, and join maintainer circles.",
            "2027-02-20 16:00",
            "Library Conference Room",
            4, 2, 60
        ),
        (
            "Mobile App Development with Flutter",
            "Cross-platform mobile application development workshop from scratch to deployment.",
            "2027-03-01 10:00",
            "Lab 204, Tech Wing",
            3, 2, 50
        ),
        (
            "Blockchain & Smart Contract Auditing",
            "Analyzing Solidity code for reentrancy bugs, integer overflows, and logical vulnerabilities.",
            "2027-03-12 11:30",
            "Seminar Hall 1",
            2, 2, 75
        ),
        (
            "Quantum Computing Introductory Seminar",
            "Understanding qubits, quantum gates, and the future of cryptography.",
            "2027-03-25 15:00",
            "Physics Amphitheater",
            1, 2, 130
        ),
        (
            "Global Tech Career & Internship Fair",
            "Network with recruiters, undergo mock interviews, and land tech internships for the summer.",
            "2027-04-05 09:00",
            "Exhibition Center Main Hall",
            4, 2, 300
        )
        ]

        db.executemany(
            """INSERT OR IGNORE INTO events
               (title, description, date, venue, category_id, organizer_id, capacity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            events
        )

        # Seed initial bookings and tickets for Alice (user_id=4) and Bob (user_id=5).
        cursor1 = db.execute(
            """INSERT INTO bookings
               (user_id, event_id, ticket_type, unit_price, currency, quantity, status)
               VALUES (?, ?, ?, ?, 'INR', ?, 'Confirmed')""",
            (4, 1, "VIP", 799, 2)
        )
        b1_id = cursor1.lastrowid
        for _ in range(2):
            db.execute(
                "INSERT INTO tickets (booking_id, ticket_code, status) VALUES (?, ?, 'Valid')",
                (b1_id, f"TKT-{uuid.uuid4().hex.upper()}")
            )

        cursor2 = db.execute(
            """INSERT INTO bookings
               (user_id, event_id, ticket_type, unit_price, currency, quantity, status)
               VALUES (?, ?, ?, ?, 'INR', ?, 'Confirmed')""",
            (5, 2, "Standard", 299, 1)
        )
        b2_id = cursor2.lastrowid
        db.execute(
            "INSERT INTO tickets (booking_id, ticket_code, status) VALUES (?, ?, 'Valid')",
            (b2_id, f"TKT-{uuid.uuid4().hex.upper()}")
        )

    _seed_poster_events(db)
    db.commit()
