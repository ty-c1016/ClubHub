# ClubHub

A centralized campus event management platform built for Northeastern University. ClubHub connects students, club organizers, administrators, and data analysts through a role-based web application for discovering events, managing RSVPs, tracking club engagement, and monitoring system health.

## Features

- **Event Discovery** — Search and filter campus events by date, type, and club
- **RSVP System** — Confirm or decline attendance; waitlist support
- **Club Comparison** — Side-by-side club stats and rankings by engagement
- **Social Invitations** — Send and receive friend invitations to events
- **Coordinator Tools** — Create events, track attendance, manage collaborations
- **Analytics Dashboard** — Search trends, demographic breakdowns, weekly engagement reports
- **System Administration** — Audit logs, system metrics, alert management, server status
- **Role-Based Access Control** — Four distinct user personas with tailored page sets

## Tech Stack

- **Frontend** — Streamlit (Python)
- **Backend** — Flask REST API (`flask-restful`, `flask-login`, `flask-cors`)
- **Database** — MySQL 9
- **Infrastructure** — Docker & Docker Compose
- **ML** — scikit-learn, SHAP (pluggable model infrastructure)
- **Visualization** — Plotly, Altair, Seaborn, Pydeck

## Project Structure

```
app/                        # Streamlit frontend
├── src/
│   ├── Home.py             # Login / role selection
│   ├── pages/              # 25+ role-scoped pages
│   ├── modules/nav.py      # RBAC sidebar navigation
│   └── .streamlit/         # Theme and config
api/                        # Flask REST API
├── backend/
│   ├── rest_entry.py       # App factory
│   ├── backend_app.py      # Entry point (port 4000)
│   ├── clubs/              # Club routes
│   ├── students/           # Student routes
│   ├── events/             # Event routes
│   ├── admin/              # Admin routes
│   ├── analytics/          # Analytics routes
│   └── invitations/        # Invitation routes
database-files/
└── clubhub_db.sql          # Schema + mock data (30+ tables)
ml-src/                     # ML model source and notebooks
datasets/                   # Data storage
docker-compose.yaml
sandbox.yaml                # Personal testing config
```

## User Roles

| Role | Persona | Key Pages |
|---|---|---|
| Student | Ruth Doe | Event discovery, club comparison, schedule, friend invites, rankings |
| Event Coordinator | Sofia Martinez | Create events, RSVP management, analytics, collaborations |
| System Administrator | David Kim | System metrics, audit logs, alert management, server status |
| Data Analyst | Marcus Rodriguez | Engagement overview, search insights, demographics, club analytics, weekly reports |

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)

### 1. Create a Python environment

```bash
conda create -n db-proj python=3.11
conda activate db-proj
```

### 2. Configure environment variables

```bash
cp api/.env.template api/.env
```

Edit `api/.env` and set a strong `MYSQL_ROOT_PASSWORD`. The other defaults work out of the box.

### 3. Start all services

```bash
docker compose up -d
```

| Service | URL |
|---|---|
| Streamlit app | http://localhost:8501 |
| Flask API | http://localhost:4000 |
| MySQL | localhost:3200 |

### 4. Stop services

```bash
docker compose down          # stop and remove containers
docker compose down -v       # also remove the database volume
```

### Personal sandbox (optional)

Use `sandbox.yaml` to run your own isolated copy without affecting the team repo:

```bash
docker compose -f sandbox.yaml up -d
docker compose -f sandbox.yaml down
```

## Database

The MySQL schema is initialized automatically from `database-files/clubhub_db.sql` when the `db` container is first created. It includes 30+ tables and demo data: 15 students, 10 clubs, and 12 events.

To reset the database after schema changes:

```bash
docker compose down db -v && docker compose up db -d
```

## Development Notes

- Flask API and Streamlit changes **hot-reload** on save.
- In the browser, click **Always Rerun** in the Streamlit toolbar to pick up frontend changes automatically.
- SQL init files execute in **alphabetical order** — name them accordingly.
- Check the MySQL container logs in Docker Desktop if the database fails to start.
