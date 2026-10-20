import os

files = {
    "app/templates/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EventHub | Event Registration & Ticket Booking</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header class="navbar">
        <div class="container nav-container">
            <a href="{{ url_for('index') }}" class="brand">Event<span>Hub</span></a>
            <nav class="nav-links">
                <a href="{{ url_for('index') }}">Home</a>
                <a href="{{ url_for('events.list_events') }}">Events</a>
                {% if g.user %}
                    <a href="{{ url_for('tickets.my_tickets') }}">My Tickets</a>
                    <a href="{{ url_for('auth.dashboard') }}">Profile</a>
                    {% if g.user['role'] in ['organizer', 'admin'] %}
                        <a href="{{ url_for('organizer.dashboard') }}">Organizer</a>
                    {% endif %}
                    {% if g.user['role'] == 'admin' %}
                        <a href="{{ url_for('admin.panel') }}">Admin</a>
                    {% endif %}
                    <span class="user-pill">{{ g.user['name'] }} ({{ g.user['role'] }})</span>
                    <a href="{{ url_for('auth.logout') }}" class="btn btn-outline">Logout</a>
                {% else %}
                    <a href="{{ url_for('auth.login') }}">Login</a>
                    <a href="{{ url_for('auth.register') }}" class="btn btn-primary">Register</a>
                {% endif %}
            </nav>
        </div>
    </header>

    <main class="container main-content">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2026 EventHub — Fictional Event Registration & Ticket Booking Platform</p>
        </div>
    </footer>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>""",

    "app/templates/index.html": """{% extends "base.html" %}
{% block content %}
<section class="hero">
    <h1>Book Your Spot at Premier Campus & Tech Events</h1>
    <p>Discover conferences, hands-on workshops, and networking sessions with instant ticket confirmation.</p>
    <div class="hero-actions">
        <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Explore Events</a>
        {% if not g.user %}
            <a href="{{ url_for('auth.register') }}" class="btn btn-secondary">Create Free Account</a>
        {% endif %}
    </div>
</section>

<section>
    <div class="section-header">
        <h2>Featured Events</h2>
        <a href="{{ url_for('events.list_events') }}" class="link-more">View All Events &rarr;</a>
    </div>
    <div class="grid">
        {% for event in featured_events %}
        <div class="card event-card">
            <div>
                <span class="badge">{{ event['category_name'] }}</span>
                <h3>{{ event['title'] }}</h3>
                <p class="meta"><strong>Date:</strong> {{ event['date'] }}</p>
                <p class="meta"><strong>Venue:</strong> {{ event['venue'] }}</p>
                <p class="meta"><strong>Organizer:</strong> {{ event['organizer_name'] }}</p>
                <p class="desc">{{ event['description'] }}</p>
            </div>
            <a href="{{ url_for('events.event_detail', event_id=event['id']) }}" class="btn btn-primary btn-block">View Details & Book</a>
        </div>
        {% endfor %}
    </div>
</section>
{% endblock %}""",

    "app/templates/events.html": """{% extends "base.html" %}
{% block content %}
<h1>All Upcoming Events</h1>

<form method="GET" action="{{ url_for('events.list_events') }}" class="filter-bar">
    <input type="text" name="q" placeholder="Search by event title..." value="{{ search_query }}">
    <select name="category">
        <option value="">All Categories</option>
        {% for cat in categories %}
            <option value="{{ cat['id'] }}" {% if selected_category == cat['id']|string %}selected{% endif %}>
                {{ cat['name'] }}
            </option>
        {% endfor %}
    </select>
    <button type="submit" class="btn btn-primary">Search</button>
    <a href="{{ url_for('events.list_events') }}" class="btn btn-secondary">Reset</a>
</form>

<div class="grid">
    {% for event in events %}
    <div class="card event-card">
        <div>
            <span class="badge">{{ event['category_name'] }}</span>
            <h3>{{ event['title'] }}</h3>
            <p class="meta"><strong>Date:</strong> {{ event['date'] }}</p>
            <p class="meta"><strong>Venue:</strong> {{ event['venue'] }}</p>
            <p class="meta"><strong>Organizer:</strong> {{ event['organizer_name'] }}</p>
            <p class="meta"><strong>Seats Available:</strong> {{ event['capacity'] - (event['booked_count'] if 'booked_count' in event.keys() else 0) }} / {{ event['capacity'] }}</p>
        </div>
        <a href="{{ url_for('events.event_detail', event_id=event['id']) }}" class="btn btn-primary btn-block">Event Details</a>
    </div>
    {% else %}
    <div class="card">
        <p>No events found matching your criteria.</p>
    </div>
    {% endfor %}
</div>
{% endblock %}""",

    "app/templates/event_detail.html": """{% extends "base.html" %}
{% block content %}
<div class="detail-layout">
    <div class="card">
        <span class="badge">{{ event['category_name'] }}</span>
        <h1>{{ event['title'] }}</h1>
        <p class="meta"><strong>Date & Time:</strong> {{ event['date'] }}</p>
        <p class="meta"><strong>Venue:</strong> {{ event['venue'] }}</p>
        <p class="meta"><strong>Organizer:</strong> {{ event['organizer_name'] }}</p>
        <hr class="divider">
        <h3>Event Description</h3>
        <p>{{ event['description'] }}</p>
    </div>

    <div class="card">
        <h3>Ticket Booking</h3>
        <p class="meta"><strong>Available Seats:</strong> {{ remaining_seats }} / {{ event['capacity'] }}</p>
        <p class="meta">Limit: Maximum 4 tickets per user.</p>

        {% if g.user %}
            {% if remaining_seats > 0 %}
            <form method="POST" action="{{ url_for('bookings.create_booking', event_id=event['id']) }}" class="form-stack">
                <label for="ticket_type">Ticket Type</label>
                <select name="ticket_type" id="ticket_type" required>
                    <option value="Standard">Standard Admission</option>
                    <option value="Student">Student Pass</option>
                    <option value="VIP">VIP Reserved</option>
                </select>

                <label for="quantity">Quantity (1 - 4)</label>
                <input type="number" name="quantity" id="quantity" min="1" max="4" value="1" required>

                <button type="submit" class="btn btn-primary btn-block">Book Tickets Now</button>
            </form>
            {% else %}
                <div class="alert alert-error">This event is sold out.</div>
            {% endif %}
        {% else %}
            <p style="margin-top: 1rem;">Please <a href="{{ url_for('auth.login') }}">log in</a> or <a href="{{ url_for('auth.register') }}">register</a> to book tickets.</p>
        {% endif %}
    </div>
</div>
{% endblock %}""",

    "app/templates/register.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h2>Create Your Account</h2>
    <form method="POST" action="{{ url_for('auth.register') }}" class="form-stack">
        <label for="name">Full Name *</label>
        <input type="text" id="name" name="name" placeholder="Jane Doe" required>

        <label for="email">Email Address *</label>
        <input type="email" id="email" name="email" placeholder="jane@eventhub.local" required>

        <label for="phone">Phone Number</label>
        <input type="text" id="phone" name="phone" placeholder="555-0199">

        <label for="password">Password (min 6 characters) *</label>
        <input type="password" id="password" name="password" minlength="6" required>

        <button type="submit" class="btn btn-primary btn-block">Register</button>
    </form>
    <p class="meta" style="margin-top: 1rem;">Already have an account? <a href="{{ url_for('auth.login') }}">Log in</a></p>
</div>
{% endblock %}""",

    "app/templates/login.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h2>Login to EventHub</h2>
    <form method="POST" action="{{ url_for('auth.login') }}" class="form-stack">
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" required>

        <label for="password">Password</label>
        <input type="password" id="password" name="password" required>

        <button type="submit" class="btn btn-primary btn-block">Sign In</button>
    </form>

    <div class="hint-box">
        <p><strong>Pre-configured Fictional Accounts (Password: <code>Password123!</code>):</strong></p>
        <ul>
            <li><strong>Participant 1:</strong> <code>alice@eventhub.local</code></li>
            <li><strong>Participant 2:</strong> <code>bob@eventhub.local</code></li>
            <li><strong>Organizer:</strong> <code>organizer@eventhub.local</code></li>
            <li><strong>Admin:</strong> <code>admin@eventhub.local</code></li>
        </ul>
    </div>
</div>
{% endblock %}""",

    "app/templates/confirmation.html": """{% extends "base.html" %}
{% block content %}
<div class="card">
    <span class="badge">{{ booking['status'] }}</span>
    <h1>Booking Confirmation #{{ booking['id'] }}</h1>
    <p><strong>Event:</strong> {{ booking['event_title'] }}</p>
    <p><strong>Date & Venue:</strong> {{ booking['event_date'] }} | {{ booking['venue'] }}</p>
    <p><strong>Participant:</strong> {{ booking['user_name'] }} ({{ booking['user_email'] }})</p>
    <p><strong>Ticket Package:</strong> {{ booking['ticket_type'] }} &times; {{ booking['quantity'] }}</p>

    <h3 style="margin-top: 1.5rem;">Generated Tickets</h3>
    <table class="table">
        <thead>
            <tr>
                <th>Ticket ID</th>
                <th>Ticket Code</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for t in tickets %}
            <tr>
                <td>#{{ t['id'] }}</td>
                <td><code>{{ t['ticket_code'] }}</code></td>
                <td><span class="badge">{{ t['status'] }}</span></td>
                <td><a href="{{ url_for('tickets.ticket_detail', ticket_id=t['id']) }}" class="btn btn-secondary">View Ticket</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}""",

    "app/templates/my_tickets.html": """{% extends "base.html" %}
{% block content %}
<h1>My Tickets</h1>
<div class="card">
    <table class="table">
        <thead>
            <tr>
                <th>Ticket ID</th>
                <th>Code</th>
                <th>Event</th>
                <th>Date & Venue</th>
                <th>Type</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for t in tickets %}
            <tr>
                <td>#{{ t['id'] }}</td>
                <td><code>{{ t['ticket_code'] }}</code></td>
                <td>{{ t['event_title'] }}</td>
                <td>{{ t['event_date'] }} ({{ t['venue'] }})</td>
                <td>{{ t['ticket_type'] }}</td>
                <td><span class="badge">{{ t['status'] }}</span></td>
                <td><a href="{{ url_for('tickets.ticket_detail', ticket_id=t['id']) }}" class="btn btn-secondary">View Pass</a></td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7">You have not booked any tickets yet. <a href="{{ url_for('events.list_events') }}">Browse events</a>.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}""",

    "app/templates/ticket_detail.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <span class="badge">{{ ticket['status'] }}</span>
    <h2>Event Entry Pass</h2>
    <div class="ticket-code-box">{{ ticket['ticket_code'] }}</div>
    <p><strong>Ticket ID:</strong> #{{ ticket['id'] }} (Booking #{{ ticket['booking_id'] }})</p>
    <p><strong>Event:</strong> {{ ticket['event_title'] }}</p>
    <p><strong>Date & Time:</strong> {{ ticket['event_date'] }}</p>
    <p><strong>Venue:</strong> {{ ticket['venue'] }}</p>
    <p><strong>Ticket Type:</strong> {{ ticket['ticket_type'] }}</p>
    <p><strong>Attendee:</strong> {{ ticket['holder_name'] }} ({{ ticket['holder_email'] }})</p>
    <a href="{{ url_for('tickets.my_tickets') }}" class="btn btn-secondary btn-block">&larr; Back to My Tickets</a>
</div>
{% endblock %}""",

    "app/templates/participant_dashboard.html": """{% extends "base.html" %}
{% block content %}
<h1>Participant Dashboard</h1>
<div class="detail-layout">
    <div class="card">
        <h3>Profile Details</h3>
        <p><strong>Name:</strong> {{ g.user['name'] }}</p>
        <p><strong>Email:</strong> {{ g.user['email'] }}</p>
        <p><strong>Phone:</strong> {{ g.user['phone'] or 'N/A' }}</p>
        <p><strong>Role:</strong> <span class="badge">{{ g.user['role'] }}</span></p>
    </div>

    <div class="card">
        <h3>Booking History</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Ref</th>
                    <th>Event</th>
                    <th>Event Date</th>
                    <th>Tickets</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {% for b in bookings %}
                <tr>
                    <td>#{{ b['id'] }}</td>
                    <td>{{ b['event_title'] }}</td>
                    <td>{{ b['event_date'] }}</td>
                    <td>{{ b['quantity'] }} ({{ b['ticket_type'] }})</td>
                    <td><span class="badge">{{ b['status'] }}</span></td>
                    <td><a href="{{ url_for('bookings.confirmation', booking_id=b['id']) }}" class="btn btn-secondary">Receipt</a></td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6">No bookings yet.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}""",

    "app/templates/organizer_dashboard.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <h1>Organizer Dashboard</h1>
    <a href="{{ url_for('organizer.create_event') }}" class="btn btn-primary">+ Create New Event</a>
</div>

<div class="card">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Event Title</th>
                <th>Category</th>
                <th>Date</th>
                <th>Venue</th>
                <th>Booked / Capacity</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for ev in events %}
            <tr>
                <td>#{{ ev['id'] }}</td>
                <td><a href="{{ url_for('events.event_detail', event_id=ev['id']) }}">{{ ev['title'] }}</a></td>
                <td>{{ ev['category_name'] }}</td>
                <td>{{ ev['date'] }}</td>
                <td>{{ ev['venue'] }}</td>
                <td>{{ ev['booked_count'] if 'booked_count' in ev.keys() else 0 }} / {{ ev['capacity'] }}</td>
                <td>
                    <a href="{{ url_for('organizer.edit_event', event_id=ev['id']) }}" class="btn btn-secondary">Edit</a>
                    <a href="{{ url_for('organizer.event_registrations', event_id=ev['id']) }}" class="btn btn-secondary">Registrations</a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7">You have not created any events yet.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}""",

    "app/templates/event_form.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h2>{% if event %}Edit Event #{{ event['id'] }}{% else %}Create New Event{% endif %}</h2>
    <form method="POST" class="form-stack">
        <label for="title">Event Title *</label>
        <input type="text" id="title" name="title" value="{{ event['title'] if event else '' }}" required>

        <label for="category_id">Category *</label>
        <select id="category_id" name="category_id" required>
            {% for cat in categories %}
                <option value="{{ cat['id'] }}" {% if event and event['category_id'] == cat['id'] %}selected{% endif %}>
                    {{ cat['name'] }}
                </option>
            {% endfor %}
        </select>

        <label for="date">Date & Time (YYYY-MM-DD HH:MM) *</label>
        <input type="text" id="date" name="date" placeholder="2026-12-15 10:00" value="{{ event['date'] if event else '' }}" required>

        <label for="venue">Venue *</label>
        <input type="text" id="venue" name="venue" value="{{ event['venue'] if event else '' }}" required>

        <label for="capacity">Total Capacity *</label>
        <input type="number" id="capacity" name="capacity" min="1" value="{{ event['capacity'] if event else 50 }}" required>

        <label for="description">Event Description *</label>
        <textarea id="description" name="description" rows="4" required>{{ event['description'] if event else '' }}</textarea>

        <button type="submit" class="btn btn-primary btn-block">Save Event</button>
    </form>
</div>
{% endblock %}""",

    "app/templates/organizer_registrations.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <h1>Registrations: {{ event['title'] }}</h1>
    <a href="{{ url_for('organizer.dashboard') }}" class="btn btn-secondary">&larr; Back to Organizer Dashboard</a>
</div>

<div class="card">
    <table class="table">
        <thead>
            <tr>
                <th>Booking ID</th>
                <th>Participant Name</th>
                <th>Participant Email</th>
                <th>Ticket Type</th>
                <th>Quantity</th>
                <th>Status</th>
                <th>Booked At</th>
            </tr>
        </thead>
        <tbody>
            {% for reg in registrations %}
            <tr>
                <td>#{{ reg['booking_id'] }}</td>
                <td>{{ reg['participant_name'] }}</td>
                <td>{{ reg['participant_email'] }}</td>
                <td>{{ reg['ticket_type'] }}</td>
                <td>{{ reg['quantity'] }}</td>
                <td><span class="badge">{{ reg['status'] }}</span></td>
                <td>{{ reg['created_at'] }}</td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7">No bookings recorded for this event yet.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}""",

    "app/templates/admin_panel.html": """{% extends "base.html" %}
{% block content %}
<h1>Admin Management Panel</h1>

<div class="card">
    <h3>User Accounts & Roles</h3>
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Current Role</th>
                <th>Change Role</th>
            </tr>
        </thead>
        <tbody>
            {% for u in users %}
            <tr>
                <td>#{{ u['id'] }}</td>
                <td>{{ u['name'] }}</td>
                <td>{{ u['email'] }}</td>
                <td>{{ u['phone'] }}</td>
                <td><span class="badge">{{ u['role'] }}</span></td>
                <td>
                    <form method="POST" action="{{ url_for('admin.update_role', user_id=u['id']) }}" class="inline-form">
                        <select name="role">
                            <option value="participant" {% if u['role'] == 'participant' %}selected{% endif %}>participant</option>
                            <option value="organizer" {% if u['role'] == 'organizer' %}selected{% endif %}>organizer</option>
                            <option value="admin" {% if u['role'] == 'admin' %}selected{% endif %}>admin</option>
                        </select>
                        <button type="submit" class="btn btn-secondary">Update</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="card">
    <h3>All Platform Events</h3>
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Organizer</th>
                <th>Date</th>
                <th>Capacity</th>
            </tr>
        </thead>
        <tbody>
            {% for ev in events %}
            <tr>
                <td>#{{ ev['id'] }}</td>
                <td><a href="{{ url_for('events.event_detail', event_id=ev['id']) }}">{{ ev['title'] }}</a></td>
                <td>{{ ev['organizer_name'] }}</td>
                <td>{{ ev['date'] }}</td>
                <td>{{ ev['capacity'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}""",

    "app/templates/403.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h1>403 — Access Denied</h1>
    <p>You do not have permission to view this page or resource.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary btn-block">Return to Home</a>
</div>
{% endblock %}""",

    "app/templates/404.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h1>404 — Page Not Found</h1>
    <p>The page or record you requested does not exist.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary btn-block">Return to Home</a>
</div>
{% endblock %}""",

    "app/templates/500.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h1>500 — Internal Server Error</h1>
    <p>Something went wrong on our end. Please try again later.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary btn-block">Return to Home</a>
</div>
{% endblock %}"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Populated {path} ({len(content)} bytes)")

print("\nAll 16 HTML templates have been written and saved!")