# Strava Activities

Strava Activities is a Python-based project that implements an ETL/data pipeline around Strava athlete and activity data, together with dashboards (AI/BI) and CI/CD deployment pipelines. The repository contains code and configuration for ingesting Strava data, cleansing and transforming it (including building dimensions such as a calendar dimension), and deploying dashboards and pipelines to production.

This README explains the repository's purpose, the main components, an architecture overview (with diagrams), and the tools and technologies used.

---

## Table of contents

- [Project overview](#project-overview)
- [Repository components](#repository-components)
- [Architecture & diagrams](#architecture--diagrams)
- [Tools & technologies](#tools--technologies)
- [Getting started (dev)](#getting-started-dev)
- [Production deployment & CI/CD notes](#production-deployment--cicd-notes)
- [Contributing](#contributing)
- [License](#license)

---

## Project overview

This project collects and processes Strava athlete and activity data, performs cleansing and transformation tasks, builds useful dimensions (e.g., calendar), and enables downstream analytics and dashboards (AI/BI). The codebase includes packaging artifacts (wheel), job configurations, and deployment configuration for production pipelines and dashboards.

High-level responsibilities:
- Ingest athlete/profile and activity records from the Strava API
- Run data cleansing and transformation tasks
- Build model/dimension tables (e.g., calendar dimension)
- Package library/artifacts (wheel) for pipeline tasks
- Deploy ETL jobs and dashboards via CI/CD workflows

---

## Repository components

Here are the main components and where to look in the repository:

- strava_activities/
  - The primary Python package containing ingestion, cleansing, and transformation code for Strava data.
  - Contains tasks that appear to include a `cleanse` activity task and potentially profile-related jobs.

- .github/
  - GitHub Actions workflows and job configuration used for CI/CD (deployments, packaging, tests).
  - Presence of workflow/job config suggested by commits referencing production deployment and job configs.

- Packaging artifacts and pipelines
  - Commits mention wheel files and updated wheel settings — the repository builds Python wheels for use in scheduled jobs or deployment.

- Deployment & job configuration
  - Job configs and pipeline definitions (referenced in commits) orchestrate the order of tasks, e.g., profile job followed by activity job.

Other files you may find useful:
- README.md (this file)
- (Possible) configuration files for environments, secrets templates, or pipelines (check the repository for `config`, `jobs`, or `deploy` directories).

---

## Architecture & diagrams

Below is a conceptual architecture showing how the pipeline components interact. Use this as a guide when exploring the code or adding new features.

Mermaid flowchart (renderable in many Markdown viewers /GitHub):

```mermaid
flowchart LR
  A[Strava API] --> B[Ingest Service<br/>(strava_activities package)]
  B --> C[Cleanse & Transform]
  C --> D[Data Warehouse / Database]
  D --> E[AI/BI Dashboards / Reports]
  B --> F[Python Wheel Artifact]
  subgraph CI/CD
    G[GitHub Actions Workflows] --> F
    G --> H[Prod Deployment (jobs/dashboards)]
  end
  C --> I[Calendar Dimension Build]
  B --> J[Profile Pipeline]
  J --> C
```

Simplified ASCII architecture:

Strava API
   |
   v
Ingest (strava_activities package)
   |
   v
Cleanse -> Transform -> Build Dimensions (calendar, profiles, etc.)
   |
   v
Data Warehouse / DB -> Dashboards (AI/BI)
   ^
   |
CI/CD (GitHub Actions) deploys pipelines & dashboard artifacts (wheels, configs)

Sequence of common pipeline tasks (as inferred from commits):
1. Profile job runs (ingest athlete/profile)
2. Activities job runs after profile job (ingest & cleanse activities)
3. Cleanse tasks transform raw data into canonical tables
4. Calendar dimension build runs to support time-based analytics
5. Dashboards are refreshed/deployed from transformed data

---

## Tools & technologies

The repository explicitly and implicitly uses the following technologies:

- Python
  - The repository is primarily Python; code is organized under the `strava_activities` package.
  - Packaging uses wheel artifacts (commits referencing updated wheel settings).

- Strava API
  - Data ingestion targets Strava athlete and activity endpoints (OAuth tokens / API credentials required).

- CI/CD: GitHub Actions
  - The `.github` directory and commit messages indicate GitHub Actions workflows are in use for building, testing, and deploying pipelines and dashboards.

- ETL/Orchestration (conceptual)
  - The project is structured as a data pipeline (ingest -> cleanse -> transform -> store -> visualize). The exact orchestrator (Airflow, Prefect, etc.) is not required by the repository metadata shown, but job/config files and workflow steps exist. Inspect pipeline/job config files in the repo to confirm the orchestrator.

- Data storage / Analytics
  - Transformed data is intended for a data warehouse or analytical store (not explicit which one). Dashboards and AI/BI artifacts are produced from transformed data.

- Packaging
  - Python wheel distribution is used to package library code for deployment to jobs.

Notes:
- Some details (exact orchestration tool, database, or dashboarding stack) are not explicit in repository metadata. Check pipeline configs and the `strava_activities` package for configuration files or environment variable names (e.g., database connection strings, orchestrator DAGs) to determine concrete implementations.

---

## Getting started (developer)

Quick steps to run or develop locally. Adjust environment variables and steps according to your infrastructure and secrets.

1. Clone the repo
   - git clone https://github.com/rajnil-guha01/strava_activities.git
   - cd strava_activities

2. Create a virtual environment and install dependencies
   - python -m venv .venv
   - source .venv/bin/activate  (Windows: .venv\Scripts\activate)
   - pip install -U pip setuptools wheel
   - pip install -e .

3. Environment variables (example; adjust names to match code)
   - STRAVA_CLIENT_ID=your_client_id
   - STRAVA_CLIENT_SECRET=your_client_secret
   - STRAVA_ACCESS_TOKEN=your_token
   - DATABASE_URL=postgresql://user:pass@host:5432/dbname
   - (Other env vars as found in configuration files)

4. Run ingestion / tasks
   - Inspect `strava_activities` package for available CLI or entrypoints.
   - Example (replace with actual command when present):
     - python -m strava_activities.ingest --since YYYY-MM-DD
     - python -m strava_activities.cleanse

5. Tests
   - If tests are included, run:
     - pytest

---

## Production deployment & CI/CD notes

- The repository includes workflow and job config changes in commit history for "prod deployment", "AI/BI dashboards deployment", and "job configs".
- Wheels are built and used by jobs — ensure CI workflows have access to secrets and artifact storage.
- Production workflows likely rely on GitHub Actions; review `.github/workflows` to see job definitions and required secrets.
- Common deployment steps:
  1. Build wheel/artifact
  2. Run tests and lint
  3. Publish artifact (internal registry or artifact store)
  4. Trigger deployment job(s) that run scheduled pipelines and refresh dashboards

---

## Contributing

- Open an issue describing the feature or bug.
- Create a branch and open a PR with a clear description and tests where applicable.
- Follow the repo's code style and include appropriate unit and integration tests.

---

## Where to look next in the repo

- strava_activities/ — core code (ingest/cleanse/transform)
- .github/ — GitHub Actions workflows and job configuration
- Any `jobs`, `deploy`, `pipelines`, or `config` folders for orchestrator and deployment definitions
- README (this file) — update with concrete commands and secrets once you confirm exact configuration names.

---

## License

If you plan to publish this repository, add a LICENSE file. If this repository already has a license file, ensure the README mentions the license. (No license file was detected by the metadata I reviewed.)

---

If you'd like, I can:
- Commit this README.md to the repository for you (I can prepare a commit message), or
- Update the README with more exact run commands after you point me to specific files in the repo (e.g., package entrypoints, workflow names, or pipeline/orchestrator configs).
