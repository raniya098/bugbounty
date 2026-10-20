import os
import subprocess
import sys

RESPONSIVE_CSS = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

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
    --radius-sm: 8px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 18px;
    --radius-pill: 9999px;

    /* Shadows */
    --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow-sm: 0 2px 6px -1px rgba(15, 23, 42, 0.06), 0 1px 3px -1px rgba(15, 23, 42, 0.04);
    --shadow-md: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 4px 10px -3px rgba(15, 23, 42, 0.04);
    --shadow-lg: 0 20px 32px -8px rgba(109, 40, 217, 0.14), 0 8px 16px -6px rgba(15, 23, 42, 0.06);
    --focus-ring: 0 0 0 3px rgba(124, 58, 237, 0.22);

    /* Touch Target Minimum */
    --touch-target: 44px;
}

/* Base Reset & Overflow Prevention */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    font-size: 100%;
    -webkit-text-size-adjust: 100%;
    overflow-x: hidden;
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
    overflow-x: hidden;
    width: 100%;
    -webkit-font-smoothing: antialiased;
}

img, svg, video, canvas {
    max-width: 100%;
    height: auto;
}

/* Mobile-First Flexible Container */
.container {
    width: 100%;
    max-width: 1320px;
    margin: 0 auto;
    padding-left: 1rem;
    padding-right: 1rem;
}

@media (min-width: 768px) {
    .container {
        padding-left: 1.75rem;
        padding-right: 1.75rem;
    }
}

@media (min-width: 1024px) {
    .container {
        padding-left: 2.25rem;
        padding-right: 2.25rem;
    }
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

/* Fluid Typography Hierarchy */
h1, h2, h3, h4 {
    color: var(--text-primary);
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.25;
    overflow-wrap: break-word;
}

h1 {
    font-size: clamp(1.5rem, 3.5vw, 2.15rem);
}

h2 {
    font-size: clamp(1.25rem, 2.5vw, 1.55rem);
}

h3 {
    font-size: clamp(1.05rem, 2vw, 1.2rem);
}

p {
    color: var(--text-secondary);
    overflow-wrap: break-word;
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
    font-size: 0.84em;
    background: var(--brand-50);
    color: var(--brand-700);
    padding: 0.2rem 0.45rem;
    border-radius: 6px;
    border: 1px solid var(--brand-100);
    overflow-wrap: anywhere;
    word-break: break-word;
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

/* Mobile-First Responsive Navigation Bar */
.navbar {
    background: rgba(15, 23, 42, 0.96);
    backdrop-filter: blur(12px);
    color: var(--text-on-brand);
    padding: 0.75rem 0;
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
    gap: var(--space-3);
}

.brand {
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-on-brand);
    display: inline-flex;
    align-items: center;
    min-height: var(--touch-target);
}

.brand:hover {
    color: var(--text-on-brand);
}

.brand span {
    background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: var(--touch-target);
    min-height: var(--touch-target);
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-sm);
    color: var(--text-on-brand);
    font-size: 0.88rem;
    font-weight: 600;
    cursor: pointer;
    gap: 0.4rem;
}

.nav-toggle:hover {
    background: rgba(255, 255, 255, 0.16);
}

.nav-links {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 0.35rem;
    padding-top: 0.75rem;
    margin-top: 0.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-links.is-open {
    display: flex;
}

.nav-links a:not(.btn) {
    color: #cbd5e1;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.6rem 0.75rem;
    border-radius: var(--radius-sm);
    min-height: var(--touch-target);
    display: flex;
    align-items: center;
}

.nav-links a:not(.btn):hover {
    color: var(--text-on-brand);
    background: rgba(255, 255, 255, 0.06);
}

.user-pill {
    background: rgba(124, 58, 237, 0.24);
    border: 1px solid rgba(167, 139, 250, 0.38);
    color: #f5f3ff;
    padding: 0.45rem 0.85rem;
    border-radius: var(--radius-pill);
    font-size: 0.82rem;
    font-weight: 600;
    text-align: center;
    overflow-wrap: anywhere;
}

@media (min-width: 768px) {
    .nav-toggle {
        display: none;
    }
    .nav-links {
        display: flex !important;
        width: auto;
        flex-direction: row;
        align-items: center;
        gap: 1.1rem;
        padding-top: 0;
        margin-top: 0;
        border-top: none;
        flex-wrap: wrap;
    }
    .nav-links a:not(.btn) {
        padding: 0.4rem 0.35rem;
    }
}

/* Main Content Area */
.main-content {
    flex: 1;
    padding: 1.5rem 0 2.5rem;
    width: 100%;
}

@media (min-width: 768px) {
    .main-content {
        padding: 2.25rem 0 3rem;
    }
}

/* Hero Banner (Mobile-First) */
.hero {
    background: linear-gradient(135deg, var(--brand-950) 0%, var(--brand-800) 52%, var(--brand-600) 100%);
    color: var(--text-on-brand);
    padding: 2.25rem 1.25rem;
    border-radius: var(--radius-lg);
    text-align: center;
    margin-bottom: var(--space-8);
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(167, 139, 250, 0.2);
}

@media (min-width: 768px) {
    .hero {
        padding: 3.75rem 2.5rem;
        border-radius: var(--radius-xl);
        margin-bottom: var(--space-10);
    }
}

.hero-eyebrow {
    display: inline-block;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.22);
    color: #ddd6fe;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.3rem 0.85rem;
    border-radius: var(--radius-pill);
    margin-bottom: var(--space-3);
}

.hero h1 {
    color: #ffffff;
    font-size: clamp(1.65rem, 4.5vw, 2.65rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: var(--space-3);
    max-width: 780px;
    margin-left: auto;
    margin-right: auto;
}

.hero p {
    color: #e2e8f0;
    font-size: clamp(0.95rem, 2vw, 1.12rem);
    max-width: 620px;
    margin: 0 auto;
}

.hero-actions {
    margin-top: var(--space-6);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.75rem;
}

@media (min-width: 480px) {
    .hero-actions {
        flex-direction: row;
        flex-wrap: wrap;
        gap: var(--space-4);
    }
}

/* Section Headers */
.section-header {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: var(--space-5);
    gap: var(--space-3);
}

@media (min-width: 640px) {
    .section-header {
        flex-direction: row;
        align-items: flex-end;
        margin-bottom: var(--space-6);
    }
}

.section-subtitle {
    color: var(--text-muted);
    font-size: 0.92rem;
    margin-top: var(--space-1);
}

.results-summary {
    font-size: 0.88rem;
    color: var(--text-muted);
    font-weight: 500;
}

.link-more {
    color: var(--brand-600);
    font-weight: 600;
    font-size: 0.95rem;
    display: inline-flex;
    align-items: center;
    min-height: var(--touch-target);
}

/* Mobile-First Responsive Grids (360px -> 768px -> 1024px -> 1440px) */
.grid,
.events-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
    align-items: stretch;
    width: 100%;
}

@media (min-width: 680px) {
    .grid,
    .events-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1.5rem;
    }
}

@media (min-width: 1024px) {
    .grid,
    .events-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1.75rem;
    }
}

.stats-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 1rem;
    margin-bottom: var(--space-6);
}

@media (min-width: 640px) {
    .stats-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1.25rem;
        margin-bottom: var(--space-8);
    }
}

.detail-layout,
.dashboard-layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
    align-items: start;
    width: 100%;
}

@media (min-width: 960px) {
    .detail-layout {
        grid-template-columns: minmax(0, 1.85fr) minmax(300px, 1fr);
        gap: 1.75rem;
    }
    .dashboard-layout {
        grid-template-columns: minmax(260px, 1fr) minmax(0, 2.15fr);
        gap: 1.75rem;
    }
    .sticky-card {
        position: sticky;
        top: 5.5rem;
    }
}

/* Cards */
.card {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-sm);
    max-width: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

@media (min-width: 768px) {
    .card {
        padding: 1.65rem;
        margin-bottom: 1.5rem;
    }
}

.grid .card,
.events-grid .card,
.stats-grid .card {
    margin-bottom: 0;
}

.stat-card {
    border-left: 4px solid var(--brand-600);
}

.stat-value {
    font-size: clamp(1.5rem, 3vw, 1.95rem);
    font-weight: 800;
    color: var(--brand-700);
    margin: var(--space-1) 0;
}

.auth-card {
    width: 100%;
    max-width: 500px;
    margin: 1rem auto;
    padding: 1.35rem;
    box-shadow: var(--shadow-md);
}

@media (min-width: 640px) {
    .auth-card {
        margin: 1.75rem auto;
        padding: 2.15rem;
    }
}

/* Event Card & 16:9 Media Ratio */
.event-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    padding: 0 !important;
    overflow: hidden;
}

.event-card:hover,
.event-card:focus-within {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--brand-400);
}

.event-card-banner {
    background: linear-gradient(135deg, var(--brand-900) 0%, var(--brand-600) 100%);
    padding: 1rem 1.25rem;
    color: var(--text-on-brand);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    border-bottom: 1px solid var(--border-subtle);
}

.event-card-banner .badge {
    background: rgba(255, 255, 255, 0.18);
    color: #ffffff;
    margin-bottom: 0;
    border: 1px solid rgba(255, 255, 255, 0.25);
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
    padding: 0.85rem 1.1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.48) 0%, rgba(15, 23, 42, 0.1) 50%, rgba(15, 23, 42, 0.68) 100%);
}

.event-card-top-tags {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.4rem;
    flex-wrap: wrap;
}

.event-card-overlay .badge {
    background: rgba(255, 255, 255, 0.95);
    color: var(--brand-800);
    font-weight: 700;
    margin-bottom: 0;
}

.seat-pill {
    font-size: 0.74rem;
    font-weight: 700;
    color: #ffffff;
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.24);
    padding: 0.22rem 0.65rem;
    border-radius: var(--radius-pill);
}

.seat-pill.sold-out {
    background: rgba(185, 28, 28, 0.92);
    border-color: rgba(254, 202, 202, 0.4);
}

.event-card-id {
    align-self: flex-end;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #e2e8f0;
    background: rgba(15, 23, 42, 0.6);
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
}

.event-card-body {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: space-between;
    gap: 1rem;
}

@media (min-width: 768px) {
    .event-card-body {
        padding: 1.35rem 1.5rem 1.5rem;
    }
}

.event-card-title {
    font-size: 1.14rem;
    font-weight: 700;
    line-height: 1.35;
    margin-bottom: 0.45rem;
    color: var(--text-primary);
}

.event-card-title a {
    color: inherit;
    text-decoration: none;
}

.event-card-title a:hover {
    color: var(--brand-600);
    text-decoration: underline;
}

.event-card-desc {
    color: var(--text-secondary);
    font-size: 0.91rem;
    line-height: 1.55;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 0.75rem;
}

.event-meta-list {
    display: flex;
    flex-direction: column;
    gap: 0.38rem;
    padding-top: 0.65rem;
    border-top: 1px solid var(--border-subtle);
}

.meta-item {
    display: flex;
    align-items: baseline;
    gap: 0.4rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
    flex-wrap: wrap;
}

.meta-label {
    font-weight: 600;
    color: var(--text-primary);
    min-width: 4.5rem;
}

.event-card-footer {
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-subtle);
}

/* Badges & Text Helpers */
.badge {
    display: inline-block;
    background: var(--brand-100);
    color: var(--brand-700);
    font-size: 0.71rem;
    font-weight: 700;
    padding: 0.24rem 0.65rem;
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

/* Native HTML5 Capacity Progress Bar */
.capacity-wrap {
    margin-top: var(--space-2);
    margin-bottom: var(--space-3);
}

.capacity-header {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    flex-wrap: wrap;
    font-size: 0.81rem;
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

/* Toolbar & Category Filter Pills */
.events-toolbar {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    margin-bottom: 1.5rem;
}

.category-pills {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.35rem;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
}

@media (min-width: 768px) {
    .category-pills {
        flex-wrap: wrap;
        overflow-x: visible;
        padding-bottom: 0;
    }
}

.pill-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 40px;
    padding: 0.45rem 0.95rem;
    font-size: 0.84rem;
    font-weight: 600;
    border-radius: var(--radius-pill);
    background: var(--surface-card);
    color: var(--text-secondary);
    border: 1px solid var(--border-subtle);
    white-space: nowrap;
    flex-shrink: 0;
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

/* Forms & Inputs (Mobile-First Touch Targets) */
.form-stack {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    margin-top: var(--space-4);
    width: 100%;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    width: 100%;
}

.form-stack label {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text-secondary);
}

.filter-bar {
    background: var(--surface-card);
    padding: 0.9rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-xs);
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    margin: 0 0 var(--space-6);
    width: 100%;
}

.filter-bar input,
.filter-bar select,
.filter-bar .btn {
    width: 100%;
    min-width: 0;
}

@media (min-width: 680px) {
    .filter-bar {
        flex-direction: row;
        flex-wrap: wrap;
        align-items: center;
        padding: 1rem;
    }
    .filter-bar input {
        flex: 1 1 220px;
        width: auto;
    }
    .filter-bar select {
        flex: 0 1 200px;
        width: auto;
    }
    .filter-bar .btn {
        width: auto;
    }
}

.inline-form {
    display: flex;
    gap: 0.45rem;
    align-items: center;
    flex-wrap: nowrap;
}

input, select, textarea {
    width: 100%;
    max-width: 100%;
    min-height: var(--touch-target);
    padding: 0.65rem 0.85rem;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    font-size: 0.95rem;
    font-family: inherit;
    color: var(--text-primary);
    background: var(--surface-card);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

textarea {
    min-height: 110px;
    resize: vertical;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--border-focus);
    box-shadow: var(--focus-ring);
}

/* Buttons (Minimum 44px Touch Target) */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    min-height: var(--touch-target);
    padding: 0.65rem 1.2rem;
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
    padding: 0.45rem 0.95rem;
    background: rgba(255, 255, 255, 0.06);
}

.btn-outline:hover {
    background: rgba(255, 255, 255, 0.16);
    color: var(--text-on-brand);
}

.btn-sm {
    min-height: 38px;
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
    gap: 0.45rem;
    flex-wrap: wrap;
}

/* Responsive Tables */
.table-responsive {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: var(--radius-sm);
}

.table {
    width: 100%;
    min-width: 580px;
    border-collapse: collapse;
    margin-top: var(--space-2);
}

.table th {
    background: var(--surface-page);
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.8rem 0.9rem;
    text-align: left;
    border-bottom: 2px solid var(--border-subtle);
    white-space: nowrap;
}

.table td {
    padding: 0.85rem 0.9rem;
    text-align: left;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.9rem;
    color: var(--text-secondary);
    vertical-align: middle;
}

.table tbody tr:hover td {
    background-color: var(--brand-50);
}

/* Alerts */
.flash-messages {
    margin-bottom: var(--space-5);
}

.alert {
    padding: 0.85rem 1.1rem;
    border-radius: var(--radius-md);
    margin-bottom: var(--space-3);
    font-weight: 500;
    font-size: 0.92rem;
    box-shadow: var(--shadow-xs);
    overflow-wrap: break-word;
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

/* Ticket Code Pass Display & Detail Rows */
.ticket-code-box {
    font-size: clamp(1.15rem, 4vw, 1.5rem);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: var(--brand-700);
    background: linear-gradient(135deg, var(--brand-50) 0%, var(--brand-100) 100%);
    border: 2px dashed var(--brand-400);
    padding: 1rem;
    text-align: center;
    border-radius: var(--radius-md);
    margin: var(--space-4) 0;
    letter-spacing: 0.06em;
    overflow-wrap: anywhere;
}

.detail-list {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    margin: var(--space-4) 0;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 0.35rem 1rem;
    padding-bottom: 0.55rem;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.92rem;
}

.detail-row span {
    overflow-wrap: anywhere;
}

/* Hints & Demo Switcher */
.hint-box {
    margin-top: var(--space-5);
    padding: var(--space-4);
    background: var(--surface-page);
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    overflow-wrap: anywhere;
}

.hint-box ul {
    margin-left: 1.15rem;
    margin-top: var(--space-2);
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.demo-btn-group {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.5rem;
    margin-top: var(--space-3);
}

@media (min-width: 440px) {
    .demo-btn-group {
        grid-template-columns: 1fr 1fr;
    }
}

.demo-btn {
    min-height: 40px;
    background: var(--surface-card);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.65rem;
    font-size: 0.82rem;
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

.empty-state,
.empty-state-card {
    grid-column: 1 / -1;
    text-align: center;
    padding: 2.5rem 1.25rem;
    color: var(--text-muted);
}

/* Footer */
.footer {
    background: var(--brand-950);
    color: #94a3b8;
    text-align: center;
    padding: 1.35rem 0;
    margin-top: auto;
    font-size: 0.85rem;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

@media print {
    .navbar, .footer, .btn, .nav-toggle {
        display: none !important;
    }
    .card {
        box-shadow: none;
        border: 2px solid #000;
    }
}
"""

BASE_HTML = """<!DOCTYPE html>
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
            <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle navigation menu">
                Menu &#9776;
            </button>
            <nav class="nav-links" id="primary-nav" aria-label="Primary navigation">
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
"""

MAIN_JS = """document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile navigation toggle
    const navToggle = document.getElementById("nav-toggle");
    const primaryNav = document.getElementById("primary-nav");
    if (navToggle && primaryNav) {
        navToggle.addEventListener("click", () => {
            const isOpen = primaryNav.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    }

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll(".flash-messages .alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.3s ease";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // 3. Quick-fill demo credentials on Login page
    const demoButtons = document.querySelectorAll("[data-demo-email]");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    demoButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            if (emailInput && passwordInput) {
                emailInput.value = btn.getAttribute("data-demo-email");
                passwordInput.value = "Password123!";
                emailInput.focus();
            }
        });
    });
});
"""

with open("app/static/css/style.css", "w", encoding="utf-8") as f:
    f.write(RESPONSIVE_CSS.lstrip())
print("Updated app/static/css/style.css with mobile-first responsive rules")

with open("app/templates/base.html", "w", encoding="utf-8") as f:
    f.write(BASE_HTML.lstrip())
print("Updated app/templates/base.html with accessible mobile menu toggle")

with open("app/static/js/main.js", "w", encoding="utf-8") as f:
    f.write(MAIN_JS.lstrip())
print("Updated app/static/js/main.js with mobile menu toggle handler")

print("\nRunning unit tests and route checks across all 10 page views...")
res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
if res.returncode != 0:
    sys.exit(res.returncode)

from app import create_app
from app.models import init_and_seed_db

app = create_app()
with app.app_context():
    init_and_seed_db()
    client = app.test_client()

    # Public routes
    for path in ["/", "/events", "/events/1", "/register", "/login"]:
        r = client.get(path)
        assert r.status_code == 200, f"Failed GET {path}"
        assert b'name="viewport" content="width=device-width, initial-scale=1.0"' in r.data

    # Participant routes (Alice)
    client.post("/login", data={"email": "alice@eventhub.local", "password": "Password123!"})
    for path in ["/dashboard", "/my-tickets", "/tickets/1", "/bookings/1/confirmation"]:
        r = client.get(path)
        assert r.status_code == 200, f"Failed Participant GET {path}"

    # Organizer routes (Olivia)
    client.get("/logout")
    client.post("/login", data={"email": "organizer@eventhub.local", "password": "Password123!"})
    for path in ["/organizer/", "/organizer/events/new", "/organizer/events/1/edit", "/organizer/events/1/registrations"]:
        r = client.get(path)
        assert r.status_code == 200, f"Failed Organizer GET {path}"

    # Admin routes (Admin)
    client.get("/logout")
    client.post("/login", data={"email": "admin@eventhub.local", "password": "Password123!"})
    r = client.get("/admin/")
    assert r.status_code == 200, "Failed Admin GET /admin/"

print("\nAll 10 EventHub page views verified (200 OK) with responsive viewport, mobile nav, and table wrappers!")