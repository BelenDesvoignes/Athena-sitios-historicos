# Athena — Argentine Historical Heritage Portal

A full-stack web system for managing and exploring Argentina's historical heritage sites. The platform features a public-facing portal with geospatial search and Google OAuth login, backed by a role-based admin panel for content management.

**Live:** [Portal](https://athena-sitios-historicos.vercel.app) · [Admin Panel](https://athena-admin-production-b23c.up.railway.app)

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Vue.js 3, Vite, Pinia, Vue Router, Leaflet / vue-leaflet |
| **Backend** | Python 3.12, Flask, SQLAlchemy, Flask-JWT-Extended, Flask-CORS |
| **Database** | PostgreSQL 16 + PostGIS |
| **Auth** | Google OAuth 2.0 (public users), session-based (admin) |
| **Infrastructure** | Railway (backend API), Vercel (frontend) |

---

## Features

### Public Portal
- Interactive Leaflet map with geospatial filtering via PostGIS
- Browse and search sites by province and category tags
- Google OAuth login via redirect flow
- Leave reviews and star ratings
- Save and manage favourite sites

### Admin Panel
- Role-based access control: System Admin → Admin → Editor → Public User
- Full CRUD for historical sites, including image upload to MinIO / S3
- Review moderation queue
- User management with granular permission assignment
- Feature flags: maintenance mode (portal + admin), review gating
- CSV data export

---

## Architecture

```
Athena/
├── admin/          # Flask app — admin panel (Jinja2 + session auth)
│   └── src/        #           + REST API (/api/*) consumed by portal (JWT auth)
└── portal/         # Vue.js 3 SPA deployed on Vercel
```

The backend serves two audiences from a single Flask process:

- **Admin panel** (`/`, `/sitios`, `/admin`, …) — server-rendered Jinja2, session cookie auth
- **REST API** (`/api/*`) — JSON endpoints consumed by the Vue portal, JWT auth

Feature flags stored in the database control portal and admin maintenance modes and whether reviews are accepting submissions.

---

## Local Setup

### Prerequisites

- PostgreSQL 16 with PostGIS — `localhost:5432`, database `grupo19`, user `postgres`, password `admin`
- MinIO (optional, for image uploads) — `localhost:9000`, access key `grupo19admin`, secret `grupo19secret`, bucket `grupo19`
- A Google OAuth 2.0 Client ID — add `http://localhost:5173` as an Authorized JavaScript Origin and Authorized Redirect URI in [Google Cloud Console](https://console.cloud.google.com)

### Backend

```bash
cd Athena/admin
poetry install
poetry run flask --app main.py run
# → http://localhost:5000
# Database and seed data are created automatically on first start.
```

### Frontend

```bash
cd Athena/portal
npm install
npm run dev
# → http://localhost:5173
```

### Default Credentials

| Role | Email | Password |
|---|---|---|
| System Admin | sysadmin@example.com | sysadmin123 |
| Admin | admin@example.com | admin123 |
| Editor | usuarioEditor@gmail.com | editor123 |
| Public User | register via portal (Google) | — |

---

## Environment Variables

| Variable | Where | Value (production) |
|---|---|---|
| `VITE_API_BASE_URL` | Vercel env vars | `https://athena-admin-production-b23c.up.railway.app/api` |
| `VITE_API_LOGIN_URL` | Vercel env vars | `https://athena-admin-production-b23c.up.railway.app/api/public_users/login` |
| `FLASK_ENV` | Railway env vars | `production` |
| `DATABASE_URL` | Railway env vars | PostgreSQL connection string (set by Railway) |

---

## Project Structure

```
admin/src/
├── core/               # Domain layer (no Flask deps)
│   ├── models/         # SQLAlchemy ORM models
│   ├── seeds.py        # Startup seed data
│   ├── flags.py        # Feature flag helper
│   └── permissions_service.py
└── web/
    ├── __init__.py     # App factory (create_app)
    ├── config.py       # Dev / Prod / Testing configs
    ├── controllers/    # Jinja2 blueprint routes
    ├── api/            # REST API blueprints
    └── handlers/       # Before-request hooks, decorators

portal/src/
├── stores/auth.js      # Pinia auth store (Google OAuth + JWT)
├── router/index.js     # Vue Router with maintenance-mode guard
├── services/           # API calls and flag polling
├── views/              # One SFC per route
└── components/SiteMap.vue   # Leaflet map component
```
