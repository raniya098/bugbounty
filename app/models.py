import uuid
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
"""

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

    user_count = db.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
    if user_count > 0:
        return

    # Seed fictional test accounts (Password: Password123!)
    seed_users = [
        ("Admin User", "admin@eventhub.local", "555-0100", generate_password_hash("Password123!"), "admin"),
        ("Olivia Organizer", "organizer@eventhub.local", "555-0101", generate_password_hash("Password123!"), "organizer"),
        ("Oscar Organizer", "oscar@eventhub.local", "555-0102", generate_password_hash("Password123!"), "organizer"),
        ("Alice Participant", "alice@eventhub.local", "555-0201", generate_password_hash("Password123!"), "participant"),
        ("Bob Participant", "bob@eventhub.local", "555-0202", generate_password_hash("Password123!"), "participant"),
    ]
    db.executemany(
        "INSERT INTO users (name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)",
        seed_users
    )

    # Seed Categories
    categories = [
        ("Technology",),            # ID 1
        ("Cybersecurity",),         # ID 2
        ("Workshop",),              # ID 3
        ("Cultural & Networking",), # ID 4
        ("AI & Data Science",),     # ID 5
        ("Cloud Computing",)        # ID 6
    ]
    db.executemany("INSERT OR IGNORE INTO event_categories (name) VALUES (?)", categories)

    # 15 Events across different categories
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
            3, 3, 40
        ),
        (
            "Annual Campus Founder & Tech Mixer",
            "Connect with student builders, project organizers, and industry mentors over networking sessions.",
            "2026-12-12 17:00",
            "Student Center Terrace",
            4, 3, 120
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
            6, 3, 150
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
            1, 3, 70
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
            6, 3, 90
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
            3, 3, 50
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
            1, 3, 130
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

    # Seed initial bookings and tickets for Alice (user_id=4) and Bob (user_id=5)
    cursor1 = db.execute(
        "INSERT INTO bookings (user_id, event_id, ticket_type, quantity, status) VALUES (?, ?, ?, ?, 'Confirmed')",
        (4, 1, "VIP", 2)
    )
    b1_id = cursor1.lastrowid
    for _ in range(2):
        db.execute(
            "INSERT INTO tickets (booking_id, ticket_code, status) VALUES (?, ?, 'Valid')",
            (b1_id, f"TKT-{uuid.uuid4().hex[:8].upper()}")
        )

    cursor2 = db.execute(
        "INSERT INTO bookings (user_id, event_id, ticket_type, quantity, status) VALUES (?, ?, ?, ?, 'Confirmed')",
        (5, 2, "Standard", 1)
    )
    b2_id = cursor2.lastrowid
    db.execute(
        "INSERT INTO tickets (booking_id, ticket_code, status) VALUES (?, ?, 'Valid')",
        (b2_id, f"TKT-{uuid.uuid4().hex[:8].upper()}")
    )

    db.commit()