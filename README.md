# Strava Activities

Strava Activities is a Data Engineering project that implements an ETL/data pipelines in Databricks Free Edition around Strava athlete and activity data, together with dashboards (AI/BI) and CI/CD deployment pipelines. The repository contains code and configuration for ingesting Strava activity data, cleansing and transforming it (including building dimensions such as a calendar dimension), and deploying dashboards and pipelines to production in Databricks.

This README explains the repository's purpose, the main components, an architecture overview (with diagrams), and the tools and technologies used.

---

## Table of contents

- [Project overview](#project-overview)
- [Repository components](#repository-components)
- [Architecture & diagrams](#architecture--diagrams)
- [Tools & technologies](#tools--technologies)
- [Getting started (dev)](#getting-started-dev)
- [Production deployment & CI/CD notes](#production-deployment--cicd-notes)


---

## Project overview

### About Strava and authentication to Strava REST API

Strava is an online apllication which is used for tracking physical activity for users and incorporating them as social media features. It uses GPS information to track activity locations and supports multiple physical activities such as running, walking, cycling, swimming, etc. Strava records data for user's activities which can then be shared with user's followers or publicly on social media websites. An activity's recorded information may include a route summary, elevation (net and unidirectional), speed (average and maximum), timing (total and moving time), power and heart rate. Activities can be recorded using the mobile app or from devices manufactured by third parties like Garmin, Google Fit, Suunto, and Wahoo. Activities can also be entered manually via the Strava website and mobile app. To know more about strava please visit strava's website or download the app.

Strava exposes all the activity data which it collects using a REST API. The Strava REST API includes data on athletes, segments, routes, clubs, and gear. It is free to use. To get data on athletes, you will have to make an application and request that athletes sign in with Strava, and grant your application certain permissions using OAuth 2.0. You can get data on yourself without authentication for testing purposes. Strava REST API usage is limited on a per-application basis using both a 15-minute and daily request limit. The default rate limit allows 200 requests every 15 minutes, with up to 2,000 requests per day. 
To know more about the Strava REST API and how to set-up authentication to fetch data please visit the link [link](https://developers.strava.com/docs/getting-started/#oauth)

Other useful Strava REST API resources:<br>
[Strava Authentication](https://developers.strava.com/docs/authentication/)<br>
[Strava REST API Reference](https://developers.strava.com/docs/reference/)

### Project Information

This project collects and processes Strava athlete and activity data from Strava REST API using OAuth 2.0 authentication, performs cleansing and transformation tasks, builds useful dimensions (e.g., calendar), and enables downstream analytics and dashboards (AI/BI). The codebase includes packaging artifacts (wheel), job configurations, and deployment configuration for production pipelines and dashboards and running the pipelines on Databricks free edition account.

High-level responsibilities:
- Ingest athlete/profile and activity records from the Strava REST API
- Run data cleansing and transformation tasks
- Build model/dimension tables (e.g., calendar dimension)
- Package library/artifacts (wheel) for pipeline tasks
- Deploy ETL jobs and dashboards via CI/CD workflows

---

## Repository components

Here are the main components and where to look in the repository:

- strava_activities/
  - The primary Python package containing ingestion, cleansing, and transformation code for Strava data.
  - All pipeline transformation logic code is kept inside `strava_activities/src/strava_activities/etl` path.
  - The path `strava_activities/src/strava_activities/utils` contains re-usable utilities used for interacting with Strava API, read config files, etc.
  - Config files with Databricks catalog, schema, table names are kept inside `strava_activities/src/strava_activities/resources/config`

- .github/
  - GitHub Actions workflows and job configuration used for CI/CD (deployments, packaging, tests).
  - Presence of workflow/job config suggested by commits referencing production deployment and job configs.
  
- Packaging artifacts and pipelines
  - Commits mention wheel files and updated wheel settings — the repository builds Python wheels for use in scheduled jobs or deployment.
  - For information on wheel file configuration and entrypoints refer `strava_activities/pyproject.toml`.

- Deployment & job configuration
  - Job configs and pipeline definitions (referenced in commits) orchestrate the order of tasks, e.g., profile job followed by activity job.
  - Job configurations - `strava_activities/resources/jobs`

Other files you may find useful:
- README.md (this file)

---

## Architecture & diagrams

Below are conceptual architecture diagrams showing how the pipeline components interact. Use this as a guide when exploring the code

### Strava Athlete Profile Pipeline:

<img width="1536" height="1024" alt="strava_profile_pipeline" src="https://github.com/user-attachments/assets/aa9b26ae-59c8-4421-83c4-f7549a35b7dd" />

### Strava Athlete Activity Pipeline:

<img width="1536" height="1024" alt="strava_activities_pipeline" src="https://github.com/user-attachments/assets/169f7d26-a452-4ef5-8995-3d93169efa8a" />

- For Athlete Activity there are 2 types of data load:
  - Full Load - For one-time load of all strava activities since the start of `2024-01-01 00:00:00`. As there is a rate limit on Strava REST API as mentioned above, we try to get all activities from the REST API in batches of 100 days since the start and then all the way till the current day.
  - Incremental Load - Fetches all activities from the REST API in last 7 days from the date of execution.

The load type is specified in the config file and passed onto the pipeline as a parameter.

### Calendar Dimension Pipeline:

The calendar dimension pipeline is a one-time job which can be executed to generate a calendar dimension common in Data warehouses. This dimension table can be used to join with activities data in-order generate different insights.

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
3. Dashboards are refreshed/deployed from transformed data

---

## Tools & technologies

The repository explicitly and implicitly uses the following technologies:
- Databricks
  - The pipelines are deployed on a Databricks free edition account.
  - Bundle file specifies DABs details like dev and prod workspaces, and other DAB detials `strava_activities/databricks.yml`

- Apache Spark
  - Most of the pipeline code is written in PySpark.

- Python
  - The repository is primarily Python; code is organized under the `strava_activities` package.
  - Packaging uses wheel artifacts (commits referencing updated wheel settings).

- Strava API
  - Data ingestion targets Strava athlete and activity endpoints (OAuth tokens / API credentials required).

- CI/CD: GitHub Actions
  - The `.github` directory and commit messages indicate GitHub Actions workflows are in use for building, testing, and deploying pipelines and dashboards.
  - During deployment a python wheel file is created as per the specifications in `strava_activities/pyproject.toml` and copied to Databricks workspace at the default location. All python wheel tasks refer to the wheel file at this location during execution.

- ETL/Orchestration (conceptual)
  - The project is structured as a data pipeline (ingest -> cleanse -> transform -> store -> visualize).
  - The tasks are specified as *.yml configuration files under `strava_activities/resources/jobs`. These files serve as specifications for Databricks Asset Bundles to create jobs within Databricks at the time of deployment.

- Data storage / Analytics
  - Data is stored in Delta Lake tables inside Databricks.

- Packaging
  - Python wheel distribution is used to package library code for deployment to jobs.
  - Jobs are deployed through Databricks Asset Bundles(DABs) as Lakeflow Jobs. Job specifications are specified in *.yml config files.

---

## Production deployment & CI/CD notes

- The repository includes workflow and job config changes in commit history for "prod deployment", "AI/BI dashboards deployment", and "job configs".
- Wheels are built and used by jobs — ensure CI workflows have access to secrets and artifact storage.
- Production workflows likely rely on GitHub Actions; review `.github/workflows` to see job definitions and required secrets.
- Common deployment steps:
  1. Verify the job configs using Databricks Asset Bundles validate.
  1. Build wheel/artifact
  3. Publish artifact (internal registry or artifact store)
  4. Trigger deployment job(s) that run scheduled pipelines and refresh dashboards.
