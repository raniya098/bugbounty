import os
import subprocess
import sys

files = {
    "app/static/css/style.css": """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

:root {
    /* Color Tokens - Purple & White Theme */
    --brand-950: #0f172a;
    --brand-900: #1e1b4b;
    --brand-800: #2e1065;
    --brand-700: #4c1d95;
    --brand-600: #6d28d9;
    --brand-500: #7c3aed;
    --brand-400: #a78bfa;
    --brand-100: #ede9fe;
    --brand-50:  #f5f3ff;

    --surface-page: #f8fafc;
    --surface-card: #ffffff;
    --surface-muted: #f1f5f9;

    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --text-on-brand: #ffffff;

    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --border-focus: #8b5cf6;

    --status-success-bg: #ecfdf5;
    --status-success-text: #047857;
    --status-success-border: #10b981;
    --status-error-bg: #fef2f2;
    --status-error-text: #b91c1c;
    --status-error-border: #ef4444;

    /* Spacing Scale */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;

    /* Border Radius Tokens */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 20px;
    --radius-pill: 9999px;

    /* Shadows */
    --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow-sm: 0 2px 6px -1px rgba(15, 23, 42, 0.06), 0 1px 3px -1px rgba(15, 23, 42, 0.04);
    --shadow-md: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 4px 10px -3px rgba(15, 23, 42, 0.04);
    --shadow-lg: 0 20px 32px -8px rgba(109, 40, 217, 0.14), 0 8px 16px -6px rgba(15, 23, 42, 0.06);
    --focus-ring: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--surface-page);
    background-image:
        radial-gradient(at 0% 0%, rgba(124, 58, 237, 0.06) 0px, transparent 45%),
        radial-gradient(at 100% 0%, rgba(109, 40, 217, 0.04) 0px, transparent 45%);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    -webkit-font-smoothing: antialiased;
}

.container {
    width: 92%;
    max-width: 1200px;
    margin: 0 auto;
}

/* Typography Hierarchy */
h1, h2, h3, h4 {
    color: var(--text-primary);
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.25;
}

h1 {
    font-size: 2rem;
}

h2 {
    font-size: 1.5rem;
}

h3 {
    font-size: 1.15rem;
}

p {
    color: var(--text-secondary);
}

a {
    color: var(--brand-600);
    text-decoration: none;
    transition: color 0.15s ease;
}

a:hover {
    color: var(--brand-700);
}

code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
    background: var(--brand-50);
    color: var(--brand-700);
    padding: 0.2rem 0.45rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--brand-100);
}

/* Navigation Bar */
.navbar {
    background: rgba(15, 23, 42, 0.96);
    backdrop-filter: blur(12px);
    color: var(--text-on-brand);
    padding: 0.9rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: var(--shadow-sm);
}

.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-4);
}

.brand {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-on-brand);
    display: inline-flex;
    align-items: center;
    gap: 0.15rem;
}

.brand:hover {
    color: var(--text-on-brand);
}

.brand span {
    background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: var(--space-5);
    flex-wrap: wrap;
}

.nav-links a:not(.btn) {
    color: #cbd5e1;
    font-weight: 500;
    font-size: 0.92rem;
    padding: 0.35rem 0.15rem;
    position: relative;
}

.nav-links a:not(.btn):hover {
    color: var(--text-on-brand);
}

.user-pill {
    background: rgba(124, 58, 237, 0.22);
    border: 1px solid rgba(167, 139, 250, 0.38);
    color: #f5f3ff;
    padding: 0.3rem 0.85rem;
    border-radius: var(--radius-pill);
    font-size: 0.8rem;
    font-weight: 600;
}

/* Main Content Area */
.main-content {
    flex: 1;
    padding: var(--space-10) 0 var(--space-12);
}

/* Hero Banner */
.hero {
    background: linear-gradient(135deg, var(--brand-950) 0%, var(--brand-800) 52%, var(--brand-600) 100%);
    color: var(--text-on-brand);
    padding: 4.25rem 2.5rem;
    border-radius: var(--radius-xl);
    text-align: center;
    margin-bottom: var(--space-10);
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(167, 139, 250, 0.2);
}

.hero-eyebrow {
    display: inline-block;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.22);
    color: #ddd6fe;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.3rem 0.9rem;
    border-radius: var(--radius-pill);
    margin-bottom: var(--space-4);
}

.hero h1 {
    color: #ffffff;
    font-size: 2.65rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: var(--space-3);
    max-width: 780px;
    margin-left: auto;
    margin-right: auto;
}

.hero p {
    color: #e2e8f0;
    font-size: 1.12rem;
    max-width: 620px;
    margin: 0 auto;
}

.hero-actions {
    margin-top: var(--space-8);
    display: flex;
    justify-content: center;
    gap: var(--space-4);
    flex-wrap: wrap;
}

/* Section Headers */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: var(--space-6);
    flex-wrap: wrap;
    gap: var(--space-3);
}

.section-subtitle {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-top: var(--space-1);
}

.link-more {
    color: var(--brand-600);
    font-weight: 600;
    font-size: 0.95rem;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}

.link-more:hover {
    color: var(--brand-700);
    text-decoration: underline;
}

/* Grids & Layouts */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: var(--space-6);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--space-5);
    margin-bottom: var(--space-8);
}

.detail-layout {
    display: grid;
    grid-template-columns: 1.85fr 1fr;
    gap: var(--space-6);
    align-items: start;
}

.dashboard-layout {
    display: grid;
    grid-template-columns: 1fr 2.15fr;
    gap: var(--space-6);
    align-items: start;
}

.sticky-card {
    position: sticky;
    top: 5.5rem;
}

@media (max-width: 900px) {
    .detail-layout,
    .dashboard-layout {
        grid-template-columns: 1fr;
    }
    .sticky-card {
        position: static;
    }
    .hero h1 {
        font-size: 2rem;
    }
}

/* Cards */
.card {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    margin-bottom: var(--space-6);
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.grid .card,
.stats-grid .card {
    margin-bottom: 0;
}

.stat-card {
    border-left: 4px solid var(--brand-600);
}

.stat-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--brand-700);
    margin: var(--space-1) 0;
}

/* Event Card & Visual Image Banner */
.event-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0;
    overflow: hidden;
}

.event-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--brand-400);
}

.event-card-banner {
    background: linear-gradient(135deg, var(--brand-900) 0%, var(--brand-600) 100%);
    padding: var(--space-5) var(--space-6);
    color: var(--text-on-brand);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-subtle);
}

.event-card-banner .badge {
    background: rgba(255, 255, 255, 0.18);
    color: #ffffff;
    backdrop-filter: blur(4px);
    margin-bottom: 0;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

.seat-pill {
    font-size: 0.76rem;
    font-weight: 600;
    color: #ede9fe;
    background: rgba(15, 23, 42, 0.35);
    padding: 0.2rem 0.65rem;
    border-radius: var(--radius-pill);
}

.event-card-body {
    padding: var(--space-6);
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: space-between;
}

.event-card h3 {
    font-size: 1.2rem;
    margin-bottom: var(--space-3);
    color: var(--text-primary);
}

.event-meta-list {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    margin: var(--space-3) 0 var(--space-4);
}

.auth-card {
    max-width: 500px;
    margin: var(--space-6) auto;
    padding: var(--space-8);
    box-shadow: var(--shadow-md);
}

/* Badges & Text Helpers */
.badge {
    display: inline-block;
    background: var(--brand-100);
    color: var(--brand-700);
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.25rem 0.7rem;
    border-radius: var(--radius-pill);
    margin-bottom: var(--space-2);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.meta {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin: 0.2rem 0;
}

.meta strong {
    color: var(--text-secondary);
    font-weight: 600;
}

.desc {
    margin: var(--space-3) 0 var(--space-4);
    color: var(--text-secondary);
    font-size: 0.94rem;
    line-height: 1.65;
}

.divider {
    border: none;
    border-top: 1px solid var(--border-subtle);
    margin: var(--space-5) 0;
}

/* Native HTML5 Capacity Progress Bar (Zero CSS Linter Warnings) */
.capacity-wrap {
    margin-top: var(--space-3);
    margin-bottom: var(--space-4);
}

.capacity-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
    font-weight: 500;
}

.capacity-progress {
    width: 100%;
    height: 8px;
    appearance: none;
    -webkit-appearance: none;
    border: none;
    border-radius: var(--radius-pill);
    background-color: var(--surface-muted);
    overflow: hidden;
    display: block;
}

.capacity-progress::-webkit-progress-bar {
    background-color: var(--surface-muted);
    border-radius: var(--radius-pill);
}

.capacity-progress::-webkit-progress-value {
    background: linear-gradient(90deg, var(--brand-500) 0%, #ec4899 100%);
    border-radius: var(--radius-pill);
}

.capacity-progress::-moz-progress-bar {
    background: linear-gradient(90deg, var(--brand-500) 0%, #ec4899 100%);
    border-radius: var(--radius-pill);
}

/* Category Pills Bar */
.category-pills {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
    margin-bottom: var(--space-4);
}

.pill-link {
    padding: 0.42rem 0.95rem;
    font-size: 0.84rem;
    font-weight: 600;
    border-radius: var(--radius-pill);
    background: var(--surface-card);
    color: var(--text-secondary);
    border: 1px solid var(--border-subtle);
    transition: all 0.15s ease;
}

.pill-link:hover {
    border-color: var(--brand-400);
    color: var(--brand-600);
    background: var(--brand-50);
}

.pill-link.active {
    background: var(--brand-600);
    color: var(--text-on-brand);
    border-color: var(--brand-600);
    box-shadow: 0 2px 8px rgba(109, 40, 217, 0.25);
}

/* Forms & Inputs */
.form-stack {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    margin-top: var(--space-4);
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}

.form-stack label {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text-secondary);
}

.filter-bar {
    background: var(--surface-card);
    padding: var(--space-4);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-xs);
    display: flex;
    gap: var(--space-3);
    margin: 0 0 var(--space-8);
    flex-wrap: wrap;
    align-items: center;
}

.filter-bar input {
    flex: 1;
    min-width: 220px;
}

.inline-form {
    display: flex;
    gap: var(--space-2);
    align-items: center;
}

input, select, textarea {
    padding: 0.65rem 0.9rem;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    font-size: 0.94rem;
    font-family: inherit;
    color: var(--text-primary);
    background: var(--surface-card);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--border-focus);
    box-shadow: var(--focus-ring);
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    padding: 0.65rem 1.25rem;
    border-radius: var(--radius-sm);
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    border: 1px solid transparent;
    text-align: center;
    font-size: 0.92rem;
    font-family: inherit;
    transition: all 0.18s ease;
}

.btn-primary {
    background: linear-gradient(135deg, var(--brand-500) 0%, var(--brand-600) 100%);
    color: var(--text-on-brand);
    box-shadow: 0 2px 8px rgba(109, 40, 217, 0.25);
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--brand-600) 0%, var(--brand-700) 100%);
    color: var(--text-on-brand);
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(109, 40, 217, 0.32);
}

.btn-secondary {
    background-color: var(--surface-muted);
    color: var(--text-secondary);
    border-color: var(--border-strong);
}

.btn-secondary:hover {
    background-color: #e2e8f0;
    color: var(--text-primary);
}

.btn-outline {
    border-color: rgba(255, 255, 255, 0.35);
    color: var(--text-on-brand);
    padding: 0.38rem 0.9rem;
    background: rgba(255, 255, 255, 0.06);
}

.btn-outline:hover {
    background: rgba(255, 255, 255, 0.16);
    color: var(--text-on-brand);
}

.btn-sm {
    padding: 0.4rem 0.8rem;
    font-size: 0.82rem;
}

.btn-block {
    display: flex;
    width: 100%;
    margin-top: var(--space-3);
}

.action-group {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
}

/* Tables */
.table-responsive {
    width: 100%;
    overflow-x: auto;
}

.table {
    width: 100%;
    border-collapse: collapse;
    margin-top: var(--space-3);
}

.table th {
    background: var(--surface-page);
    color: var(--text-muted);
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.85rem 1rem;
    text-align: left;
    border-bottom: 2px solid var(--border-subtle);
    white-space: nowrap;
}

.table td {
    padding: 0.9rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.92rem;
    color: var(--text-secondary);
    vertical-align: middle;
}

.table tbody tr:hover td {
    background-color: var(--brand-50);
}

/* Alerts */
.flash-messages {
    margin-bottom: var(--space-6);
}

.alert {
    padding: 0.9rem 1.15rem;
    border-radius: var(--radius-md);
    margin-bottom: var(--space-3);
    font-weight: 500;
    font-size: 0.93rem;
    box-shadow: var(--shadow-xs);
}

.alert-success {
    background: var(--status-success-bg);
    color: var(--status-success-text);
    border-left: 4px solid var(--status-success-border);
}

.alert-error {
    background: var(--status-error-bg);
    color: var(--status-error-text);
    border-left: 4px solid var(--status-error-border);
}

/* Ticket Code Pass Display */
.ticket-code-box {
    font-size: 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: var(--brand-700);
    background: linear-gradient(135deg, var(--brand-50) 0%, var(--brand-100) 100%);
    border: 2px dashed var(--brand-400);
    padding: var(--space-5);
    text-align: center;
    border-radius: var(--radius-md);
    margin: var(--space-4) 0;
    letter-spacing: 0.08em;
}

.detail-list {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    margin: var(--space-4) 0;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.93rem;
}

/* Hints & Demo Switcher */
.hint-box {
    margin-top: var(--space-6);
    padding: var(--space-4);
    background: var(--surface-page);
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
}

.hint-box ul {
    margin-left: 1.2rem;
    margin-top: var(--space-2);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.demo-btn-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-2);
    margin-top: var(--space-3);
}

.demo-btn {
    background: var(--surface-card);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.6rem;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    color: var(--text-secondary);
    transition: all 0.15s ease;
}

.demo-btn:hover {
    border-color: var(--brand-600);
    color: var(--brand-600);
    background: var(--brand-50);
}

.empty-state {
    text-align: center;
    padding: var(--space-8) var(--space-4);
    color: var(--text-muted);
}

/* Footer */
.footer {
    background: var(--brand-950);
    color: #94a3b8;
    text-align: center;
    padding: var(--space-6) 0;
    margin-top: auto;
    font-size: 0.88rem;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

@media print {
    .navbar, .footer, .btn {
        display: none !important;
    }
    .card {
        box-shadow: none;
        border: 2px solid #000;
    }
}
""",

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
            <p>&copy; 2026 EventHub &mdash; Fictional Event Registration &amp; Ticket Booking Platform</p>
        </div>
    </footer>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
""",

    "app/templates/index.html": """{% extends "base.html" %}
{% block content %}
<section class="hero">
    <span class="hero-eyebrow">Campus &amp; Tech Event Platform</span>
    <h1>Book Your Spot at Premier Campus &amp; Tech Events</h1>
    <p>Discover conferences, hands-on workshops, and networking sessions with instant digital ticket confirmation.</p>
    <div class="hero-actions">
        <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Explore Events</a>
        {% if not g.user %}
            <a href="{{ url_for('auth.register') }}" class="btn btn-outline">Create Free Account</a>
        {% endif %}
    </div>
</section>

<div class="stats-grid">
    <div class="card stat-card">
        <span class="badge">Instant Access</span>
        <h3>Digital Event Passes</h3>
        <p class="meta">Receive unique, verifiable ticket codes immediately upon booking confirmation.</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Verified Organizers</span>
        <h3>Curated Tech Sessions</h3>
        <p class="meta">Hands-on workshops, AppSec summits, and conferences hosted by domain leads.</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Live Tracking</span>
        <h3>Real-Time Seat Availability</h3>
        <p class="meta">Monitor remaining venue capacity live and manage all your passes in one place.</p>
    </div>
</div>

<section>
    <div class="section-header">
        <div>
            <h2>Featured Events</h2>
            <p class="section-subtitle">Upcoming highlights open for registration</p>
        </div>
        <a href="{{ url_for('events.list_events') }}" class="link-more">View All Events &rarr;</a>
    </div>
    <div class="grid">
        {% for event in featured_events %}
        {% set booked = event['booked_count'] | default(0, true) %}
        {% set remaining = event['capacity'] - booked %}
        <div class="card event-card">
            <div class="event-card-banner">
                <span class="badge">{{ event['category_name'] }}</span>
                <span class="seat-pill">{{ remaining }} seats left</span>
            </div>
            <div class="event-card-body">
                <div>
                    <h3>{{ event['title'] }}</h3>
                    <div class="event-meta-list">
                        <p class="meta"><strong>Date:</strong> {{ event['date'] }}</p>
                        <p class="meta"><strong>Venue:</strong> {{ event['venue'] }}</p>
                        <p class="meta"><strong>Organizer:</strong> {{ event['organizer_name'] }}</p>
                    </div>
                    <p class="desc">{{ event['description'] }}</p>
                </div>
                <div>
                    <div class="capacity-wrap">
                        <div class="capacity-header">
                            <span>Availability</span>
                            <span>{{ remaining }} / {{ event['capacity'] }} seats</span>
                        </div>
                        <progress class="capacity-progress" value="{{ booked }}" max="{{ event['capacity'] }}"></progress>
                    </div>
                    <a href="{{ url_for('events.event_detail', event_id=event['id']) }}" class="btn btn-primary btn-block">View Details &amp; Book</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</section>
{% endblock %}
""",

    "app/templates/events.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>All Upcoming Events</h1>
        <p class="section-subtitle">Browse, filter by category, and reserve your tickets</p>
    </div>
</div>

<div class="category-pills">
    <a href="{{ url_for('events.list_events', q=search_query) }}"
       class="pill-link {% if not selected_category %}active{% endif %}">
        All Events
    </a>
    {% for cat in categories %}
        <a href="{{ url_for('events.list_events', category=cat['id'], q=search_query) }}"
           class="pill-link {% if selected_category == cat['id']|string %}active{% endif %}">
            {{ cat['name'] }}
        </a>
    {% endfor %}
</div>

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
    {% set booked = event['booked_count'] | default(0, true) %}
    {% set remaining = event['capacity'] - booked %}
    <div class="card event-card">
        <div class="event-card-banner">
            <span class="badge">{{ event['category_name'] }}</span>
            <span class="seat-pill">
                {% if remaining > 0 %}{{ remaining }} left{% else %}Sold Out{% endif %}
            </span>
        </div>
        <div class="event-card-body">
            <div>
                <h3>{{ event['title'] }}</h3>
                <div class="event-meta-list">
                    <p class="meta"><strong>Date:</strong> {{ event['date'] }}</p>
                    <p class="meta"><strong>Venue:</strong> {{ event['venue'] }}</p>
                    <p class="meta"><strong>Organizer:</strong> {{ event['organizer_name'] }}</p>
                </div>
                <p class="desc">{{ event['description'] }}</p>
            </div>
            <div>
                <div class="capacity-wrap">
                    <div class="capacity-header">
                        <span>Seats Available</span>
                        <span>{{ remaining }} / {{ event['capacity'] }}</span>
                    </div>
                    <progress class="capacity-progress" value="{{ booked }}" max="{{ event['capacity'] }}"></progress>
                </div>
                <a href="{{ url_for('events.event_detail', event_id=event['id']) }}" class="btn btn-primary btn-block">
                    Event Details &amp; Book
                </a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="card empty-state">
        <p>No events found matching your criteria.</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
""",

    "app/templates/event_detail.html": """{% extends "base.html" %}
{% block content %}
{% set booked = event['booked_count'] | default(0, true) %}

<div class="detail-layout">
    <div class="card">
        <span class="badge">{{ event['category_name'] }}</span>
        <h1>{{ event['title'] }}</h1>
        <div class="event-meta-list">
            <p class="meta"><strong>Date &amp; Time:</strong> {{ event['date'] }}</p>
            <p class="meta"><strong>Venue:</strong> {{ event['venue'] }}</p>
            <p class="meta"><strong>Organizer:</strong> {{ event['organizer_name'] }}</p>
        </div>
        <hr class="divider">
        <h3>Event Description</h3>
        <p class="desc">{{ event['description'] }}</p>
        <hr class="divider">
        <a href="{{ url_for('events.list_events') }}" class="btn btn-secondary">&larr; Back to All Events</a>
    </div>

    <div class="card sticky-card">
        <h3>Ticket Booking</h3>
        <div class="capacity-wrap">
            <div class="capacity-header">
                <span>Available Seats</span>
                <span>{{ remaining_seats }} / {{ event['capacity'] }}</span>
            </div>
            <progress class="capacity-progress" value="{{ booked }}" max="{{ event['capacity'] }}"></progress>
        </div>
        <p class="meta">Limit: Maximum 4 tickets per user.</p>

        {% if g.user %}
            {% if remaining_seats > 0 %}
            <form method="POST" action="{{ url_for('bookings.create_booking', event_id=event['id']) }}" class="form-stack">
                <div class="form-group">
                    <label for="ticket_type">Ticket Type</label>
                    <select name="ticket_type" id="ticket_type" required>
                        <option value="Standard">Standard Admission</option>
                        <option value="Student">Student Pass</option>
                        <option value="VIP">VIP Reserved</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="quantity">Quantity (1 - 4)</label>
                    <input type="number" name="quantity" id="quantity" min="1" max="4" value="1" required>
                </div>

                <button type="submit" class="btn btn-primary btn-block">Book Tickets Now</button>
            </form>
            {% else %}
                <div class="alert alert-error">This event is sold out.</div>
            {% endif %}
        {% else %}
            <div class="hint-box">
                <p>Please <a href="{{ url_for('auth.login') }}"><strong>log in</strong></a> or <a href="{{ url_for('auth.register') }}"><strong>register</strong></a> to book tickets.</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
""",

    "app/templates/register.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h2>Create Your Account</h2>
    <p class="meta">Register as a participant to book and manage event passes.</p>
    <form method="POST" action="{{ url_for('auth.register') }}" class="form-stack">
        <div class="form-group">
            <label for="name">Full Name *</label>
            <input type="text" id="name" name="name" placeholder="Jane Doe" required>
        </div>

        <div class="form-group">
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" placeholder="jane@eventhub.local" required>
        </div>

        <div class="form-group">
            <label for="phone">Phone Number</label>
            <input type="text" id="phone" name="phone" placeholder="555-0199">
        </div>

        <div class="form-group">
            <label for="password">Password (min 6 characters) *</label>
            <input type="password" id="password" name="password" minlength="6" required>
        </div>

        <button type="submit" class="btn btn-primary btn-block">Register</button>
    </form>
    <hr class="divider">
    <p class="meta">Already have an account? <a href="{{ url_for('auth.login') }}">Log in here</a></p>
</div>
{% endblock %}
""",

    "app/templates/login.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h2>Login to EventHub</h2>
    <p class="meta">Sign in with your account credentials below.</p>
    <form method="POST" action="{{ url_for('auth.login') }}" class="form-stack">
        <div class="form-group">
            <label for="email">Email Address</label>
            <input type="email" id="email" name="email" required>
        </div>

        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required>
        </div>

        <button type="submit" class="btn btn-primary btn-block">Sign In</button>
    </form>

    <div class="hint-box">
        <p><strong>Pre-configured Fictional Accounts (Password: <code>Password123!</code>):</strong></p>
        <div class="demo-btn-group">
            <button type="button" class="demo-btn" data-demo-email="alice@eventhub.local">Alice (Participant)</button>
            <button type="button" class="demo-btn" data-demo-email="bob@eventhub.local">Bob (Participant)</button>
            <button type="button" class="demo-btn" data-demo-email="organizer@eventhub.local">Olivia (Organizer)</button>
            <button type="button" class="demo-btn" data-demo-email="admin@eventhub.local">System Admin</button>
        </div>
        <ul>
            <li><strong>Participant 1:</strong> <code>alice@eventhub.local</code></li>
            <li><strong>Participant 2:</strong> <code>bob@eventhub.local</code></li>
            <li><strong>Organizer:</strong> <code>organizer@eventhub.local</code></li>
            <li><strong>Admin:</strong> <code>admin@eventhub.local</code></li>
        </ul>
    </div>
</div>
{% endblock %}
""",

    "app/templates/confirmation.html": """{% extends "base.html" %}
{% block content %}
<div class="card">
    <span class="badge">{{ booking['status'] }}</span>
    <h1>Booking Confirmation #{{ booking['id'] }}</h1>
    <div class="detail-list">
        <div class="detail-row">
            <strong>Event</strong>
            <span>{{ booking['event_title'] }}</span>
        </div>
        <div class="detail-row">
            <strong>Date &amp; Venue</strong>
            <span>{{ booking['event_date'] }} | {{ booking['venue'] }}</span>
        </div>
        <div class="detail-row">
            <strong>Participant</strong>
            <span>{{ booking['user_name'] }} ({{ booking['user_email'] }})</span>
        </div>
        <div class="detail-row">
            <strong>Ticket Package</strong>
            <span>{{ booking['ticket_type'] }} &times; {{ booking['quantity'] }}</span>
        </div>
    </div>

    <h3>Generated Tickets</h3>
    <div class="table-responsive">
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
                    <td><a href="{{ url_for('tickets.ticket_detail', ticket_id=t['id']) }}" class="btn btn-secondary btn-sm">View Ticket</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
""",

    "app/templates/my_tickets.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>My Tickets</h1>
        <p class="section-subtitle">All active passes associated with your account</p>
    </div>
    <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Book More Events</a>
</div>

<div class="card">
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Code</th>
                    <th>Event</th>
                    <th>Date &amp; Venue</th>
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
                    <td><strong>{{ t['event_title'] }}</strong></td>
                    <td>{{ t['event_date'] }} ({{ t['venue'] }})</td>
                    <td>{{ t['ticket_type'] }}</td>
                    <td><span class="badge">{{ t['status'] }}</span></td>
                    <td><a href="{{ url_for('tickets.ticket_detail', ticket_id=t['id']) }}" class="btn btn-secondary btn-sm">View Pass</a></td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="7" class="empty-state">You have not booked any tickets yet. <a href="{{ url_for('events.list_events') }}">Browse events</a>.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
""",

    "app/templates/ticket_detail.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <span class="badge">{{ ticket['status'] }}</span>
    <h2>Event Entry Pass</h2>
    <div class="ticket-code-box">{{ ticket['ticket_code'] }}</div>
    <div class="detail-list">
        <div class="detail-row">
            <strong>Ticket ID</strong>
            <span>#{{ ticket['id'] }} (Booking #{{ ticket['booking_id'] }})</span>
        </div>
        <div class="detail-row">
            <strong>Event</strong>
            <span>{{ ticket['event_title'] }}</span>
        </div>
        <div class="detail-row">
            <strong>Date &amp; Time</strong>
            <span>{{ ticket['event_date'] }}</span>
        </div>
        <div class="detail-row">
            <strong>Venue</strong>
            <span>{{ ticket['venue'] }}</span>
        </div>
        <div class="detail-row">
            <strong>Ticket Type</strong>
            <span>{{ ticket['ticket_type'] }}</span>
        </div>
        <div class="detail-row">
            <strong>Attendee</strong>
            <span>{{ ticket['holder_name'] }} ({{ ticket['holder_email'] }})</span>
        </div>
    </div>
    <button type="button" onclick="window.print()" class="btn btn-primary btn-block">Print / Save Pass as PDF</button>
    <a href="{{ url_for('tickets.my_tickets') }}" class="btn btn-secondary btn-block">&larr; Back to My Tickets</a>
</div>
{% endblock %}
""",

    "app/templates/participant_dashboard.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>Participant Dashboard</h1>
        <p class="section-subtitle">Manage your profile and view booking receipts</p>
    </div>
    <a href="{{ url_for('events.list_events') }}" class="btn btn-primary">Browse Events</a>
</div>

<div class="dashboard-layout">
    <div class="card">
        <h3>Profile Details</h3>
        <div class="detail-list">
            <div class="detail-row">
                <strong>Name</strong>
                <span>{{ g.user['name'] }}</span>
            </div>
            <div class="detail-row">
                <strong>Email</strong>
                <span>{{ g.user['email'] }}</span>
            </div>
            <div class="detail-row">
                <strong>Phone</strong>
                <span>{{ g.user['phone'] or 'N/A' }}</span>
            </div>
            <div class="detail-row">
                <strong>Role</strong>
                <span class="badge">{{ g.user['role'] }}</span>
            </div>
        </div>
    </div>

    <div class="card">
        <h3>Booking History</h3>
        <div class="table-responsive">
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
                        <td><strong>{{ b['event_title'] }}</strong></td>
                        <td>{{ b['event_date'] }}</td>
                        <td>{{ b['quantity'] }} ({{ b['ticket_type'] }})</td>
                        <td><span class="badge">{{ b['status'] }}</span></td>
                        <td><a href="{{ url_for('bookings.confirmation', booking_id=b['id']) }}" class="btn btn-secondary btn-sm">Receipt</a></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="empty-state">No bookings yet.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
""",

    "app/templates/organizer_dashboard.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>Organizer Dashboard</h1>
        <p class="section-subtitle">Create events and monitor attendee registrations</p>
    </div>
    <a href="{{ url_for('organizer.create_event') }}" class="btn btn-primary">+ Create New Event</a>
</div>

{% set total_events = events | length %}
{% set total_booked = events | sum(attribute='booked_count') if events else 0 %}
{% set total_capacity = events | sum(attribute='capacity') if events else 0 %}

<div class="stats-grid">
    <div class="card stat-card">
        <span class="badge">Managed Events</span>
        <div class="stat-value">{{ total_events }}</div>
        <p class="meta">Events assigned to your organizer account</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Tickets Booked</span>
        <div class="stat-value">{{ total_booked }}</div>
        <p class="meta">Confirmed attendee seats reserved</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Total Capacity</span>
        <div class="stat-value">{{ total_capacity }}</div>
        <p class="meta">Combined seat capacity across events</p>
    </div>
</div>

<div class="card">
    <h3>Managed Events</h3>
    <div class="table-responsive">
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
                    <td><a href="{{ url_for('events.event_detail', event_id=ev['id']) }}"><strong>{{ ev['title'] }}</strong></a></td>
                    <td><span class="badge">{{ ev['category_name'] }}</span></td>
                    <td>{{ ev['date'] }}</td>
                    <td>{{ ev['venue'] }}</td>
                    <td>{{ ev['booked_count'] | default(0, true) }} / {{ ev['capacity'] }}</td>
                    <td>
                        <div class="action-group">
                            <a href="{{ url_for('organizer.edit_event', event_id=ev['id']) }}" class="btn btn-secondary btn-sm">Edit</a>
                            <a href="{{ url_for('organizer.event_registrations', event_id=ev['id']) }}" class="btn btn-secondary btn-sm">Registrations</a>
                        </div>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="7" class="empty-state">You have not created any events yet.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
""",

    "app/templates/event_form.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <h2>{% if event %}Edit Event #{{ event['id'] }}{% else %}Create New Event{% endif %}</h2>
    <form method="POST" class="form-stack">
        <div class="form-group">
            <label for="title">Event Title *</label>
            <input type="text" id="title" name="title" value="{{ event['title'] if event else '' }}" required>
        </div>

        <div class="form-group">
            <label for="category_id">Category *</label>
            <select id="category_id" name="category_id" required>
                {% for cat in categories %}
                    <option value="{{ cat['id'] }}" {% if event and event['category_id'] == cat['id'] %}selected{% endif %}>
                        {{ cat['name'] }}
                    </option>
                {% endfor %}
            </select>
        </div>

        <div class="form-group">
            <label for="date">Date &amp; Time (YYYY-MM-DD HH:MM) *</label>
            <input type="text" id="date" name="date" placeholder="2026-12-15 10:00" value="{{ event['date'] if event else '' }}" required>
        </div>

        <div class="form-group">
            <label for="venue">Venue *</label>
            <input type="text" id="venue" name="venue" value="{{ event['venue'] if event else '' }}" required>
        </div>

        <div class="form-group">
            <label for="capacity">Total Capacity *</label>
            <input type="number" id="capacity" name="capacity" min="1" value="{{ event['capacity'] if event else 50 }}" required>
        </div>

        <div class="form-group">
            <label for="description">Event Description *</label>
            <textarea id="description" name="description" rows="4" required>{{ event['description'] if event else '' }}</textarea>
        </div>

        <button type="submit" class="btn btn-primary btn-block">Save Event</button>
        <a href="{{ url_for('organizer.dashboard') }}" class="btn btn-secondary btn-block">Cancel</a>
    </form>
</div>
{% endblock %}
""",

    "app/templates/organizer_registrations.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>Registrations: {{ event['title'] }}</h1>
        <p class="section-subtitle">{{ event['date'] }} &bull; {{ event['venue'] }}</p>
    </div>
    <a href="{{ url_for('organizer.dashboard') }}" class="btn btn-secondary">&larr; Back to Organizer Dashboard</a>
</div>

<div class="card">
    <div class="table-responsive">
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
                    <td><strong>{{ reg['participant_name'] }}</strong></td>
                    <td>{{ reg['participant_email'] }}</td>
                    <td>{{ reg['ticket_type'] }}</td>
                    <td>{{ reg['quantity'] }}</td>
                    <td><span class="badge">{{ reg['status'] }}</span></td>
                    <td>{{ reg['created_at'] }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="7" class="empty-state">No bookings recorded for this event yet.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
""",

    "app/templates/admin_panel.html": """{% extends "base.html" %}
{% block content %}
<div class="section-header">
    <div>
        <h1>Admin Management Panel</h1>
        <p class="section-subtitle">Platform-wide user roles, event oversight, and security audit logs</p>
    </div>
</div>

<div class="stats-grid">
    <div class="card stat-card">
        <span class="badge">Total Users</span>
        <div class="stat-value">{{ users | length }}</div>
        <p class="meta">Registered platform accounts</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Active Events</span>
        <div class="stat-value">{{ events | length }}</div>
        <p class="meta">Published events across categories</p>
    </div>
    <div class="card stat-card">
        <span class="badge">Audit Entries</span>
        <div class="stat-value">{{ logs | length }}</div>
        <p class="meta">Recent recorded system actions</p>
    </div>
</div>

<div class="card">
    <h3>User Accounts &amp; Roles</h3>
    <div class="table-responsive">
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
                    <td><strong>{{ u['name'] }}</strong></td>
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
                            <button type="submit" class="btn btn-secondary btn-sm">Update</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<div class="card">
    <h3>All Platform Events</h3>
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Organizer</th>
                    <th>Category</th>
                    <th>Date</th>
                    <th>Booked / Capacity</th>
                </tr>
            </thead>
            <tbody>
                {% for ev in events %}
                <tr>
                    <td>#{{ ev['id'] }}</td>
                    <td><a href="{{ url_for('events.event_detail', event_id=ev['id']) }}"><strong>{{ ev['title'] }}</strong></a></td>
                    <td>{{ ev['organizer_name'] }}</td>
                    <td><span class="badge">{{ ev['category_name'] }}</span></td>
                    <td>{{ ev['date'] }}</td>
                    <td>{{ ev['booked_count'] | default(0, true) }} / {{ ev['capacity'] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<div class="card">
    <h3>Audit Logs</h3>
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Timestamp</th>
                    <th>User</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td>#{{ log['id'] }}</td>
                    <td>{{ log['timestamp'] }}</td>
                    <td>{{ log['user_email'] or 'System' }}</td>
                    <td>{{ log['action'] }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4" class="empty-state">No audit logs recorded yet.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
""",

    "app/templates/403.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <span class="badge">Error 403</span>
    <h1>Access Denied</h1>
    <p class="desc">You do not have permission to view this page or resource.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary btn-block">Return to Home</a>
</div>
{% endblock %}
""",

    "app/templates/404.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <span class="badge">Error 404</span>
    <h1>Page Not Found</h1>
    <p class="desc">The page or record you requested does not exist.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary btn-block">Return to Home</a>
</div>
{% endblock %}
""",

    "app/templates/500.html": """{% extends "base.html" %}
{% block content %}
<div class="card auth-card">
    <span class="badge">Error 500</span>
    <h1>Internal Server Error</h1>
    <p class="desc">Something went wrong on our end. Please try again later.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary btn-block">Return to Home</a>
</div>
{% endblock %}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {path}")

print("\nRunning automated test suite...")
res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
sys.exit(res.returncode)