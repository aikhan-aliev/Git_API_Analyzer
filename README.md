# GitHub Repo Risk Analyzer API

A production-ready REST API that analyzes GitHub repositories for risk factors including code complexity, security vulnerabilities, contributor health, and maintenance activity.

## Features

- 🔐 **JWT Authentication** — Register, login, and secure endpoints
- 📦 **Repository Registration** — Register any public GitHub repository by URL or `owner/name`
- 🔬 **Automated Analysis** — Async Celery worker runs 4 analyzers in sequence:
  - **Structure Analyzer** — Checks for README, LICENSE, CI config, tests
  - **Activity Analyzer** — Commit frequency, days since last push, open issues
  - **Contributor Analyzer** — Bus factor, contributor count, commit concentration
  - **Python Analyzer** — Radon (cyclomatic complexity) + Bandit (security) via shallow clone
- 📊 **Risk Reports** — Scored snapshots with weighted overall risk level (low/moderate/elevated/high)
- 🔔 **Webhooks** — GitHub push event webhook triggers automatic re-analysis with HMAC verification
- 🐳 **Docker Ready** — Full `docker-compose.yml` with PostgreSQL, Redis, API, and worker services

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/yourorg/git-api-analyzer
cd git-api-analyzer
cp .env.example .env
# Edit .env with your GITHUB_TOKEN and JWT_SECRET_KEY
```

### 2. Start Services

```bash
docker compose up --build
```

Or locally with a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -e ".[dev]"

# Start PostgreSQL and Redis (requires Docker)
docker compose up db redis -d

# Apply migrations
alembic upgrade head

# Start the API
uvicorn app.main:app --reload

# Start the Celery worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info
```

### 3. Explore the API

Visit **[http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)** or **[http://localhost:8000/docs](http://localhost:8000/docs)** for the interactive Swagger UI.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Obtain JWT access token |
| `GET`  | `/api/v1/auth/me` | Get current user |
| `POST` | `/api/v1/repositories` | Register a GitHub repository |
| `GET`  | `/api/v1/repositories` | List user's repositories |
| `GET`  | `/api/v1/repositories/{id}` | Get repository details |
| `POST` | `/api/v1/analysis/repositories/{id}/analyze` | Trigger analysis |
| `GET`  | `/api/v1/analysis/jobs/{job_id}` | Get job status |
| `GET`  | `/api/v1/reports/repositories/{id}/report/latest` | Latest analysis report |
| `GET`  | `/api/v1/reports/repositories/{id}/reports` | All reports |
| `GET`  | `/api/v1/reports/repositories/{id}/findings` | Latest findings |
| `POST` | `/api/v1/webhooks/github` | GitHub push webhook receiver |
| `GET`  | `/health` | Health check |
| `GET`  | `/ready` | Readiness check |

## Architecture

```
┌──────────────┐    ┌─────────────┐    ┌──────────────────┐
│   FastAPI    │───▶│  PostgreSQL  │    │   Celery Worker  │
│  (REST API)  │    │  (via ORM)  │    │                  │
└──────┬───────┘    └─────────────┘    │ ┌──────────────┐ │
       │                               │ │  Structure   │ │
       │  Queue job                    │ │  Analyzer    │ │
       ▼                               │ ├──────────────┤ │
┌──────────────┐                       │ │  Activity    │ │
│    Redis     │──────────────────────▶│ │  Analyzer    │ │
│   (broker)   │                       │ ├──────────────┤ │
└──────────────┘                       │ │ Contributors │ │
                                       │ │  Analyzer    │ │
                                       │ ├──────────────┤ │
                                       │ │   Python     │ │
                                       │ │  Analyzer    │ │
                                       │ └──────────────┘ │
                                       └──────────────────┘
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | Required |
| `GITHUB_TOKEN` | GitHub Personal Access Token | - |
| `JWT_SECRET_KEY` | JWT signing secret | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `WEBHOOK_SECRET` | GitHub webhook secret | - |
| `ENVIRONMENT` | `development`/`production` | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Development

### Running Tests

```bash
pytest -v
```

### Linting

```bash
ruff check .
black --check .
```

### Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Tech Stack

- **Python 3.11** + **FastAPI** — High-performance async REST API
- **SQLAlchemy 2** + **Alembic** — ORM with migrations
- **PostgreSQL** — Primary database
- **Redis** + **Celery** — Async task queue
- **pwdlib** — Bcrypt password hashing
- **python-jose** — JWT tokens
- **httpx** — GitHub API client
- **radon** — Python cyclomatic complexity
- **bandit** — Python security scanner
- **gitpython** / `git` CLI — Repository cloning
