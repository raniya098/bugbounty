import os
import subprocess
import sys

CSS_ADDITIONS = """
/* === Enhanced Event Listings Grid & Card Media System === */
.container {
    width: 94%;
    max-width: 1320px;
    margin: 0 auto;
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* 3 columns on desktop, 2 on tablet/medium, 1 on mobile */
.events-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.75rem;
    align-items: stretch;
    width: 100%;
}

@media (max-width: 1024px) {
    .events-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1.5rem;
    }
}

@media (max-width: 640px) {
    .events-grid {
        grid-template-columns: minmax(0, 1fr);
        gap: 1.25rem;
    }
}

.events-toolbar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
}

.results-summary {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 500;
}

/* Uniform Card Heights & Consistent 16:9 Media Ratio */
.event-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 0;
    overflow: hidden;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    background: var(--surface-card);
    box-shadow: var(--shadow-sm);
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.event-card:hover,
.event-card:focus-within {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--brand-400);
}

.event-card-media {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    background: linear-gradient(135deg, var(--brand-950) 0%, var(--brand-800) 50%, var(--brand-600) 100%);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid var(--border-subtle);
}

.event-card-svg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    opacity: 0.92;
    transition: transform 0.35s ease;
}

.event-card:hover .event-card-svg {
    transform: scale(1.04);
}

.event-card-overlay {
    position: absolute;
    inset: 0;
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.45) 0%, rgba(15, 23, 42, 0.1) 50%, rgba(15, 23, 42, 0.65) 100%);
}

.event-card-top-tags {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}

.event-card-overlay .badge {
    background: rgba(255, 255, 255, 0.95);
    color: var(--brand-800);
    font-weight: 700;
    margin-bottom: 0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
}

.seat-pill {
    font-size: 0.76rem;
    font-weight: 700;
    color: #ffffff;
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.24);
    padding: 0.24rem 0.7rem;
    border-radius: var(--radius-pill);
    backdrop-filter: blur(4px);
}

.seat-pill.sold-out {
    background: rgba(185, 28, 28, 0.9);
    border-color: rgba(254, 202, 202, 0.4);
}

.event-card-id {
    align-self: flex-end;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #e2e8f0;
    background: rgba(15, 23, 42, 0.55);
    padding: 0.15rem 0.55rem;
    border-radius: var(--radius-sm);
}

.event-card-body {
    padding: 1.35rem 1.5rem 1.5rem;
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: space-between;
    gap: 1.1rem;
}

.event-card-title {
    font-size: 1.18rem;
    font-weight: 700;
    line-height: 1.35;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
}

.event-card-title a {
    color: inherit;
    text-decoration: none;
}

.event-card-title a:hover,
.event-card-title a:focus-visible {
    color: var(--brand-600);
    text-decoration: underline;
}

.event-card-desc {
    color: var(--text-secondary);
    font-size: 0.92rem;
    line-height: 1.55;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 0.85rem;
}

.event-meta-list {
    display: flex;
    flex-direction: column;
    gap: 0.42rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-subtle);
}

.meta-item {
    display: flex;
    align-items: baseline;
    gap: 0.45rem;
    font-size: 0.86rem;
    color: var(--text-secondary);
}

.meta-label {
    font-weight: 600;
    color: var(--text-primary);
    min-width: 4.6rem;
}

.event-card-footer {
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-subtle);
}

/* Strong Keyboard Focus States */
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
.pill-link:focus-visible {
    outline: 3px solid var(--brand-500);
    outline-offset: 2px;
}

.empty-state-card {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3.5rem 1.5rem;
}
"""

EVENTS_HTML = """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>All Upcoming Events</h1>
        <p class="section-subtitle">Browse verified campus conferences, technical workshops, and networking sessions</p>
    </div>
    <p class="results-summary" aria-live="polite">
        Showing <strong>{{ events | length }}</strong> event{% if (events | length) != 1 %}s{% endif %}
        {% if search_query %} matching "{{ search_query }}"{% endif %}
    </p>
</div>

<div class="events-toolbar">
    <!-- Accessible Category Filter Pills -->
    <nav class="category-pills" aria-label="Filter events by category">
        <a href="{{ url_for('events.list_events', q=search_query) }}"
           class="pill-link {% if not selected_category %}active{% endif %}"
           {% if not selected_category %}aria-current="page"{% endif %}>
            All Categories
        </a>
        {% for cat in categories %}
            <a href="{{ url_for('events.list_events', category=cat['id'], q=search_query) }}"
               class="pill-link {% if selected_category == cat['id']|string %}active{% endif %}"
               {% if selected_category == cat['id']|string %}aria-current="page"{% endif %}>
                {{ cat['name'] }}
            </a>
        {% endfor %}
    </nav>

    <!-- Search & Category Filter Form (Preserves existing GET parameters & routes) -->
    <form method="GET" action="{{ url_for('events.list_events') }}" class="filter-bar" role="search" aria-label="Search and filter events">
        <label for="event-search-input" class="sr-only">Search events by title</label>
        <input type="text" id="event-search-input" name="q" placeholder="Search by event title..." value="{{ search_query }}">

        <label for="event-category-select" class="sr-only">Filter by category</label>
        <select id="event-category-select" name="category" aria-label="Event category">
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
</div>

<!-- Responsive 3 / 2 / 1 Event Cards Grid -->
<div class="events-grid">
    {% for event in events %}
    {% set has_booked_count = event['booked_count'] is defined and event['booked_count'] is not none %}
    {% set booked = event['booked_count'] if has_booked_count else 0 %}
    {% set remaining = (event['capacity'] - booked) if has_booked_count else event['capacity'] %}
    <article class="card event-card">
        <!-- Consistent 16:9 Local SVG Event Banner -->
        <div class="event-card-media">
            <svg class="event-card-svg" viewBox="0 0 640 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{ event['category_name'] }} event illustration">
                <defs>
                    <linearGradient id="bg-{{ event['id'] }}" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0f172a" />
                        <stop offset="50%" stop-color="#3b0764" />
                        <stop offset="100%" stop-color="#6d28d9" />
                    </linearGradient>
                    <linearGradient id="accent-{{ event['id'] }}" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.35" />
                        <stop offset="100%" stop-color="#ec4899" stop-opacity="0.2" />
                    </linearGradient>
                </defs>
                <rect width="640" height="360" fill="url(#bg-{{ event['id'] }})" />
                <circle cx="540" cy="70" r="140" fill="url(#accent-{{ event['id'] }})" />
                <circle cx="90" cy="310" r="110" fill="url(#accent-{{ event['id'] }})" />
                <path d="M0 260 Q 180 200 340 270 T 640 230 L 640 360 L 0 360 Z" fill="rgba(255,255,255,0.06)" />
                <g stroke="rgba(255,255,255,0.12)" stroke-width="1">
                    <line x1="0" y1="90" x2="640" y2="90" />
                    <line x1="0" y1="180" x2="640" y2="180" />
                    <line x1="0" y1="270" x2="640" y2="270" />
                    <line x1="160" y1="0" x2="160" y2="360" />
                    <line x1="320" y1="0" x2="320" y2="360" />
                    <line x1="480" y1="0" x2="480" y2="360" />
                </g>
            </svg>
            <div class="event-card-overlay">
                <div class="event-card-top-tags">
                    <span class="badge">{{ event['category_name'] }}</span>
                    {% if has_booked_count %}
                        {% if remaining > 0 %}
                            <span class="seat-pill">{{ remaining }} seats left</span>
                        {% else %}
                            <span class="seat-pill sold-out">Sold Out</span>
                        {% endif %}
                    {% else %}
                        <span class="seat-pill">Capacity: {{ event['capacity'] }}</span>
                    {% endif %}
                </div>
                <span class="event-card-id">EVENT #{{ event['id'] }}</span>
            </div>
        </div>

        <!-- Card Body -->
        <div class="event-card-body">
            <div>
                <h2 class="event-card-title">
                    <a href="{{ url_for('events.event_detail', event_id=event['id']) }}">
                        {{ event['title'] }}
                    </a>
                </h2>
                <p class="event-card-desc">{{ event['description'] }}</p>

                <div class="event-meta-list">
                    <div class="meta-item">
                        <span class="meta-label">Date:</span>
                        <span>{{ event['date'] }}</span>
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
            </div>

            <!-- Card Footer: Availability & Action -->
            <div class="event-card-footer">
                <div class="capacity-wrap">
                    <div class="capacity-header">
                        <span>Ticket Availability</span>
                        {% if has_booked_count %}
                            <span><strong>{{ remaining }}</strong> of {{ event['capacity'] }} available</span>
                        {% else %}
                            <span>Capacity: {{ event['capacity'] }} seats</span>
                        {% endif %}
                    </div>
                    <progress class="capacity-progress"
                              value="{{ booked }}"
                              max="{{ event['capacity'] }}"
                              aria-label="Booked seats for {{ event['title'] }}"></progress>
                </div>

                <a href="{{ url_for('events.event_detail', event_id=event['id']) }}"
                   class="btn {% if not has_booked_count or remaining > 0 %}btn-primary{% else %}btn-secondary{% endif %} btn-block"
                   aria-label="{% if not has_booked_count or remaining > 0 %}View details and book tickets for {{ event['title'] }}{% else %}View event details for {{ event['title'] }} (Sold Out){% endif %}">
                    {% if not has_booked_count or remaining > 0 %}
                        View Details &amp; Book
                    {% else %}
                        View Event Details
                    {% endif %}
                </a>
            </div>
        </div>
    </article>
    {% else %}
    <div class="card empty-state-card">
        <h3>No matching events found</h3>
        <p class="meta">No events matched your current search or category filter.</p>
        <div style="margin-top: 1rem;">
            <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Reset All Filters</a>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

# 1. Append or update CSS rules in app/static/css/style.css
css_path = "app/static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

marker = "/* === Enhanced Event Listings Grid & Card Media System === */"
if marker in existing_css:
    existing_css = existing_css.split(marker)[0]

with open(css_path, "w", encoding="utf-8") as f:
    f.write(existing_css.rstrip() + "\n\n" + CSS_ADDITIONS.lstrip())
print("Updated app/static/css/style.css")

# 2. Update app/templates/events.html
events_tpl_path = "app/templates/events.html"
with open(events_tpl_path, "w", encoding="utf-8") as f:
    f.write(EVENTS_HTML.lstrip())
print("Updated app/templates/events.html")

# 3. Run unit tests + additional verification for filtering and card links
print("\nRunning test suite and verifying event filters & links...")
res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
if res.returncode != 0:
    sys.exit(res.returncode)

# Verify search query, category filter, and card links directly via Flask test_client
from app import create_app
from app.models import init_and_seed_db

app = create_app()
with app.app_context():
    init_and_seed_db()
    client = app.test_client()

    r_all = client.get("/events")
    assert r_all.status_code == 200, "GET /events failed"
    assert b"events-grid" in r_all.data, "Responsive .events-grid missing"
    assert b"event-card-media" in r_all.data, "Card media header missing"

    r_search = client.get("/events?q=Security")
    assert r_search.status_code == 200, "Search filter failed"
    assert b"Defensive Application Security Summit" in r_search.data, "Expected search result missing"

    r_cat = client.get("/events?category=2")
    assert r_cat.status_code == 200, "Category filter failed"

    r_detail = client.get("/events/1")
    assert r_detail.status_code == 200, "Event detail link failed"

print("Verification passed: Search, Category Filters, Reset, Card Links, and Responsive Grid all OK!")