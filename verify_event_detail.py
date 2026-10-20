import os
import subprocess
import sys

EVENT_DETAIL_HTML = """{% extends "base.html" %}
{% block content %}
{% set booked = event['booked_count'] | default(0, true) %}
{% set remaining = event['capacity'] - booked %}
{% set pct = ((booked / event['capacity']) * 100) | round | int if event['capacity'] > 0 else 0 %}

<div style="margin-bottom: 1.5rem;">
    <a href="{{ url_for('events.list_events') }}" class="btn btn-secondary btn-sm">&larr; Back to Event Listings</a>
</div>

<div class="detail-layout">
    <!-- Main Event Information Column -->
    <div class="card" style="padding: 0; overflow: hidden;">
        <!-- Event Banner Graphic -->
        <div class="event-card-media" style="aspect-ratio: 21 / 9;">
            <svg class="event-card-svg" viewBox="0 0 840 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{ event['category_name'] }} event banner">
                <defs>
                    <linearGradient id="detail-bg-{{ event['id'] }}" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0f172a" />
                        <stop offset="50%" stop-color="#2e1065" />
                        <stop offset="100%" stop-color="#6d28d9" />
                    </linearGradient>
                    <linearGradient id="detail-acc-{{ event['id'] }}" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.4" />
                        <stop offset="100%" stop-color="#ec4899" stop-opacity="0.25" />
                    </linearGradient>
                </defs>
                <rect width="840" height="360" fill="url(#detail-bg-{{ event['id'] }})" />
                <circle cx="700" cy="80" r="160" fill="url(#detail-acc-{{ event['id'] }})" />
                <circle cx="120" cy="300" r="130" fill="url(#detail-acc-{{ event['id'] }})" />
                <path d="M0 280 Q 220 210 420 280 T 840 240 L 840 360 L 0 360 Z" fill="rgba(255,255,255,0.05)" />
            </svg>
            <div class="event-card-overlay">
                <div class="event-card-top-tags">
                    <span class="badge">{{ event['category_name'] }}</span>
                    <span class="seat-pill">EVENT ID #{{ event['id'] }}</span>
                </div>
            </div>
        </div>

        <div style="padding: 2rem;">
            <h1 style="font-size: clamp(1.5rem, 3vw, 2.2rem); margin-bottom: 1rem;">{{ event['title'] }}</h1>

            <div class="event-meta-list" style="margin-bottom: 1.5rem;">
                <div class="meta-item">
                    <span class="meta-label">Date &amp; Time:</span>
                    <span><strong>{{ event['date'] }}</strong></span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Venue:</span>
                    <span>{{ event['venue'] }}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Organizer:</span>
                    <span>{{ event['organizer_name'] }}</span>
                </div>
            </div>

            <hr class="divider">

            <h3 style="margin-bottom: 0.75rem;">About This Event</h3>
            <!-- Safely rendered using Jinja2 auto-escaping (preventing raw injection / XSS) -->
            <p class="desc" style="font-size: 1rem; line-height: 1.8; white-space: pre-line;">{{ event['description'] }}</p>

            <hr class="divider">

            <h3 style="margin-bottom: 0.75rem;">Configured Ticket Tiers &amp; Pricing</h3>
            <div class="stats-grid" style="margin-bottom: 0;">
                <div class="card" style="margin-bottom: 0; background: var(--surface-page);">
                    <span class="badge">Standard Pass</span>
                    <h4 style="font-size: 1.25rem; margin: 0.25rem 0;">Free / Included</h4>
                    <p class="meta">General admission access to all keynote sessions and expo floors.</p>
                </div>
                <div class="card" style="margin-bottom: 0; background: var(--surface-page);">
                    <span class="badge">VIP Tier</span>
                    <h4 style="font-size: 1.25rem; margin: 0.25rem 0;">Reserved Seating</h4>
                    <p class="meta">Priority front-row seating and direct networking with guest organizers.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Booking Sidebar Column -->
    <div class="card sticky-card">
        <h3>Reserve Tickets</h3>
        <div class="capacity-wrap">
            <div class="capacity-header">
                <span>Real-Time Availability</span>
                <span><strong>{{ remaining_seats }}</strong> / {{ event['capacity'] }} seats</span>
            </div>
            <progress class="capacity-progress" value="{{ booked }}" max="{{ event['capacity'] }}" aria-label="Seat availability progress"></progress>
        </div>
        <p class="meta">Policy: Maximum 4 tickets per user registration.</p>

        {% if g.user %}
            {% if remaining_seats > 0 %}
            <form method="POST" action="{{ url_for('bookings.create_booking', event_id=event['id']) }}" class="form-stack">
                <div class="form-group">
                    <label for="ticket_type">Select Ticket Type</label>
                    <select name="ticket_type" id="ticket_type" required>
                        <option value="Standard">Standard Admission (Free)</option>
                        <option value="Student">Student Pass (Free)</option>
                        <option value="VIP">VIP Reserved Pass</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="quantity">Quantity (1 - 4)</label>
                    <input type="number" name="quantity" id="quantity" min="1" max="4" value="1" required>
                </div>

                <button type="submit" class="btn btn-primary btn-block">Book Tickets Now</button>
            </form>
            {% else %}
                <div class="alert alert-error" style="margin-top: 1rem;">This event is currently sold out.</div>
            {% endif %}
        {% else %}
            <div class="hint-box">
                <p>Please <a href="{{ url_for('auth.login') }}"><strong>sign in</strong></a> or <a href="{{ url_for('auth.register') }}"><strong>create an account</strong></a> to proceed with ticket booking.</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

# Write updated event_detail.html
target_path = "app/templates/event_detail.html"
with open(target_path, "w", encoding="utf-8") as f:
    f.write(EVENT_DETAIL_HTML.lstrip())
print(f"Updated {target_path}")

# Run tests & verify correct event ID loading and 404 handling
print("\nRunning test suite and verifying event ID detail routes...")
res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
if res.returncode != 0:
    sys.exit(res.returncode)

from app import create_app
from app.models import init_and_seed_db

app = create_app()
with app.app_context():
    init_and_seed_db()
    client = app.test_client()

    # Test valid event IDs
    r1 = client.get("/events/1")
    assert r1.status_code == 200
    assert b"NextGen Web Engineering Conference" in r1.data, "Event #1 title mismatch"

    r2 = client.get("/events/2")
    assert r2.status_code == 200
    assert b"Defensive Application Security Summit" in r2.data, "Event #2 title mismatch"

    r3 = client.get("/events/3")
    assert r3.status_code == 200
    assert b"Hands-On Full-Stack Flask Workshop" in r3.data, "Event #3 title mismatch"

    # Test non-existent event ID yields 404
    r_404 = client.get("/events/9999")
    assert r_404.status_code == 404, "Non-existent event ID did not return 404"

print("\nVerification passed: Event details template updated, backend DB integration active, and valid/invalid event IDs tested successfully!")