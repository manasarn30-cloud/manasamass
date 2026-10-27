# StreamFlix — Full-Stack Django Streaming Platform with AI Support Assistant

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![Django](https://img.shields.io/badge/Django-6.1-green.svg)
![Database](https://img.shields.io/badge/SQL-SQLite%20%7C%20PostgreSQL-orange.svg)
![NoSQL](https://img.shields.io/badge/MongoDB-Atlas%20%7C%20PyMongo-brightgreen.svg)
![Styling](https://img.shields.io/badge/UI%2FUX-Cinematic%20Dark%20System-red.svg)
![Tests](https://img.shields.io/badge/Tests-32%20Passed-success.svg)

StreamFlix is a production-grade, full-stack web application inspired by modern cinematic streaming interfaces (such as Netflix). It features an integrated, FAQ-driven AI Support Assistant, resilient multi-database persistence (relational SQL for transactional platform data + MongoDB for unstructured chat logs and feedback), TMDB API integration with strict timeouts and local curated fallback, comprehensive request logging, automated health monitoring, and complete coverage of standard and diagnostic HTTP error codes.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Architecture & Multi-Database Design](#architecture--multi-database-design)
6. [Project Directory Structure](#project-directory-structure)
7. [Installation & Local Setup](#installation--local-setup)
   - [Prerequisites](#prerequisites)
   - [Virtual Environment Setup](#virtual-environment-setup)
   - [Dependency Installation](#dependency-installation)
   - [Environment Configuration](#environment-configuration)
   - [Database Migrations & Data Seeding](#database-migrations--data-seeding)
   - [Creating a Superuser](#creating-a-superuser)
   - [Running the Server](#running-the-server)
8. [Automated Testing](#automated-testing)
9. [AI Support Assistant & Chatbot Architecture](#ai-support-assistant--chatbot-architecture)
10. [Error Code Documentation (8 Codes)](#error-code-documentation)
11. [Third-Party API Integration (TMDB) & Fallback Engine](#third-party-api-integration-tmdb--fallback-engine)
12. [Request Logging & Health Checks](#request-logging--health-checks)
13. [Security Architecture](#security-architecture)
14. [Deployment Guide (Render & HTTPS)](#deployment-guide)
15. [Project Submission Details](#project-submission-details)
16. [Proposed Future Improvement](#proposed-future-improvement)

---

## Project Overview

StreamFlix delivers an entertainment platform browsing experience paired with a real-time, responsive technical help assistant. Users can discover trending blockbusters, search across genres, view detailed movie synopses with embedded official YouTube trailers, maintain a private SQL-backed "My List", consult a searchable knowledge base, and receive intelligent diagnostic support from the **StreamFlix Assistant** on every page.

---

## Problem Statement

Modern web platforms often treat customer support and error handling as disconnected, external third-party widgets or generic static 404 pages. When a user experiences an authentication denial (401), missing page (404), rate limit (429), server hiccup (500), or application-specific diagnostic event (460), they are usually left without clear recovery steps.

**StreamFlix solves this by unifying entertainment browsing with an active contextual support assistant:**
- Instant explanations for technical error codes directly inside the interface.
- Real-time knowledge retrieval from an SQL FAQ database without requiring paid proprietary LLM APIs.
- Seamless escalation to persistent Support Tickets when confidence is low.
- Multi-database architecture separating structured relational entities from conversation histories.

---

## Key Features

- **Cinematic Dark Theme:** Built on a design system with CSS custom properties (`--bg-primary: #08090D`, `--accent-primary: #E5093F`), responsive typography (Inter), glassmorphism headers, and smooth hover elevation.
- **Hero Banner & Horizontal Rows:** Featured movie banner with dark gradient overlay, trailer modal triggers, and horizontally scrollable movie rows (Trending, Popular, Sci-Fi, Action, Thriller, Drama).
- **Interactive Discover & Search:** Real-time query search, genre filter chips, and sorting controls (Highest Rated, Newest, Title A-Z).
- **Movie Details & Official Trailers:** Synopsis, metadata, cast/genre badges, YouTube trailer embed, and recommended similar titles.
- **User Authentication & Session Management:**
  - Secure registration with password strength enforcement and confirmation.
  - Sign-in via username or registered email address.
  - Secure POST-only logout.
  - User profile management.
- **Private SQL "My List":** One-click toggle adding or removing movies from a user's personal list with optimistic AJAX and toast notifications.
- **AI Support Assistant on Every Page:**
  - Floating bottom-right widget with session conversation persistence.
  - Token-overlap and keyword search against SQL FAQ records.
  - Detailed explanations of all 8 required status codes.
  - Automated escalation offering to open a unique Support Ticket (`SF-TICK-XXXXXXXX`).
  - Helpful / Not Helpful feedback rating with MongoDB logging.
- **Resilient Fallback Mode:** Operates with a rich 24-movie curated local catalog if TMDB API is offline or unconfigured.
- **Comprehensive Logging & Health Probes:** Rotating log files recording sanitized HTTP requests and a `/health/` monitoring endpoint reporting status of Django, SQL, MongoDB, and TMDB.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.14, Django 6.1.2 |
| **Frontend** | HTML5, CSS3 (Vanilla Design System), Vanilla JavaScript (ES6+) |
| **Relational Database (SQL)** | SQLite (Development/Testing), PostgreSQL (Production ready) |
| **Document Store (NoSQL)** | MongoDB (Atlas or Local via PyMongo) for chat logs & feedback |
| **External API** | The Movie Database (TMDB) API v3 (5.0s timeout + local fallback) |
| **Production WSGI & Static** | Gunicorn 23.0, WhiteNoise 6.12 |
| **Environment Management** | `python-dotenv` |
| **Testing** | Django Test Framework (Unit & Integration, 32 test cases) |

---

## Architecture & Multi-Database Design

```
+-------------------------------------------------------------------------+
|                                StreamFlix                               |
|                       Client Browser / Mobile App                       |
+------------------------------------+------------------------------------+
                                     |
                                     v
                       +----------------------------+
                       |   Django Request/Response  |
                       |    - RequestLoggingMiddleware
                       |    - SecurityMiddleware     |
                       |    - WhiteNoise (Statics)  |
                       +--------------+-------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
| Relational (SQL) |         | Document (NoSQL) |         | External REST    |
| SQLite / Postgres|         |  MongoDB Atlas   |         |   TMDB API v3    |
+------------------+         +------------------+         +------------------+
| - User / Auth    |         | - chat_logs      |         | - Trending Movies|
| - Movie Metadata |         |   (indexed conv) |         | - Search Movies  |
| - MyList (M2M)   |         | - chat_feedback  |         | - Trailer Videos |
| - FAQ Knowledge  |         |                  |         | - Strict 5s TO   |
| - Support Tickets|         | (Resilient Fall- |         | - Curated Fall-  |
|   (Unique Refs)  |         |  back if offline)|         |   back Catalog   |
+------------------+         +------------------+         +------------------+
```

---

## Project Directory Structure

```
StreamFlix/
|-- accounts/                      # Authentication & Profile management
|   |-- forms.py                   # SignUpForm, LoginForm, ProfileUpdateForm
|   |-- models.py                  # UserProfile extension
|   |-- tests.py                   # Authentication unit tests
|   |-- urls.py                    # /accounts/signup/, /login/, /logout/, /profile/
|   `-- views.py                   # Auth controllers
|-- config/                        # Core Django project package
|   |-- asgi.py                    # ASGI entrypoint
|   |-- settings.py                # Environment-driven settings & logging config
|   |-- urls.py                    # Root URL routing & custom error handlers
|   `-- wsgi.py                    # Production WSGI entrypoint
|-- monitoring/                    # Request logging & health monitoring
|   |-- handlers.py                # Custom HTTP 400, 403, 404, 500 handlers
|   |-- middleware.py              # RequestLoggingMiddleware with sensitive param masking
|   |-- tests.py                   # Health endpoint & error code unit tests
|   |-- urls.py                    # /health/, /test-error/<code>/
|   `-- views.py                   # health_check_view, test_error_view
|-- movies/                        # Movie catalog, streaming dashboard & TMDB integration
|   |-- context_processors.py      # Global context (my_list_count, tmdb_mode)
|   |-- management/commands/
|   |   `-- seed_movies.py         # Seeds 24 curated films into SQL
|   |-- models.py                  # Movie and MyList SQL models
|   |-- tests.py                   # Catalog, search, and list tests
|   |-- tmdb.py                    # TMDB API client with 5s timeout & fallback dataset
|   |-- urls.py                    # /, /discover/, /movie/<id>/, /my-list/
|   `-- views.py                   # home_view, discover_view, detail, my_list
|-- support/                       # FAQ knowledge base, Assistant & Support Tickets
|   |-- assistant.py               # AI Assistant reasoning, FAQ matcher & error explainer
|   |-- forms.py                   # SupportTicketForm
|   |-- management/commands/
|   |   `-- seed_faqs.py           # Seeds 18 comprehensive FAQs into SQL
|   |-- models.py                  # FAQ and SupportTicket SQL models
|   |-- mongo.py                   # PyMongo client, chat_logs & chat_feedback handlers
|   |-- tests.py                   # Assistant, ticket privacy & FAQ tests
|   |-- urls.py                    # /faq/, /support/, /api/chatbot/, /api/chatbot/feedback/
|   `-- views.py                   # FAQ views, ticket desk, chatbot API
|-- static/                        # Static UI assets
|   |-- css/
|   |   |-- style.css              # Design system, tokens, layouts, cards, modals
|   |   `-- chatbot.css            # Floating assistant widget stylesheet
|   |-- images/                    # Fallback posters and backdrops
|   `-- js/
|       |-- main.js                # Navbar, row scroll, list toggle, trailer modal, toasts
|       `-- chatbot.js             # Assistant chat engine, session history, feedback
|-- templates/                     # Modular Django templates
|   |-- accounts/                  # login.html, signup.html, profile.html
|   |-- errors/                    # 400, 401, 403, 404, 429, 460, 500, 503 error pages
|   |-- includes/                  # navbar.html, footer.html, chatbot.html, movie_card.html
|   |-- movies/                    # home.html, discover.html, detail.html, my_list.html
|   |-- support/                   # faq.html, support.html, ticket_detail.html
|   `-- base.html                  # Shared master layout
|-- logs/                          # Rotating log files (streamflix.log)
|-- .env.example                   # Environment configuration template
|-- .gitignore                     # Git exclusion rules for secrets, DBs, venv
|-- manage.py                      # Django management utility
|-- Procfile                       # Gunicorn production worker specification
|-- render.yaml                    # Render cloud deployment blueprint
|-- requirements.txt               # Pinned Python package dependencies
`-- SUBMISSION.md                  # Task sheet submission fields
```

---

## Installation & Local Setup

### Prerequisites
- Python 3.10+ (tested with Python 3.14)
- Git (optional for local deployment, required for GitHub publish)
- Windows PowerShell, macOS Terminal, or Linux Bash

### 1. Virtual Environment Setup
Open PowerShell in the project root:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(On macOS/Linux: `source venv/bin/activate`)*

### 2. Dependency Installation
Install verified requirements:
```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Key environment variables:
```ini
SECRET_KEY=your-secure-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# SQL Database (defaults to SQLite if unset; configure for PostgreSQL in production)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=streamflix_db
# DB_USER=streamflix_user
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# MongoDB Persistence for Chat Logs & Feedback
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=streamflix_db

# TMDB API (Leave blank to use built-in curated 24-movie fallback catalog)
TMDB_API_KEY=
TMDB_TIMEOUT=5.0
```

### 4. Database Migrations & Data Seeding
Run migrations to initialize the SQL schema:
```powershell
python manage.py migrate
```

Seed the SQL database with 18 comprehensive FAQs:
```powershell
python manage.py seed_faqs
```

Seed the SQL database with 24 curated movies:
```powershell
python manage.py seed_movies
```

### 5. Creating an Administrative Account
Create a Django superuser interactively (never hardcode credentials):
```powershell
python manage.py createsuperuser
```
Follow the prompts to enter an administrative username, email, and password.

### 6. Running the Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```
Open your browser at **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

---

## Automated Testing

The project includes an extensive test suite covering user authentication, catalog browsing, movie filtering, My List privacy, FAQ search, assistant logic, support tickets, error handling, health checks, and request logging.

Execute all automated tests:
```powershell
python manage.py test
```

### Test Results
```text
Ran 32 tests in 41.172s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).
```
**Test Coverage Includes:**
- `accounts.tests.AuthenticationTests`: Registration validation, password mismatch rejection, duplicate user protection, username/email login, POST-only logout, login-required profile enforcement.
- `movies.tests.MovieTests`: Home dashboard loading, search query filtering, genre chip filtering, movie details rendering, My List privacy isolation, TMDB timeout fallback activation.
- `support.tests.SupportAndChatbotTests`: SQL FAQ retrieval, token-overlap matching, error code detection (all 8 codes), ticket escalation for unknown questions, ticket creation confirmation, ticket privacy (403 Forbidden for unauthorized users), chatbot feedback validation.
- `monitoring.tests.MonitoringAndErrorHandlingTests`: Machine-readable `/health/` response, real HTTP 404 on invalid paths, custom error templates (400, 401, 403, 404, 429, 460, 500, 503) rendering "Ask the Assistant", `X-Request-ID` middleware verification.

---

## AI Support Assistant & Chatbot Architecture

The **StreamFlix Assistant** is embedded on every page (including all error templates) via `templates/includes/chatbot.html`.

### How It Works:
1. **Conversation Persistence:** A persistent UUID conversation session is generated and saved in `sessionStorage`. Navigating across pages maintains the conversation thread.
2. **Real Endpoint (`/api/chatbot/`):** Receives the message payload with CSRF verification.
3. **Reasoning Pipeline (`support/assistant.py`):**
   - **Step A (Ticket Escalation Confirmation):** Checks if the user confirms opening a support ticket (e.g., saying *"yes"*, *"open ticket"*, or clicking the prompt). If confirmed, creates an SQL `SupportTicket`, generates reference `SF-TICK-XXXXXXXX`, and returns tracking link.
   - **Step B (Error Code Explanations):** Detects if the user asked about any of the 8 status codes (400, 401, 403, 404, 429, 460, 500, 503). Returns a structured explanation (meaning, causes, user steps, support triggers).
   - **Step C (FAQ SQL Knowledge Base Matcher):** Normalizes user queries, strips conversational stop-words, and calculates token/keyword overlap against active SQL FAQs. Returns matched answer with FAQ reference.
   - **Step D (Escalation Proposal):** If confidence is below threshold, politely informs the user and offers to open a Support Ticket.
4. **MongoDB Persistence (`support/mongo.py`):**
   - User and assistant messages are saved to the `chat_logs` collection.
   - User ratings (Helpful / Not Helpful) are saved to the `chat_feedback` collection via `/api/chatbot/feedback/`.
   - **Resilience:** If MongoDB is offline, operations degrade gracefully without crashing any page or widget.

---

## Error Code Documentation

StreamFlix handles 8 status codes with dedicated custom templates in `templates/errors/` and assistant explanations:

| Code | Type | Meaning | Recovery Action | Assistant Trigger |
|---|---|---|---|---|
| **400** | Client Error | Bad Request (malformed parameters) | Clear cache, verify parameters | Supported |
| **401** | Client Error | Unauthorized (authentication required) | Sign in or register | Supported |
| **403** | Client Error | Forbidden (insufficient permission) | Return to personal dashboard | Supported |
| **404** | Client Error | Not Found (page/movie missing) | Return home, search title | Supported |
| **429** | Client Error | Too Many Requests (rate limited) | Wait 30-60 seconds and retry | Supported |
| **460** | Application Event | StreamFlix Diagnostic Error (site convention) | Internal triage & testing | Supported |
| **500** | Server Error | Internal Server Error | Retry in a few moments | Supported |
| **503** | Server Error | Service Unavailable (maintenance) | Check `/health/` status | Supported |

> **Note on Code 460:** Error 460 is an internal StreamFlix application diagnostic convention (not a standardized RFC HTTP code). It is used for system triage and resilience verification.

---

## Third-Party API Integration (TMDB) & Fallback Engine

StreamFlix integrates with [The Movie Database (TMDB)](https://www.themoviedb.org/) API:
- Configured via `TMDB_API_KEY` or `TMDB_READ_ACCESS_TOKEN` in `.env`.
- Uses a strict **5.0-second timeout** (`TMDB_TIMEOUT`).
- **Resilient Fallback Mode:** If no API key is supplied, or if TMDB experiences downtime, network errors, or rate limits, StreamFlix seamlessly serves its built-in catalog of 24 curated titles across all genres with valid poster and backdrop URLs and YouTube trailer links.
- The UI displays an informative badge (`Curated Fallback Catalog` or `Live TMDB API`) in the footer and context.

---

## Request Logging & Health Checks

### Request Logging (`monitoring/middleware.py`)
- Automatically records HTTP method, requested path, response status code, elapsed duration in milliseconds, client IP, and a unique `X-Request-ID`.
- Logs are written to rotating log files: `logs/streamflix.log` (5MB max per file, 5 backups).
- **Data Privacy:** Passwords, session tokens, CSRF tokens, and secret parameters are automatically redacted (`***REDACTED***`).

**Example Log Entries:**
```text
[2026-10-27 16:24:14,781] INFO streamflix: [f7632480] GET /health/ status=200 duration=15.86ms ip=127.0.0.1
[2026-10-27 16:24:15,192] INFO streamflix: [75c9b452] POST /accounts/login/ status=302 duration=465.94ms ip=127.0.0.1
[2026-10-27 16:24:16,818] WARNING streamflix: [e69a32bd] GET /missing-page/ status=404 duration=1.67ms ip=127.0.0.1
```

### Health Check Endpoint (`/health/`)
Machine-readable JSON endpoint reporting operational status:
```json
{
  "status": "healthy",
  "timestamp": "2026-10-27T11:01:25.131544Z",
  "latency_ms": 14.2,
  "checks": {
    "django": "healthy",
    "sql_database": {
      "status": "connected",
      "engine": "sqlite3"
    },
    "mongodb": {
      "status": "connected",
      "role": "persistent_chat_logs_and_feedback",
      "connected": true
    },
    "tmdb_api": {
      "status": "curated_fallback_mode",
      "timeout_seconds": 5.0
    }
  }
}
```

---

## Security Architecture

- **CSRF Protection:** Enabled on all forms and JavaScript AJAX requests.
- **SQL Injection Prevention:** 100% queries executed through Django ORM with parameter binding.
- **XSS Escaping:** Auto-escaping in Django template engine with strict sanitization on markdown bubbles.
- **Password Protection:** Django PBKDF2 password hashing with minimum 8 characters and complexity validators.
- **Authorization Enforcement:** Direct object ownership checks on Support Tickets (unauthorized access triggers HTTP 403 Forbidden).
- **Environment Isolation:** Secrets, API keys, database credentials, and session tokens are strictly loaded via `.env` and excluded from git via `.gitignore`.
- **Production Cookie Hardening:** `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and `SECURE_SSL_REDIRECT` automatically activated when `DEBUG=False`.

---

## Deployment Guide

### Deployment on Render (or Heroku/AWS)

StreamFlix includes a production blueprint (`render.yaml`) and `Procfile`.

1. **Push your code to GitHub:**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit of StreamFlix application"
   git branch -M main
   git remote add origin https://github.com/<your-username>/streamflix.git
   git push -u origin main
   ```
2. **Create Managed Services:**
   - **PostgreSQL:** Create a free PostgreSQL instance on Render or Supabase. Note the connection URI.
   - **MongoDB Atlas:** Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/atlas). Under Database Access, create a database user; under Network Access, allow IP `0.0.0.0/0`. Copy the connection string (`mongodb+srv://...`).
3. **Deploy Web Service on Render:**
   - Connect your GitHub repository.
   - Set Environment to **Python**.
   - Build Command:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_faqs && python manage.py seed_movies
     ```
   - Start Command:
     ```bash
     gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
     ```
4. **Configure Environment Variables on Hosting Provider:**
   - `DEBUG`: `False`
   - `SECRET_KEY`: `(generate secure random string)`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
   - `DB_ENGINE`: `django.db.backends.postgresql`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: `(PostgreSQL details)`
   - `MONGO_URI`: `(MongoDB Atlas URI)`
   - `MONGO_DB_NAME`: `streamflix_prod`
   - `TMDB_API_KEY`: `(Your TMDB v3 API Key)`
   - `SECURE_SSL_REDIRECT`: `True`
   - `SESSION_COOKIE_SECURE`: `True`
   - `CSRF_COOKIE_SECURE`: `True`

---

## Project Submission Details

| Field | Submission Value | Status |
|---|---|---|
| **Individual Task Title** | Development of StreamFlix: A Django-Based Streaming Platform with an FAQ-Driven AI Support Assistant | Verified & Ready |
| **Live Website Link** | *Pending deployment authorization by user* | Deployment Ready (`render.yaml` configured) |
| **GitHub Repository Link** | *Pending repository push by user* | Git Ready (`.gitignore` & clean tree prepared) |

---

## Proposed Future Improvement

### Personalized Privacy-Preserving Collaborative Recommendations
As a next enhancement, StreamFlix can incorporate an on-device or federated recommendation engine:
- Compute implicit watch-time and bookmark affinities locally in session or encrypted user vectors.
- Surface a dedicated **"Recommended For You"** shelf balancing exploration (discovering new genres) and exploitation (refining user favorites).
- Respect user privacy by allowing users to clear recommendation history or opt out at any time.
