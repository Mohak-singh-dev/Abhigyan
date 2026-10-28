# Abhigyan

Abhigyan is a React, TypeScript, and Vite dashboard backed by a FastAPI REST API, SQLAlchemy 2, and Supabase PostgreSQL. Existing API routes remain under `/api`; health is available at `/api/health`. Authentication uses JWT and bcrypt with role and case ownership checks.

## Production architecture

- **Frontend:** Vercel static Vite deployment (`npm run build`, output `dist`). `vercel.json` supplies SPA deep-link fallback.
- **API:** long-running Python Web Service on Render. A persistent service is the selected host because the API uses synchronous SQLAlchemy connections and scikit-learn model loading; a Vercel Python Function would require per-instance serverless connection behavior and cold-start/bundle tuning. The Render service is configured as an always-on Starter instance.
- **Database:** Supabase-hosted PostgreSQL, independent of the developer computer. The API uses only `DATABASE_URL` for database access.
- **ML:** Render builds the classifier from `backend/ml/training_data.csv` into deployment-local artifacts. Those files are included in the built service image, so the runtime does not depend on local persistent disk. The checked-in dataset is synthetic demonstration data; its predictions are not validated for operational decisions.

## Deploy

### 1. Prepare Supabase

1. Create or select the intended Supabase project and take a backup before changing an existing database.
2. In **Connect**, copy the PostgreSQL URL. For Render, use the **Session pooler** when Render cannot reach your project's direct IPv6 endpoint; use the direct URL if the service network supports it. Do not use the transaction pooler for this persistent service.
3. Keep SSL enabled. The app enforces `sslmode=require` if it is missing; `require` encrypts traffic but does not verify the server certificate. For certificate and hostname verification, install the Supabase CA certificate and use `sslmode=verify-full` with `sslrootcert`.
4. URL-encode reserved characters in the database password. Never put the URL in frontend variables or commit it.

The transaction pooler is intended for serverless and edge functions, uses port `6543`, and does not support prepared statements. This project does not use that mode. If the architecture changes to serverless, use the transaction-pooler URL, limit each SQLAlchemy process to one pooled connection, keep SSL required, and verify warm-instance connection health. The current `psycopg2` driver does not automatically prepare statements; if migrating to Psycopg 3, use `postgresql+psycopg://` with SQLAlchemy `connect_args={"prepare_threshold": None}` for transaction pooling. Keep migrations on a direct or session connection.

### 2. Deploy the API on Render

1. Push this repository to a Git provider accessible to Render, then create a Render Blueprint from the repository using `render.yaml` (or create a Python Web Service manually with root directory `backend`).
2. The Blueprint uses Python 3.11.11, installs `backend/requirements.txt`, trains ML artifacts from the checked-in synthetic dataset during build, starts Uvicorn on Render's `$PORT`, and checks `/api/health`.
3. Set the Blueprint's prompted environment variables in Render:

   | Variable | Value |
   | --- | --- |
   | `DATABASE_URL` | Supabase direct or session-pooler URL as above |
   | `JWT_SECRET_KEY` | Unique cryptographically random value, at least 32 characters |
   | `CORS_ORIGINS` | Exact production Vercel origin, e.g. `https://your-project.vercel.app`; no wildcard |
   | `ENVIRONMENT` | `production` (set in Blueprint) |
   | `DEMO_AUTH_ENABLED` | `false` (set in Blueprint) |
   | `API_PREFIX` | `/api` (set in Blueprint) |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` (adjust to policy; set in Blueprint) |

   Generate a secret locally with `python -c "import secrets; print(secrets.token_urlsafe(48))"`; enter its output directly in Render's secret field. Do not save it in this repository. Do not set `DEFAULT_SEED_PASSWORD` in Render.
4. Deploy and confirm Render reports `/api/health` healthy. The health endpoint checks database connectivity and returns a generic failure response without database exception details.
5. Apply schema migrations as a controlled one-time release step after reviewing the migration plan and taking a backup. In the Render Shell, from the service root (`backend`), run `python -m alembic -c alembic.ini upgrade head`. Do not run migrations automatically on each web-service startup. Do not run `backend/app/seed.py` against production.

The Blueprint selects Render's always-on `starter` plan; this avoids free-tier sleep and requires an active paid Render account. No deployment or database migration has been performed by this repository change.

### 3. Deploy the frontend on Vercel

1. Import the repository as a Vercel project with the repository root as the project root.
2. Use the Vite defaults or these settings: install command `npm ci --include=dev`; build command `npm run build`; output directory `dist`. The install command is also set in `vercel.json` so TypeScript and Vite dev dependencies are present during deployment.
3. Set `VITE_API_URL` in Vercel Production and Preview environments to the backend origin plus `/api`, for example `https://your-render-service.onrender.com/api`. This URL is public configuration, not a secret. The production build fails if it is missing, non-HTTPS, or points at localhost.
4. Deploy the frontend. Add its exact deployed origin (scheme and host, without a path) to Render's `CORS_ORIGINS`, then redeploy the API. For a custom frontend domain, include that exact origin too. Do not use `*.vercel.app` or `*` with credentialed CORS.

Keep database credentials, `JWT_SECRET_KEY`, seed passwords, and privileged keys out of every `VITE_` variable. No Supabase admin or service-role key is needed in this application frontend.

## Local development

1. Install Node.js and Python 3.11. Create a virtual environment and install `backend/requirements.txt`; run `npm install` at repository root.
2. Copy `backend/.env.example` to `backend/.env`. Set `DATABASE_URL` to the Supabase session-pooler URL (or another PostgreSQL URL), and replace the local-only `JWT_SECRET_KEY`. The checked-in local example has no seed password; if you need demo accounts on a disposable development database, set a private `DEFAULT_SEED_PASSWORD` in `backend/.env` before explicitly running the seed script.
3. Run `cd backend; python -m alembic -c alembic.ini upgrade head` only against the intended development database. Seeding is a separate, explicit step: `python app/seed.py`. The seed script refuses to run when `ENVIRONMENT=production`.
4. Start the API from `backend`: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
5. Copy root `.env.example` to `.env` if you want to override the frontend API base URL. Vite defaults to `http://localhost:8000/api` for development. Start the UI with `npm run dev`.

## Environment variables

### Backend

- `DATABASE_URL`: the only application database connection setting. PostgreSQL URLs are normalized to psycopg2 and SSL is required by default.
- `JWT_SECRET_KEY`: required in production; minimum 32 characters. Use a unique random value, not a demo/default value.
- `ENVIRONMENT`: set to `production` on Render. Production configuration validation fails for an insecure/missing JWT key, missing PostgreSQL URL, wildcard/non-HTTPS CORS, or enabled demo auth.
- `DEMO_AUTH_ENABLED`: always `false` in production. The backend also blocks `/api/auth/demo-login` whenever `ENVIRONMENT=production`.
- `CORS_ORIGINS`: comma-separated exact origins. Local defaults allow Vite dev and preview; production must list only HTTPS frontend origins.
- `API_PREFIX`: `/api`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: access token duration; default `120`.
- `DEFAULT_SEED_PASSWORD`: local seed-only input. The seeding function refuses to run in production and requires this to be explicitly set locally.
- `AI_CONFIDENCE_THRESHOLD`: optional advisory classifier threshold; default `0.40`.

### Frontend

- `VITE_API_URL`: API base URL including `/api`. Local development may omit it and use localhost. Production builds require a public HTTPS URL. Never put secrets here.

## Demo accounts and operational gaps

The repository contains synthetic demo account identities in the seed script and development login screen; historical demo builds used a shared password. The production frontend omits demo login shortcuts and begins complaint, user, overlap, and notification views without local demo records; failed API requests clear those lists instead of substituting fake case records. Treat any database seeded with demo records as non-production. Do not seed production, remove/disable demo users before launch if they already exist, and provision real accounts with unique passwords through an approved administrator process. Production startup rejects the known weak configuration and demo login is disabled server-side regardless of frontend visibility. Public complainant registration remains available as implemented; administrative roles must be provisioned through a trusted process.

**Production data onboarding remains required:** the production frontend loads its institution directory from the backend and no longer ships the demonstration roster, but the backend currently has no institution import workflow. Populate the production `institutions` table through a reviewed, authorized data import before enabling citizen intake. No real registry data was supplied, so this setup does not copy demonstration institutions into the production database or claim those records are official.

Email alerts and automatic SLA escalation have configuration UI but no background worker or SMTP integration. A persistent API process does not run scheduled jobs automatically; add a separately managed Render Cron Job or background worker with an idempotent job before enabling these operational features. In-app notifications are browser-state only and do not survive reloads or sync across devices. Supporting document binaries are held in browser memory and are not durable or uploaded; use private object storage with authorization, retention rules, and malware scanning before collecting real evidence. Do not use those demo controls as if they were live services.

## Migrations, verification, and rollback

- Alembic scripts remain the schema source of truth. Review each new migration and take a database backup before production application. Run `python -m alembic -c alembic.ini upgrade head` as an explicit release action, not at app startup.
- Frontend checks: `npm test`, `npx tsc --noEmit`, and production build with `VITE_API_URL=https://your-backend.example/api npm run build`.
- Backend checks: from repository root, `.venv/Scripts/python -m pytest backend/tests -v` on Windows or `.venv/bin/python -m pytest backend/tests -v` on Unix.
- The live API checks in `src/api/__tests__` expect a running API and development test data; run those only against a disposable development database. Never aim these tests or seed scripts at production.
- After deploy, check `GET https://<backend-host>/api/health`, sign in with a real provisioned account, and verify role/ownership boundaries and key workflows in a staging environment before launch.
- If an application deploy fails, use Render's previous successful deploy and Vercel's previous deployment. Database migrations may not be reversible without data loss; do not downgrade automatically. Restore a backup or apply a reviewed forward-fix migration if schema rollback is unsafe.

## Troubleshooting

- **Frontend reports API URL is not configured:** set `VITE_API_URL` in the Vercel project's environment and redeploy.
- **Browser CORS error:** check `CORS_ORIGINS` exactly matches the frontend origin, including `https://`, and redeploy the API.
- **Health endpoint returns 503:** verify Render `DATABASE_URL`, password URL encoding, selected Supabase connection mode, network reachability, and SSL. Never paste connection strings into logs or issue reports.
- **Login fails after deployment:** confirm production has `DEMO_AUTH_ENABLED=false`, the account has a password hash, and demo/seed identities were not carried into the production database.
- **Classifier reports unavailable:** inspect Render build logs for the `python ml/train_model.py` build step and verify model files are included in the built service. Runtime training or local disk persistence is not used.
- **A route refresh returns 404:** ensure the Vercel project root contains the committed `vercel.json` and output directory is `dist`.
