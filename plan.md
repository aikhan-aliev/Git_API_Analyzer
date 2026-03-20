You are a senior backend engineer and system designer. Your task is to fully implement a production-style project called GitHub Repo Risk Analyzer API.

You must act like an experienced engineer working on a real portfolio-grade backend product, not like a tutorial generator. Build the project end-to-end with clean architecture, strong engineering decisions, debugging discipline, and production-style quality.

PROJECT NAME

GitHub Repo Risk Analyzer API

PROJECT GOAL

Build a Python-based REST API platform that analyzes public GitHub repositories and produces an explainable engineering risk report based on repository metadata, commit activity, contributor concentration, repository structure, Python code complexity, and Python security findings. The system must support asynchronous analysis jobs, historical snapshots, Dockerized local execution, automated tests, and CI/CD through GitHub Actions. The project should be strong enough to showcase on a CV, GitHub profile, and to recruiters or engineers at backend-heavy companies.

IMPORTANT EXECUTION RULES

Do not ask me for clarification unless absolutely necessary. Make strong, reasonable engineering choices and proceed.

Do not leave placeholders like TODO, implement later, or omitted for brevity. Fully implement things.

Do not generate pseudocode unless it is part of architecture documentation. Generate real working code.

Do not overcomplicate the first version with unnecessary abstractions, but do keep the architecture clean and scalable.

Do not use a JavaScript frontend in the first implementation unless it is needed minimally. API-first is the priority.

Do not stop after scaffolding. Fully implement the API, models, database logic, services, workers, analyzers, tests, Docker, CI, and documentation.

Do not implement dangerous execution of repository code. The project must remain static-analysis-oriented. Never execute arbitrary code from cloned repositories.

Do not use in-memory storage for core features. Use PostgreSQL and Redis properly.

Do not implement only a partial demo. Implement a real MVP that runs end-to-end.

GENERAL QUALITY BAR

The project must look like it was built by a strong backend engineer.

The code must be:
clean
modular
typed where appropriate
consistent
well-structured
readable
testable
debuggable
production-oriented

The repository must include:
clear structure
strong README
environment configuration
Docker support
database migrations
unit and integration tests
GitHub Actions CI
API docs through FastAPI OpenAPI
error handling
logging

TECH STACK REQUIREMENTS

Use the following stack unless there is a strong engineering reason to slightly adjust details:

Python 3.12
FastAPI
SQLAlchemy 2.x
Alembic
PostgreSQL
Redis
Celery
Pydantic
httpx
GitPython or subprocess-based git clone
Radon
Bandit
pytest
pytest-asyncio
httpx test client where suitable
Docker
Docker Compose
Ruff
Black
mypy
pre-commit
GitHub Actions

If helpful, you may also use:
passlib or pwdlib for password hashing
python-jose or PyJWT for JWT auth
tenacity for retry logic
structlog or standard logging
pydantic-settings for configuration
asyncpg or psycopg depending on compatibility with chosen SQLAlchemy setup

PRODUCT REQUIREMENTS

The platform must support the following flows.

Flow 1: authentication
A user can register and log in.
The API returns JWT access tokens.
Protected routes require authentication.

Flow 2: repository registration
A user submits a public GitHub repository URL or owner/repo string.
The system validates and normalizes the repository identifier.
The system fetches repository metadata from GitHub API.
The repository is stored in the database.

Flow 3: analysis job creation
A user creates an analysis job for a repository.
The request returns immediately with queued status.
A Celery worker processes the job asynchronously.

Flow 4: analysis processing
The worker fetches GitHub metadata and repository activity data.
The worker clones the repository shallowly into a temporary workspace.
The worker runs analyzers:
repository structure analyzer
commit activity analyzer
contributor analyzer
Python complexity analyzer
Python security analyzer
The worker computes normalized sub-scores and an overall score.
The worker stores all metrics, findings, and a snapshot in PostgreSQL.
The worker marks the job completed or failed.

Flow 5: report retrieval
The user can fetch:
repository details
analysis job status
latest report
snapshot history
detailed findings

Flow 6: optional webhook foundation
Implement GitHub webhook ingestion foundation as part of MVP if feasible without harming stability.
At minimum include endpoint, signature verification helper, payload storage model, and job creation for push events. If full automatic webhook creation is too much for MVP, the receiver foundation is enough.

RISK DIMENSIONS TO IMPLEMENT

Implement these five explainable dimensions.

Maintainability score
Based on code complexity, maintainability index, repository structure quality, presence of README, tests, license, CI config, and overly large Python files if detected.

Security score
Based on Bandit findings for Python repositories.
Use severity and confidence weighting.
If repository contains no Python files, return a neutral or not_applicable-aware result and document the scoring rule clearly.

Activity score
Based on commit activity over the last 30 and 90 days, recency of latest commit, and inactivity penalties.

Collaboration score
Based on contributor concentration and bus factor heuristics.
At minimum calculate recent contributor distribution and top contributor share.

Sustainability score
Based on active contributors, repository archival status if available, age versus activity, and issue/activity heuristics where feasible.

SCORING REQUIREMENTS

The scoring system must be explicit and documented.
Use a 0 to 100 scale where higher means healthier and lower means riskier.
Implement weighted overall score as:
0.30 maintainability
0.25 security
0.20 activity
0.15 collaboration
0.10 sustainability

Map overall score to risk levels:
85 to 100 low
70 to 84 moderate
50 to 69 elevated
below 50 high

The scoring logic must be centralized in a dedicated service module.
The scoring logic must be deterministic and explainable.
Document all thresholds in code comments and README.

MVP ENDPOINTS TO IMPLEMENT

POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me

POST /api/v1/repositories
GET /api/v1/repositories/{repository_id}
GET /api/v1/repositories
POST /api/v1/repositories/{repository_id}/analyze
GET /api/v1/repositories/{repository_id}/snapshots
GET /api/v1/repositories/{repository_id}/latest-report

GET /api/v1/analyses/{analysis_job_id}
GET /api/v1/analyses/{analysis_job_id}/findings

POST /api/v1/webhooks/github

GET /health
GET /ready

If metrics endpoint is easy and clean, include GET /metrics or internal instrumentation hooks, but do not let that delay core functionality.

DATABASE ENTITIES TO IMPLEMENT

Implement proper SQLAlchemy models and Alembic migrations for these entities.

User
id
email
hashed_password
is_active
created_at
updated_at

Repository
id
github_owner
github_name
full_name
html_url
clone_url
default_branch
description
primary_language
stars
forks
open_issues
is_private
is_archived
last_pushed_at
created_at
updated_at

RepositoryRegistration or ownership link
id
user_id
repository_id
created_at

AnalysisJob
id
repository_id
requested_by_user_id
status
trigger_source
branch
commit_sha
error_message
created_at
started_at
finished_at

AnalysisSnapshot
id
analysis_job_id
overall_score
overall_risk_level
maintainability_score
security_score
activity_score
collaboration_score
sustainability_score
generated_at

Finding
id
snapshot_id
category
severity
title
description
recommendation
metric_key
metric_value_text
metric_value_numeric
created_at

Metric
id
snapshot_id
key
value_numeric
value_text
unit
created_at

WebhookEvent
id
repository_id nullable if unresolved
event_type
delivery_id
payload_json
status
received_at
processed_at

Use UUIDs for primary keys if practical. If using integers simplifies too much of the stack, UUID is still preferred because it looks more production-ready. Be consistent.

PROJECT STRUCTURE REQUIREMENTS

Create a clean structure similar to this and adapt as needed:

repo-risk-analyzer/
app/
api/
v1/
endpoints/
auth.py
repositories.py
analyses.py
webhooks.py
health.py
dependencies.py
core/
config.py
security.py
logging.py
constants.py
db/
base.py
session.py
models/
user.py
repository.py
analysis_job.py
snapshot.py
finding.py
metric.py
webhook_event.py
schemas/
auth.py
repository.py
analysis.py
finding.py
webhook.py
common.py
services/
auth_service.py
github_service.py
repository_service.py
analysis_service.py
scoring_service.py
webhook_service.py
analyzers/
base.py
github_metadata.py
commit_activity.py
contributors.py
repo_structure.py
python_complexity.py
python_security.py
workers/
celery_app.py
tasks.py
utils/
git_utils.py
time_utils.py
parsers.py
tempdirs.py
exceptions.py
main.py
tests/
conftest.py
unit/
integration/
fixtures/
alembic/
docker/
.github/
workflows/
ci.yml
.env.example
Dockerfile
docker-compose.yml
pyproject.toml
README.md
pre-commit-config.yaml

If any file names need to change for implementation quality, that is acceptable, but preserve this level of organization.

IMPLEMENTATION DETAILS

Backend framework
Use FastAPI.
Use dependency injection for DB sessions and authenticated users.
Expose OpenAPI docs.
Use response models for all major endpoints.

Configuration
Use environment-driven configuration with a settings class.
Support local dev, test, and docker usage.
Include .env.example with all required variables.

Required env variables:
DATABASE_URL
REDIS_URL
GITHUB_TOKEN
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
WEBHOOK_SECRET
ENVIRONMENT
LOG_LEVEL

Authentication
Implement register and login.
Hash passwords securely.
Issue JWT tokens.
Protect repository and analysis endpoints.
Return standard auth responses.

GitHub integration
Implement a dedicated GitHub service layer.
Use GitHub REST API with token-based auth.
Support:
fetch repository metadata
fetch contributors
fetch commits in recent ranges
optionally detect rate limit errors and retry gracefully
Parse both full URL and owner/repo input formats.

Repository cloning
Clone public repositories shallowly into a temp directory.
Prefer a safe clone strategy with timeout handling.
Do not checkout arbitrary refs from untrusted input unless validated.
Clean up temp directories after analysis.

Analyzer implementation
Implement analyzers as separate modules returning structured outputs.

Repository structure analyzer should detect:
README presence
LICENSE presence
tests folder presence
docs folder presence
CI config presence such as .github/workflows
requirements.txt or pyproject.toml presence
basic file count or Python file count if useful

Commit activity analyzer should calculate:
commits in last 30 days
commits in last 90 days
latest commit timestamp
basic activity category

Contributor analyzer should calculate:
number of contributors
top contributor percentage
top three contributor share if feasible
bus factor heuristic

Python complexity analyzer should:
run only when Python files exist
use Radon for cyclomatic complexity and maintainability index
summarize average complexity
summarize max complexity
count high-complexity functions
store metrics and findings

Python security analyzer should:
run only when Python files exist
use Bandit programmatically if practical, otherwise safe subprocess execution
count findings by severity
count findings by confidence
store detailed findings in normalized form

Scoring logic
Implement a scoring service that consumes analyzer outputs and returns:
sub-scores
overall score
risk level
human-readable finding generation inputs if needed

Keep threshold logic readable and centralized.
Document penalty rules in code.

Analysis pipeline
When analysis starts:
mark job started
run all analyzers
handle partial analyzer failures without crashing whole job when possible
store warnings if some analyzers fail
store snapshot and metrics
mark job completed

When fatal failure happens:
store error message
mark job failed

Use Celery tasks with proper serialization-safe job inputs, preferably passing job id and re-loading state from DB.

API behavior
POST analyze should queue a job and return:
analysis_job_id
status queued

GET analysis should return:
job metadata
status
error if failed
snapshot summary if complete

GET latest report should return:
repository metadata
latest snapshot
high-level findings
optionally compact metrics summary

GET findings should return paginated or non-paginated list if simple enough.

Error handling
Implement consistent structured errors.
Use proper HTTP status codes.
Validate repository input strongly.
Handle:
invalid GitHub URL
repository not found
rate limit issues
duplicate repository registration
unauthorized access
analysis job not found
worker failures

Logging
Implement structured logging or at minimum clean standard logging.
Log:
auth events at safe level
repository registration
analysis job lifecycle
GitHub API failures
analyzer failures
webhook receipt
worker completion or failure

Do not log secrets or raw tokens.

Testing
Implement real tests, not superficial tests.

Unit tests should cover:
URL parsing
JWT helpers
password hashing
scoring logic
signature verification
bus factor and contributor calculations
risk level mapping

Integration tests should cover:
register and login flow
repository registration flow with mocked GitHub API
analysis job creation
fetch analysis status
fetch latest report
webhook endpoint basic acceptance and signature verification

Analyzer tests should use fixture repositories or fixture directories with sample files to validate structure, complexity, and security analyzers.

Use pytest.
Set up a test configuration.
Mock external GitHub API calls.
Avoid flakiness.

Migrations
Use Alembic properly.
Generate and refine migrations.
Ensure initial migration creates all core tables.
Do not leave schema drift unresolved.

Docker
Provide a Dockerfile for app.
Provide Docker Compose with services:
api
worker
postgres
redis

Ensure local startup with one command is possible.
Use sensible container commands.

CI/CD
Implement GitHub Actions CI for this repository.
On push and pull_request, run:
lint
format check
type check
tests

If Docker build is stable, add build verification.
Do not require deployment in CI unless it is easy and robust.

README
Write a strong README that includes:
project overview
why this project matters
architecture summary
features
stack
how scoring works
local setup
docker setup
env variables
migration commands
running tests
API overview
example requests and responses
future improvements

Developer experience
Include:
pyproject.toml
ruff config
black config if needed
mypy config
pre-commit hooks
Makefile optional if it improves usability

Webhook foundation
Implement POST /api/v1/webhooks/github
Verify GitHub signature using WEBHOOK_SECRET
Store raw payload
Handle push event by creating a new analysis job for the repository if known
If repository not known, still store event and return accepted if appropriate
Keep webhook code clean and safe

IMPLEMENTATION ORDER

Follow this exact development sequence.

Step 1
Initialize project structure, pyproject, FastAPI app, config, logging, health endpoints.

Step 2
Implement database setup, SQLAlchemy base, sessions, models, Alembic setup, initial migration.

Step 3
Implement auth models, schemas, service, JWT, password hashing, auth endpoints, auth tests.

Step 4
Implement repository parsing and GitHub metadata service.
Implement repository registration flow and tests.

Step 5
Implement Celery integration, Redis config, worker startup, analysis job model changes if needed.
Implement queueing flow and job status endpoint.

Step 6
Implement repository structure analyzer and integration into worker flow.

Step 7
Implement commit activity analyzer and contributor analyzer using GitHub API data.

Step 8
Implement Python repository detection, clone utility, Radon analyzer, Bandit analyzer.

Step 9
Implement scoring service and snapshot persistence.

Step 10
Implement latest report endpoint, findings endpoint, snapshots endpoint.

Step 11
Implement webhook endpoint and signature verification.

Step 12
Implement Docker, Docker Compose, CI, pre-commit, linting, type checking.

Step 13
Write README and finalize project polish.

At each step, make the project runnable before moving to the next step.

DEBUGGING AND VALIDATION PROCESS

This is critical. You must self-debug continuously.

After each major implementation phase:
run formatting
run linting
run type checks
run tests
fix all failures before moving on

Use this debugging discipline:

start small and verify imports

verify app boots without syntax errors

verify database migrations apply cleanly

verify auth flow manually and with tests

verify repository registration with mocked GitHub responses

verify Redis and Celery connectivity

verify job queueing and worker consumption

verify analyzers on known fixture repos

verify snapshot persistence and retrieval

verify Dockerized startup

verify CI config commands match local commands

When a bug occurs:
read full traceback carefully
identify whether it is import issue, typing issue, DB issue, serialization issue, external API issue, subprocess issue, or test configuration issue
fix root cause, not symptoms
rerun the smallest relevant test first
then rerun the broader suite

Common issues to proactively guard against:
circular imports between models and services
SQLAlchemy session lifecycle bugs
Celery passing non-serializable objects
using async DB patterns inconsistently with sync worker code
Bandit or Radon invocation path issues
Git clone cleanup failures
timezone-naive versus timezone-aware datetime problems
GitHub API pagination or auth errors
Pydantic model mismatches
Docker service hostname mismatches
Alembic migration import problems

SELF-CHECK REQUIREMENTS

Before finalizing, confirm that:
the API starts successfully
the worker starts successfully
migrations run successfully
register and login work
repository registration works for a public GitHub repo
analysis job can be queued
worker processes analysis
snapshot is created
latest report endpoint returns data
tests pass
Docker Compose works
CI workflow is valid

IMPORTANT IMPLEMENTATION CHOICES

Prefer practical working choices over theoretical perfection.
Use sync SQLAlchemy sessions if that simplifies reliable Celery worker interaction, unless async is already cleanly handled.
Keep FastAPI endpoints clean and straightforward.
Use service layer for business logic.
Use analyzer modules for domain logic.
Use schemas for request and response validation.
Use clear enums or constants for job status, risk levels, severity levels if helpful.

RESPONSE AND REPORT DESIGN

The API responses should look professional and stable.

Example latest report shape:
repository object
snapshot object with overall and sub-scores
key_findings array
metrics_summary object if useful

Findings must include:
category
severity
title
description
recommendation

METRIC NORMALIZATION GUIDELINES

Implement reasonable initial thresholds such as:
commit inactivity heavily penalized after 90 days without commits
top contributor share above 75 percent penalizes collaboration
missing README and missing tests mildly penalize maintainability
average complexity above moderate threshold penalizes maintainability
Bandit high severity findings significantly penalize security
few contributors plus long inactivity penalizes sustainability

Do not use random values.
Do not make scoring arbitrary without explanation.
Document all formulas and thresholds.

TEST DATA STRATEGY

Create fixture directories or minimal sample repos for analyzer tests.
Examples:
a Python fixture repo with README, tests, pyproject, some functions of varying complexity
a Python fixture repo with Bandit-detectable unsafe code samples
a sparse repo fixture missing documentation and tests

Mock GitHub API responses for:
repository metadata
contributors
recent commits

DOCUMENTATION EXPECTATIONS

The README must be convincing and portfolio-ready.
Explain not only how to run the project, but why its architecture makes sense.
Include example API usage.
Include a section describing risk dimensions and scoring.
Include future roadmap ideas such as:
trend analysis
GitHub App auth
dependency manifest analysis
organization-wide dashboards
LLM-generated executive summaries

OUTPUT EXPECTATION

Generate the complete project files and code.
Do not only describe what to do.
Actually implement it.
When there are multiple files, create them all with proper content.
Keep the implementation coherent across files.

FINAL QUALITY STANDARD

This project should be something a strong CS student can show publicly and say:
I built a production-style FastAPI platform for repository engineering risk analysis with async job processing, GitHub integration, static analysis, explainable scoring, Dockerized deployment, and CI/CD automation.

Now begin implementing the entire project step by step, creating all files, code, configuration, tests, migrations, and documentation needed for a working MVP.

If the context window becomes large, prioritize completing a coherent runnable MVP over adding optional extra features. The MVP must be functional, tested, and polished.