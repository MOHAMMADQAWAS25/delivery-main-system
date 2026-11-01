# Agent Feature Log

This file is the repository's running implementation history for agent-assisted work.

## Working rule

- Read this file before making any change in this repository.
- After completing work, add a dated entry describing what changed and how it was verified.
- State whether a database migration is required and name it when applicable.
- Keep entries concise, factual, and limited to this repository.

## Entries

### 2026-09-28 - Retest Supabase database connectivity

- Verified the corrected `DATABASE_URL` has the asyncpg driver, complete direct Supabase host, port `5432`, database name, username, and a populated password without exposing secret values.
- Verified the authenticated Supabase API request still succeeds.
- The read-only PostgreSQL check reached connection setup but failed DNS resolution because the direct Supabase database endpoint requires IPv6 in this environment; use the project's Session Pooler connection string for IPv4 access.
- Verification: Supabase API passed; database `SELECT 1` was not reached because direct-host DNS resolution failed.
- Migration required: No.

### 2026-09-28 - Validate Supabase connectivity configuration

- Confirmed the ignored local environment contains all three required Supabase variables without exposing their values.
- Verified an authenticated request to the configured Supabase API succeeds.
- The read-only PostgreSQL `SELECT 1` check could not start because the configured `DATABASE_URL` is malformed with an empty port; the URL must be replaced with a complete single-line connection string.
- Verification: Supabase API passed; database URL parsing failed before any database connection was attempted.
- Migration required: No.

### 2026-09-28 - Make database configuration Supabase-only

- Removed the local `POSTGRES_*` fallback fields from application settings, `.env.example`, and the ignored local `.env` file.
- Made `DATABASE_URL` the single PostgreSQL connection setting alongside the Supabase project URL and backend secret key.
- Added a regression test confirming that no localhost/PostgreSQL-host fallback remains.
- Verification: 3 pytest tests passed; mypy reported no issues in 29 source files; Python byte-compilation and `git diff --check` passed.
- Migration required: No.

### 2026-09-28 - Add local Supabase configuration placeholders

- Added blank `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and `DATABASE_URL` placeholders to `.env.example`.
- Created the ignored local `.env` file with the same blank placeholders for developer-supplied secrets.
- Verification: confirmed `.env` exists locally, is ignored by Git, and contains no secret values; `git diff --check` passed.
- Migration required: No.

### 2026-09-28 - Establish the FastAPI architecture foundation

- Added the `entities -> app -> interface/infrastructure` package structure based on Shadow's practical clean architecture, adapted for the InkFig domain.
- Added a FastAPI application factory, configurable CORS and `/api/v1` prefix, root and versioned health endpoints, environment template, PostgreSQL-ready dependencies, test/type-check configuration, and architecture documentation.
- Reserved organized locations for DTOs, enums, exceptions, repository ports, services, routes, controllers, dependencies, middleware, SQLAlchemy models, repositories, integrations, and timestamped migrations.
- Verification: 2 pytest tests passed; mypy reported no issues in 29 source files; Python byte-compilation and `git diff --check` passed.
- Migration required: No. The migrations directory is structural only.

### 2026-09-28 - Document the InkFig product vision

- Added `README.md` with the project's university context, art-community purpose, planned discovery and interaction features, AI-assisted image search, teacher event moderation workflow, and access-control direction.
- Clarified that this repository owns InkFig's main business features and workflows.
- Verification: reviewed the rendered Markdown structure and ran Git's whitespace validation.
- Migration required: No.

### 2026-09-27 - Initialize agent feature log

- Added this repository-level feature log and established the read-before-work and update-after-work convention.
- Verification: confirmed the file exists in the repository.
- Migration required: No.

## 2026-09-28 - Standardize agent feature log requirements

### Request

Require every repository to use a root `AGENT_FEATURE_LOG.md`, read it fully before each ticket, preserve its history, and append every completed ticket using the prescribed structured sections.

### Changes

- Renamed the existing root feature log to the exact uppercase filename while preserving all previous entries unchanged.
- Adopted the required entry format for this and all future tickets.
- Intentionally left application behavior, authorization, APIs, database configuration, and dependencies unchanged.

### Repositories

- `delivery-main-system`: standardized the root feature-log filename and adopted the structured ticket record.
- `delivery-user-system`: standardized the root feature-log filename and adopted the structured ticket record.
- `delivery-user-FE`: standardized the root feature-log filename and adopted the structured ticket record.

### Files

- `AGENT_FEATURE_LOG.md`: renamed from `agent_feature_log.md` and appended this structured entry.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or role access changed.
- No organization or domain scope changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] git status --short` - confirmed the case-only rename is tracked.
- `[passed] git diff --check`
- `[not run] application tests and builds` - documentation-only filename and log-format change.

### Deployment

No special deployment steps.

### Git

- Branch: `main`
- Commit: `89e00b0`
- Push: `successful`

### Notes

Historical entries retain their original format; the required structured format applies from this entry onward.

## 2026-09-28 - Verify live Supabase connections

### Request

Retest the backend connection after replacing the direct IPv6 PostgreSQL URL with the Supabase Session Pooler connection string.

### Changes

- Performed read-only live checks against the configured Supabase API and PostgreSQL database without printing credentials.
- Confirmed the Session Pooler connection works with SQLAlchemy and asyncpg.
- Removed the temporary diagnostic script after verification.
- Intentionally left runtime application code and configuration values unchanged.

### Repositories

- `delivery-main-system`: verified its local Supabase API and database configuration.
- `delivery-user-system`: verified its local Supabase API and database configuration.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the successful live connection verification.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or roles changed.
- No organization or domain scope changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] authenticated GET to the configured Supabase REST API root`
- `[passed] SQLAlchemy asyncpg connection through the Supabase Session Pooler`
- `[passed] SELECT 1`
- `[not run] pytest and mypy` - no application source code changed.

### Deployment

- Configure `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and the Session Pooler `DATABASE_URL` in each deployed backend environment.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `d0987be`
- Push: `successful`

### Notes

The verified local `.env` secrets remain ignored by Git and were not printed or committed.

## 2026-09-29 - Add AWS SAM Lambda deployment template

### Request

Prepare the InkFig main FastAPI backend for deployment to AWS Lambda using AWS SAM and add a root `template.yaml`.

### Changes

- Added a Mangum adapter that exposes the existing FastAPI application as an AWS Lambda handler.
- Added a SAM template with Python 3.13, x86_64 Lambda, API Gateway HTTP API root/proxy events, tracing, resource tags, and API/function outputs.
- Added deployment parameters for environment, trusted CORS origins, Supabase URL, backend secret key, Session Pooler database URL, and project name; secret parameters use `NoEcho`.
- Added Mangum to backend dependencies and excluded `.aws-sam/` build output from Git.
- Made the existing settings regression test inspect model defaults without loading local secrets.
- Documented SAM validation, build, and guided deployment commands.
- Intentionally left FastAPI routes, authorization behavior, database schema, and custom-domain configuration unchanged.

### Repositories

- `delivery-main-system`: added its Lambda handler, SAM template, deployment documentation, dependency, and focused test.
- `delivery-user-system`: added its Lambda handler, SAM template, deployment documentation, dependency, and focused test.

### Files

- `template.yaml`: defines the main-system Lambda and API Gateway HTTP API.
- `src/lambda_handler.py`: wraps FastAPI with Mangum.
- `requirements.txt`: adds Mangum.
- `tests/test_health.py`: verifies the Lambda handler and avoids loading secret configuration in assertions.
- `.gitignore`: excludes SAM build artifacts.
- `README.md`: documents validation, build, deployment, and parameter handling.
- `AGENT_FEATURE_LOG.md`: records this ticket.

### API

- `ANY /`: API Gateway forwards root requests to FastAPI.
- `ANY /{proxy+}`: API Gateway forwards all nested paths, including `/api/v1/*`, to FastAPI.
- No request fields, responses, filters, validation, permission checks, or application error contracts changed.

### Database

No migration required.

### Permissions and scope

- No application permissions, roles, or access scopes changed.
- Existing and future backend authorization remains authoritative inside FastAPI.
- The SAM template creates only the Lambda execution role required by the serverless function; no domain-specific IAM permissions were added.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML compose check for template.yaml`
- `[passed] py -m pytest` - 4 tests passed.
- `[passed] py -m mypy src tests` - no issues in 30 source files.
- `[passed] py -m compileall -q src tests`
- `[passed] git diff --check`
- `[failed] initial py -m pytest` - the pre-existing settings test loaded local `.env` data and was corrected to inspect field defaults without exposing values.
- `[not run] sam validate --lint` - AWS SAM CLI is not installed in this environment.
- `[not run] sam build` - AWS SAM CLI is not installed in this environment.

### Deployment

- Deploy `delivery-main-system` as its own SAM/CloudFormation stack.
- Run `sam validate --lint`, `sam build`, and `sam deploy --guided` on a machine with AWS SAM CLI and configured AWS credentials.
- Provide `CorsOrigins`, `SupabaseUrl`, `SupabaseSecretKey`, and the Session Pooler `DatabaseUrl` during deployment; do not save secrets in committed files.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `f132664`
- Push: `successful`

### Notes

Custom domains and ACM certificates remain follow-up work after the production domains are chosen. The database password appeared in failed test output and must be rotated before deployment.

## 2026-09-29 - Align local folders with renamed repositories

### Request

Rename the local repository folders to match the new InkFig GitHub repository names.

### Changes

- Renamed the local folder from `delivery-main-system` to `inkfig-main-system`.
- Updated `origin` from the legacy redirected repository URL to the canonical `inkfig-main-system` GitHub URL.
- Removed only the empty old folder remnant left by the Windows move operation.
- Intentionally left application code, configuration values, dependencies, and runtime behavior unchanged.

### Repositories

- `inkfig-main-system`: renamed its local folder and updated its canonical `origin` URL.
- `inkfig-user-system`: renamed its local folder and updated its canonical `origin` URL.
- `inkfig-user-FE`: renamed its local folder and updated its canonical `origin` URL.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the local folder and remote URL alignment.
- No application files changed.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, authorization checks, or access scopes changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] git status --short --branch` - repository remained clean after the move.
- `[passed] git remote get-url origin` - canonical InkFig remote URL is configured.
- `[passed] git ls-remote --exit-code origin refs/heads/main` - renamed GitHub repository is reachable.
- `[passed] workspace directory inspection` - only the three new repository folder names remain.
- `[not run] application tests and builds` - no application files changed.

### Deployment

- Update local scripts or external deployment jobs that still reference the old `delivery-main-system` folder or repository URL.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `070f7e1`
- Push: `successful`

### Notes

The old GitHub URL redirected successfully, but the canonical URL is now configured directly.
## 2026-09-29 - Align AWS SAM runtime with local Python 3.12

### Request

Fix the AWS SAM build failure caused by the template requiring Python 3.13 while the development machine provides Python 3.12.

### Changes

- Changed the Lambda runtime from `python3.13` to `python3.12` so SAM can use the installed interpreter.
- Aligned mypy's configured Python version and the README development documentation with Python 3.12.
- Left application behavior, authentication, API contracts, and deployment topology unchanged.

### Repositories

- `inkfig-main-system`: aligned the SAM, type-checking, and documented Python runtime.
- `inkfig-user-system`: received the matching runtime alignment in its own repository.

### Files

- `template.yaml`: changed the Lambda runtime to `python3.12`.
- `mypy.ini`: changed the type-checking target to Python 3.12.
- `README.md`: documented Python 3.12 as the backend development version.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or role scopes changed.
- Existing backend authorization remains unchanged and backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] py -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` when this runtime correction is needed in AWS.
- No migration is required before deployment.
- No environment-variable or configuration-value changes are required; rebuild the SAM artifact before deployment.

### Git

- Branch: `main`
- Commit: `35a14c4`
- Push: `successful`

### Notes

Python 3.12 is an AWS Lambda-supported runtime and matches the installed local interpreter. Using `sam build --use-container` remains an optional alternative when a matching local interpreter is unavailable.
## 2026-09-29 - Configure the main API custom domain

### Request

Configure `main-api.inkfig-hu.com` as the Cloudflare-managed hostname for the main backend.

### Changes

- Added a regional API Gateway custom domain secured by an ACM certificate supplied at deployment.
- Mapped the custom domain root path to the HTTP API `$default` stage using TLS 1.2.
- Added stack outputs for the public custom URL and the generated API Gateway hostname required as the Cloudflare CNAME target.
- Assigned the main backend its own CloudFormation stack and S3 prefix so it cannot collide with the user backend deployment.
- Documented ACM region and Cloudflare DNS/proxy requirements.
- Left FastAPI behavior, authorization, APIs, and database access unchanged.

### Repositories

- `inkfig-main-system`: configured `main-api.inkfig-hu.com` and its deployment outputs.
- `inkfig-user-system`: separately configured `user-api.inkfig-hu.com`.

### Files

- `template.yaml`: added the certificate parameter, API Gateway custom domain, API mapping, and domain outputs.
- `samconfig.toml`: added the repository-specific deployment stack configuration.
- `README.md`: documented certificate and Cloudflare CNAME setup.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

- `ANY https://main-api.inkfig-hu.com/`: maps to the existing HTTP API `$default` stage.
- `ANY https://main-api.inkfig-hu.com/{proxy+}`: continues forwarding nested FastAPI routes.
- No request, response, validation, filtering, or error-contract changes.

### Database

No migration required.

### Permissions and scope

- No application permissions, roles, or scopes changed.
- Existing backend authorization remains authoritative and backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check`

### Deployment

- Deploy the `inkfig-main-system` stack in `eu-west-1` and provide an ACM certificate ARN valid for `main-api.inkfig-hu.com` from that region.
- After deployment, create Cloudflare CNAME `main-api` pointing to the `CloudflareCnameTarget` stack output; use DNS-only during initial validation.
- No migration is required before deployment.
- Existing Supabase, database, CORS, and environment parameters remain required.

### Git

- Branch: `main`
- Commit: `03c8fb2`
- Push: `successful`

### Notes

Cloudflare DNS cannot be completed until AWS deploys the custom domain and returns its unique regional hostname. If Cloudflare proxying is enabled later, use Full (strict) SSL/TLS mode.
## 2026-09-29 - Order API domain mapping after stage creation

### Request

Fix the API Gateway custom-domain deployment failure reporting `Invalid stage identifier specified` while creating the domain mapping.

### Changes

- Added an explicit CloudFormation dependency so `ApiDomainMapping` waits for the SAM-generated `$default` HTTP API stage.
- Applied the correction to both backends to prevent the same creation-order race during fresh deployments or resource replacement.
- Preserved locally generated `samconfig.toml` deployment values without committing them.
- Left application behavior, API contracts, authorization, and database access unchanged.

### Repositories

- `inkfig-main-system`: added the stage dependency as a preventive correction.
- `inkfig-user-system`: added the stage dependency that resolves the observed failed deployment.

### Files

- `template.yaml`: made `ApiDomainMapping` depend on `HttpApiApiGatewayDefaultStage`.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, or access scopes changed.
- Existing backend authorization remains backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- template.yaml`

### Deployment

- No immediate redeployment is required for the already healthy main-system stack.
- Future deployments will wait for the HTTP API stage before creating or replacing the domain mapping.
- No migration is required and no new environment variables are needed.

### Git

- Branch: `main`
- Commit: `8fa6fe0`
- Push: `successful`

### Notes

The user-system failure occurred because CloudFormation created the mapping concurrently with its stage; the certificate and domain resource were valid.
## 2026-09-29 - Deploy the main backend from GitHub Actions

### Request

Automatically test and deploy the main backend to AWS whenever changes are pushed to the `main` branch.

### Changes

- Added a GitHub Actions workflow triggered by pushes to `main` and manual dispatches.
- Added Python 3.12 dependency installation, pytest, mypy, SAM validation, SAM build, non-interactive deployment, and production health verification.
- Used GitHub OIDC and temporary AWS credentials instead of permanent AWS access keys.
- Serialized production deployments to prevent overlapping CloudFormation updates.
- Passed production backend configuration from GitHub secrets without relying on local `samconfig.toml` values.
- Documented the required GitHub environment, secrets, and AWS deployment-role responsibilities.
- Left runtime behavior, APIs, authorization, and database schema unchanged.

### Repositories

- `inkfig-main-system`: added automated deployment for the main backend.
- `inkfig-user-system`: added the corresponding user-backend deployment workflow.

### Files

- `.github/workflows/deploy.yml`: tests, validates, builds, deploys, and health-checks the main backend.
- `README.md`: documents OIDC and required GitHub secrets.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- The workflow requests only `contents: read` and `id-token: write` GitHub permissions.
- AWS access is obtained through an IAM role restricted by its GitHub OIDC trust policy and AWS permissions.
- No application roles or backend authorization rules changed.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- .github/workflows/deploy.yml README.md`
- `[not run] GitHub Actions deployment` — requires the production environment, OIDC role, and repository secrets to be configured in GitHub.

### Deployment

- Configure the GitHub `production` environment and the documented secrets before relying on automatic deployment.
- Configure the AWS GitHub OIDC provider and deployment role, restricted to this repository's `main` branch.
- After setup, every push to `main` deploys the `inkfig-main-system` stack in `eu-west-1`.
- No migration is required.

### Git

- Branch: `main`
- Commit: `7c6c91c`
- Push: `successful`

### Notes

The first workflow run will fail at AWS authentication until `AWS_DEPLOY_ROLE_ARN` and the other required secrets exist. Local `samconfig.toml` changes were preserved and intentionally excluded.
## 2026-09-29 - Review and map the current project foundation

### Request

Read the InkFig repositories and establish an accurate understanding of the product, service boundaries, implementation status, and deployment model before future feature work.

### Changes

- Reviewed the product documentation, architecture rules, runtime entry points, health request flow, configuration, tests, SAM infrastructure, and deployment workflow.
- Confirmed this service owns artwork, portfolios, discovery, likes, recommendations, search, events, submissions, moderation, and reports, while identity and access management belong to the user system.
- Confirmed the repository currently provides architecture and deployment foundations plus health endpoints; domain workflows and persistence implementations are not yet implemented.
- Intentionally left application behavior and configuration unchanged.

### Repositories

- `inkfig-main-system`: reviewed and documented the current main-backend baseline.
- `inkfig-user-system`: reviewed alongside this service to verify ownership boundaries.
- `inkfig-user-FE`: reviewed alongside this service to verify client integration and deployment boundaries.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the project-understanding pass.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

No permissions, roles, authorization behavior, or access scopes changed.

### Frontend

No frontend changes.

### Verification

- `[passed] repository source, architecture, configuration, tests, and deployment files reviewed`
- `[passed] git diff --check`
- `[not run] application tests and builds` - documentation-only change.

### Deployment

No deployment changes or special steps.

### Git

- Branch: `main`
- Commit and push: performed after verification.

### Notes

This entry records understanding only; it does not claim that planned product capabilities are already implemented.
## 2026-09-29 - Preserve JSON configuration in automated SAM deployment

### Request

Fix the automated deployment after the production health check returned HTTP 500 following an otherwise successful GitHub Actions deployment.

### Changes

- Diagnosed the Lambda startup failure from CloudWatch as an invalid `CORS_ORIGINS` value; the command-line SAM override had deployed only `[` instead of a JSON array.
- Replaced shell-expanded SAM overrides with an ephemeral structured JSON parameter file generated on the GitHub runner.
- Preserved the exact production CORS JSON and passed Supabase, database, and certificate secrets without printing them.
- Applied the same correction to both backend workflows to prevent an identical failure in the user service.
- Left application behavior, API contracts, authorization, and database schema unchanged.

### Repositories

- `inkfig-main-system`: fixed the workflow responsible for the observed production 500.
- `inkfig-user-system`: applied the same safe parameter handling proactively.

### Files

- `.github/workflows/deploy.yml`: generates and supplies a structured SAM deployment-parameter file.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- GitHub OIDC and AWS IAM permissions remain unchanged.
- No application permissions, roles, or authorization scopes changed.

### Frontend

No frontend changes.

### Verification

- `[passed] CloudWatch log inspection` — identified `SettingsError` while parsing `cors_origins`.
- `[passed] deployed Lambda configuration inspection` — confirmed the malformed value was only `[` without exposing secrets.
- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- .github/workflows/deploy.yml`
- `[not run] corrected GitHub Actions deployment` — triggered by pushing this fix and verified after the push.

### Deployment

- Pushing this correction triggers deployment of the `inkfig-main-system` stack and its production health check.
- No environment-secret changes or database migrations are required.

### Git

- Branch: `main`
- Commit: `9c64526`
- Push: `successful`

### Notes

The production outage was caused by command-line quoting, not FastAPI application logic or the Lambda runtime.
## 2026-09-29 - Use a SAM-supported deployment parameter file

### Request

Complete the automated CORS recovery after the first structured-parameter workflow run failed immediately in the SAM deploy step.

### Changes

- Changed the ephemeral parameter filename from `.json` to `.yaml`, one of the file extensions supported by the installed SAM CLI parameter parser.
- Retained JSON-formatted content because JSON is valid YAML and preserves the CORS array and secret strings exactly.
- Left application behavior, APIs, authorization, infrastructure resources, and database schema unchanged.

### Repositories

- `inkfig-main-system`: corrected the deployment parameter-file extension.
- `inkfig-user-system`: applied the same correction.

### Files

- `.github/workflows/deploy.yml`: writes the structured parameter document with a SAM-supported `.yaml` extension.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No GitHub, AWS IAM, application permission, role, or scope changes.

### Frontend

No frontend changes.

### Verification

- `[passed] installed SAM CLI parameter parser loaded the YAML file and returned ["https://inkfig-hu.com"] exactly`
- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] git diff --check -- .github/workflows/deploy.yml`
- `[failed] prior corrected GitHub Actions deployment` — SAM rejected `.json` as an unsupported parameter-file extension before contacting CloudFormation.

### Deployment

- Pushing this correction triggers the main production deployment again.
- No secret, configuration-value, or migration changes are required.

### Git

- Branch: `main`
- Commit: `2b04744`
- Push: `successful`

### Notes

The parameter document remains structured and ephemeral; only its extension changed for SAM CLI compatibility.
## 2026-10-01 - Public artwork upload and feed foundation

### Request

Prepare the backend and database so every user can upload typed artwork, store image files in Supabase, publish the work publicly, and allow authenticated users to like it. Official system work types will be supplied later.

### Changes

- Added a clean-architecture works domain with DTOs, service contracts, repository implementation, FastAPI routes, and Supabase Storage integration.
- Added a two-stage upload workflow: the authenticated owner requests a signed upload URL, uploads directly to Supabase Storage, and then publishes only after the backend verifies that the object exists.
- Added a public cursor-ready feed and authenticated, idempotent like/unlike operations.
- Added JWT validation compatible with access tokens issued by `inkfig-user-system`; the Supabase service key remains backend-only.
- Added automated database migration execution to the production deployment workflow.
- Intentionally left the work-type table empty until the official system types are provided.

### Repositories

- `inkfig-main-system`: added works APIs, persistence, storage integration, database migration, tests, and deployment configuration.
- `inkfig-user-FE`: consumes these APIs in a separate repository change.

### Files

- `migrations/20261001_001_create_works.sql`: creates the works schema and configures the Storage bucket.
- `migrations/run.py`: applies tracked migrations idempotently and verifies the works schema.
- `src/app/services/work_service.py`: implements upload, publish, feed, and like workflows.
- `src/infrastructure/repositories/work_repository.py`: implements PostgreSQL work persistence and feed queries.
- `src/infrastructure/integrations/supabase_storage.py`: creates signed upload URLs and verifies stored objects.
- `src/interface/api/routes/works.py`: exposes the works HTTP API.
- `template.yaml`: supplies JWT and works configuration to Lambda.
- `.github/workflows/deploy.yml`: passes the JWT secret and runs migrations before deployment.
- `tests/test_work_service.py`: verifies core ownership, file validation, publication, and feed behavior.

### API

- `GET /api/v1/works/types`: publicly lists active system work types.
- `GET /api/v1/works`: publicly lists published works; accepts `limit` from 1 to 50 and an optional `before` timestamp, and includes viewer-like state when a valid bearer token is supplied.
- `POST /api/v1/works/uploads`: requires authentication; validates type, title, description, supported image MIME type, and a maximum 10 MiB size, then returns a work ID and short-lived signed upload URL.
- `POST /api/v1/works/{work_id}/publish`: requires the owning user and an existing uploaded object; returns 404 when the owned draft or object is unavailable.
- `PUT /api/v1/works/{work_id}/like`: requires authentication and idempotently likes a published work.
- `DELETE /api/v1/works/{work_id}/like`: requires authentication and idempotently removes the user's like.

### Database

- Migration: `20261001_001_create_works.sql`
- Creates `work_types`, `works`, and `work_likes`, including ownership/type foreign keys, unique storage paths, size/status checks, public-feed and owner indexes, timestamps, and cascading cleanup for owned works and likes.
- Creates or updates the public `works` Storage bucket with a 10 MiB limit and JPEG, PNG, WebP, and GIF MIME restrictions.
- Enables RLS and removes direct anon/authenticated table grants; database access remains backend-controlled through the service role/PostgreSQL connection.
- No type rows are backfilled. Rollback requires preserving or deliberately removing uploaded Storage objects separately from relational rows.

### Permissions and scope

- Public visitors can read active types and published works.
- Any authenticated InkFig user can prepare uploads and like or unlike published works.
- Only the work owner can publish that work's draft; ownership is validated by backend database predicates.
- Authentication and authorization are validated by the backend using the shared JWT signing secret and issuer.

### Frontend

- No frontend changes in this repository; `inkfig-user-FE` contains the upload page and public-feed integration.

### Verification

- `[passed] uv run --with-requirements requirements.txt ruff check src tests`
- `[passed] uv run --with-requirements requirements.txt pytest — 8 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 43 files`
- `[passed] python -m migrations.run — migration applied and works tables/public bucket verified`
- `[passed] sam validate --lint`
- `[failed] sam build — local machine does not have a Python 3.12 executable on PATH; GitHub Actions installs Python 3.12 before building`

### Deployment

- Deploy `inkfig-main-system`; the workflow runs the database migration before the SAM deployment.
- Configure `JWT_SECRET` in the main backend production GitHub environment with the same value used by `inkfig-user-system`.
- Existing `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, and AWS/ACM secrets remain required.

### Git

- Branch: `main`
- Commit: `1f2271a`
- Push: `successful`

### Notes

Signed upload URLs avoid sending image bodies through API Gateway/Lambda. Draft rows can remain if a client requests a URL but never publishes; stale-draft cleanup can be added later. Access-token revocation takes effect in this service when the short-lived token expires because this service validates the signed token without querying the user service on every request.

## 2026-10-01 - Fix nullable public-feed query parameters

### Request

Verify the newly deployed works foundation and correct the public feed after production returned HTTP 500 for an empty unauthenticated request.

### Changes

- Added explicit PostgreSQL casts for nullable viewer UUID and cursor timestamp parameters in the public-feed query.
- Kept feed ordering, visibility, pagination, and authorization behavior unchanged.

### Repositories

- `inkfig-main-system`: corrected the PostgreSQL public-feed query.

### Files

- `src/infrastructure/repositories/work_repository.py`: casts nullable parameters so asyncpg can prepare the statement.

### API

- `GET /api/v1/works`: now returns an empty feed instead of HTTP 500 when both the optional viewer and cursor are absent.

### Database

- No migration required.

### Permissions and scope

- No permission changes; the feed remains public and optional bearer-token validation remains backend-enforced.

### Frontend

- No frontend changes.

### Verification

- `[passed] direct SqlAlchemyWorkRepository.list_published(None, 21, None) query against Supabase — feed_rows=0`
- `[passed] production Lambda logs identified asyncpg AmbiguousParameterError before the correction`

### Deployment

- Redeploy `inkfig-main-system` through the existing GitHub Actions workflow.
- No migration or configuration changes are required.

### Git

- Branch: `main`
- Commit: `749d701`
- Push: `successful`

### Notes

The failure was specific to asyncpg preparing untyped null bind parameters; explicit `uuid` and `timestamptz` casts make the statement deterministic.

## 2026-10-04 - Add canonical work categories and feed filtering

### Request

Create Digital Art, Hand Art, Video, Audio, Animation, Games, Interactive, and VR/AR categories and support homepage navigation between them.

### Changes

- Added an idempotent migration that inserts or reactivates all eight canonical work types with English and Arabic names.
- Added an optional `type_code` query parameter to the public works feed.
- Passed the selected type code through the API route, service, repository contract, and PostgreSQL repository.
- Added a parameterized work-type predicate to the published-feed query without changing public visibility, pagination, or like behavior.
- Added service regression coverage proving a category code reaches the repository.
- Preserved Lambda initialization and dependency construction, so the change remains compatible with future AWS Lambda SnapStart use.

### Repositories

- `inkfig-main-system`: seeds canonical types and filters the public feed authoritatively.
- `inkfig-user-FE`: provides the localized homepage category controls and sends `type_code`.
- `inkfig-user-system`: no changes required.

### Files

- `migrations/20261004_001_seed_work_categories.sql`: upserts the eight active bilingual categories.
- `src/interface/api/routes/works.py`: accepts the optional validated `type_code` filter.
- `src/app/services/work_service.py`: forwards the filter while preserving pagination.
- `src/entities/repositories/works.py`: extends the repository contract.
- `src/infrastructure/repositories/work_repository.py`: applies the parameterized category predicate.
- `tests/test_work_service.py`: verifies filter propagation.
- `AGENT_FEATURE_LOG.md`: records this ticket.

### API

- `GET /api/v1/works` accepts optional `type_code` (1-64 characters).
- Omitting `type_code` preserves the existing all-works feed.
- Supplying a canonical code returns published works from that category only.
- Response fields, pagination shape, authentication behavior, and errors are unchanged.

### Database

- Migration required: `20261004_001_seed_work_categories.sql`.
- The migration is idempotent through `ON CONFLICT (code) DO UPDATE` and reactivates canonical categories.

### Permissions and scope

- The public feed remains publicly readable.
- Uploads remain authenticated and backend-authorized.
- Category filtering cannot broaden visibility; it only narrows the existing published feed.
- Existing service-role-only table access and backend authorization remain authoritative.

### Frontend

The paired frontend change renders the categories as a localized homepage filter and sends the selected canonical code to this endpoint.

### Verification

- `[passed] git diff --check`
- `[passed] migration-runner inspection` - the existing runner discovers all sorted `*.sql` migrations, including the new seed file.
- `[not run] pytest, mypy, and compileall` - no Python interpreter is installed or discoverable in this environment.
- `[not run] sam validate --lint` - AWS SAM CLI is not installed in this environment.

### Deployment

- Deploy `inkfig-main-system` first and run `migrations/run.py` so all eight work types exist before exposing the filter.
- Deploy `inkfig-user-FE` second.
- No new environment variables are required.

### Git

- Branch: `main`
- Commit: this ticket's focused commit.
- Push: pushed directly to `origin/main` after synchronization.

### Notes

The migration owns stable category codes while display names remain bilingual and can be updated safely without changing filter URLs.
## 2026-10-04 - Synchronize main API JWT validation secret

### Request

Fix `Invalid or expired access token.` when an authenticated user attempts to upload a work.

### Changes

- Diagnosed the deployed Lambda configuration and confirmed the user API had a JWT signing secret while the main API secret was empty.
- Updated the main deployment workflow to securely read the existing signing secret from the deployed user API after AWS authentication.
- Masks the secret before adding it to the GitHub Actions environment and stops deployment when the source secret is missing.
- Removed the ineffective dependency on a separate main-repository `JWT_SECRET` GitHub secret.
- Left token claims, expiry, upload behavior, APIs, and database structure unchanged.

### Repositories

- `inkfig-main-system`: corrected production JWT-secret provisioning and added regression coverage.

### Files

- `.github/workflows/deploy.yml`: retrieves, validates, masks, and passes the shared user API JWT secret into the main SAM stack.
- `tests/test_health.py`: verifies the deployment cannot regress to an independent or missing JWT secret.

### API

- No API contract changes. Authenticated work endpoints now accept valid access tokens issued by `inkfig-user-system` after deployment.

### Database

- No migration required.

### Permissions and scope

- Existing authenticated-user and work-owner rules are unchanged.
- JWT signature, issuer, token type, expiry, and subject validation remain backend-enforced.
- The main GitHub deployment role requires `lambda:GetFunctionConfiguration` for `inkfig-user-system-api`.

### Frontend

- No frontend changes.

### Verification

- `[passed] deployed Lambda configuration comparison — issuer values matched; main secret was confirmed empty without printing either secret`
- `[passed] uv run --with-requirements requirements.txt ruff check src tests`
- `[passed] uv run --with-requirements requirements.txt pytest — 10 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 43 source files`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` through GitHub Actions.
- No migration is required.
- The user API must remain deployed with a nonempty `JWT_SECRET`; no new frontend or GitHub secret is required.

### Git

- Branch: `main`
- Commit: `a230f27`
- Push: `successful`

### Notes

The signing value remains secret and was never printed. A future central AWS Secrets Manager value could replace the user Lambda as the shared source of truth if desired.

## 2026-10-04 - Permit main deployment to read shared JWT configuration

### Request

Complete the JWT synchronization deployment after GitHub Actions was denied while reading the user API Lambda configuration.

### Changes

- Added `lambda:GetFunctionConfiguration` to the main GitHub deployment role for only `inkfig-user-system-api`.
- Preserved every existing deployment-role statement unchanged.
- Removed the temporary local policy document after application.

### Repositories

- `inkfig-main-system`: recorded the required external IAM deployment permission.

### Files

- `AGENT_FEATURE_LOG.md`: records the IAM correction and verification.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- AWS role `InkFigMainSamDeployPolicy` can read configuration only from `arn:aws:lambda:eu-west-1:710412005992:function:inkfig-user-system-api` in addition to its existing permissions.
- No runtime application role or end-user permission changed.

### Frontend

No frontend changes.

### Verification

- `[passed] aws iam simulate-principal-policy — lambda:GetFunctionConfiguration evaluated as allowed for the exact user API Lambda ARN`
- `[failed] initial GitHub Actions run 37220723930 — deployment role lacked the new read permission`

### Deployment

- Rerun the `inkfig-main-system` GitHub Actions deployment.
- No migration or environment-variable change is required.

### Git

- Branch: `main`
- Commit: `documentation-only deployment retry commit`
- Push: `successful`

### Notes

The IAM permission is infrastructure state outside the SAM application stack and was applied directly to the existing GitHub deployment role.
## 2026-10-04 - Add optional external links to works

### Request

Allow users to attach an optional link to an uploaded work and safely validate it.

### Changes

- Added an optional HTTP/HTTPS external URL to work creation and public feed responses.
- Persists a normalized URL or `null` when no link is supplied.
- Rejects malformed URLs and non-HTTP schemes through backend DTO validation and a database constraint.
- Intentionally does not request user-supplied destinations during upload, avoiding SSRF and unreliable availability checks.

### Repositories

- `inkfig-main-system`: added API validation, persistence, feed output, migration, and tests.
- `inkfig-user-FE`: adds the optional form field and public link presentation separately.

### Files

- `src/entities/dto/works.py`: adds validated request and nullable response URL fields.
- `src/infrastructure/db/postgres/models/work.py`: maps the nullable URL column.
- `src/infrastructure/repositories/work_repository.py`: stores and returns work links.
- `migrations/20261004_002_add_work_external_url.sql`: adds the nullable constrained column.
- `tests/test_work_service.py`: verifies valid HTTP URLs and rejects unsafe schemes.

### API

- `POST /api/v1/works/uploads`: accepts optional `external_url`; it must be a complete HTTP/HTTPS URL and is limited to 2083 characters.
- `GET /api/v1/works`: each item now includes nullable `external_url`.

### Database

- Migration: `20261004_002_add_work_external_url.sql`
- Adds nullable `works.external_url varchar(2083)` with an HTTP/HTTPS check; existing rows remain `null` and require no backfill. Rollback drops the constraint and column.

### Permissions and scope

- Only authenticated users can submit the link as part of an upload draft.
- Published links are publicly visible with their work.
- Validation is backend- and database-enforced; no new role or permission is introduced.

### Frontend

- No frontend changes in this repository; corresponding changes are in `inkfig-user-FE`.

### Verification

- `[passed] uv run --with-requirements requirements.txt ruff check src tests migrations`
- `[passed] uv run --with-requirements requirements.txt pytest — 11 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests`
- `[passed] python -m migrations.run — migration applied and works schema verified`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`; migration 20261004_002 must run first and is included in the backend workflow.
- No environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `517a8ed`
- Push: `successful`

### Notes

Future link-health monitoring should run asynchronously in a hardened checker that blocks private/reserved IPs, limits redirects and response sizes, and applies strict timeouts.
## 2026-10-04 - Support multiple safe links per work

### Request

Replace the single optional work link with multiple safe links.

### Changes

- Supports up to 10 unique HTTP/HTTPS links per work, each with an optional 120-character label and stable order.
- Migrates existing single links, stores new links transactionally with the draft, and returns ordered links in the public feed.
- Rejects unsafe schemes, duplicates, excessive links, and invalid positions. Automatic destination requests remain intentionally excluded to prevent SSRF.

### Repositories

- `inkfig-main-system`: multi-link DTOs, model, persistence, migration, feed response, and tests.
- `inkfig-user-FE`: multi-link controls and rendering in a paired change.

### Files

- `migrations/20261004_003_create_work_links.sql`: creates and secures `work_links`, backfills old links, and removes the legacy column.
- `src/entities/dto/works.py`: adds link request/response contracts and uniqueness/count validation.
- `src/infrastructure/db/postgres/models/work.py`: maps ordered work links.
- `src/infrastructure/repositories/work_repository.py`: persists and aggregates links.

### API

- `POST /api/v1/works/uploads`: replaces `external_url` with `links`, an optional array of at most 10 `{url,label}` objects.
- `GET /api/v1/works`: replaces `external_url` with an ordered `links` array.

### Database

- Migration: `20261004_003_create_work_links.sql`
- Creates `work_links` with cascading work FK, HTTP/HTTPS check, unique work/URL and work/position constraints, order index, RLS, and service-role grants; backfills existing links before dropping `works.external_url`.

### Permissions and scope

- Authenticated users submit links with owned drafts; published links are public. Backend and database enforce safety and scope.

### Frontend

- No frontend changes in this repository.

### Verification

- `[passed] ruff check`
- `[passed] pytest — 11 tests passed`
- `[passed] mypy — no issues`
- `[passed] migration applied and verified`

### Deployment

- Deploy backend before frontend; migration 003 must run first. No configuration changes.

### Git

- Branch: `main`
- Commit: `eeeeb84`
- Push: `successful`

### Notes

Health monitoring remains future hardened asynchronous work.

## 2026-10-04 - Add authenticated profile feeds

### Request

Support a user profile that lists the authenticated user's published posts and the published posts they liked.

### Changes

- Added authenticated, paginated feeds for the current user's published works and liked works.
- Reused the existing published-work response so profile cards include artwork metadata, ordered links, like counts, and viewer like state.
- Scoped both queries exclusively from the verified backend user ID; clients cannot request another user's profile collections through these endpoints.
- Kept the public feed, uploads, likes, storage, and existing schema unchanged.

### Repositories

- `inkfig-main-system`: added backend-authorized profile feed queries.
- `inkfig-user-FE`: consumes the feeds in the new profile page.

### Files

- `src/interface/api/routes/works.py`: added current-user post and like routes.
- `src/app/services/work_service.py`: added the profile-feed workflow and pagination.
- `src/entities/repositories/works.py`: extended the repository contract with owner and liker scopes.
- `src/infrastructure/repositories/work_repository.py`: added SQL owner and liked-by filtering.
- `tests/test_work_service.py`: verifies authenticated scope selection.

### API

- `GET /api/v1/works/me`: returns up to 50 published works owned by the authenticated user; supports `limit` and `before`; returns 401 for an invalid or missing token.
- `GET /api/v1/works/likes`: returns up to 50 published works liked by the authenticated user; supports `limit` and `before`; returns 401 for an invalid or missing token.
- Existing response fields and public-feed behavior are unchanged.

### Database

No migration required. Queries use the existing `works.owner_user_id` and `work_likes` relationships and existing indexes.

### Permissions and scope

- Both endpoints require a valid InkFig access token.
- Any authenticated user can read only their own posts and likes collections.
- User scope is derived and validated by the backend; no user ID is accepted from the client.

### Frontend

- Paired frontend adds the protected profile route, posts section, and Likes section.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest — 13 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 43 source files`
- `[passed] uv run --with-requirements requirements.txt ruff check src tests`
- `[passed] uv run --with-requirements requirements.txt ruff format src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`.
- No migration or environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `f050498`
- Push: `successful`

### Notes

Profile collections currently return the first 50 items; API cursors are available for future load-more UI.

## 2026-10-05 - Authenticate requests from secure access cookies

### Request

Accept the user backend's HTTP-only access cookie so protected main-system APIs no longer require frontend-managed bearer tokens.

### Changes

- Reads the signed access token from the configured cookie and validates its signature, issuer, type, expiry, and user ID.
- Retains temporary Authorization Bearer compatibility for safe staged deployment and existing sessions.
- Kept all work ownership, likes, profile scope, and public-feed behavior unchanged.

### Repositories

- `inkfig-main-system`: added access-cookie authentication.
- `inkfig-user-system`: issues the shared access cookie.
- `inkfig-user-FE`: sends credentialed requests.

### Files

- `src/interface/dependencies/authentication.py`: resolves cookie authentication with bearer fallback.
- `src/infrastructure/config/settings.py`, `.env.example`, `template.yaml`: configure the access-cookie name.
- `tests/test_cookie_authentication.py`: proves a valid signed cookie identifies its user.

### API

- All existing protected `/api/v1/works/*` endpoints accept `inkfig_access` as an HTTP-only cookie.
- Invalid or expired cookies return 401 and missing credentials retain existing authentication behavior.

### Database

No migration required.

### Permissions and scope

- Existing backend authorization and authenticated-user scope remain authoritative.
- Cookie contents are signature- and expiry-validated before the user ID is trusted.

### Frontend

- No UI changes in this repository.

### Verification

- `[passed] pytest — 14 tests passed`
- `[passed] mypy src tests — no issues in 44 source files`
- `[passed] ruff check src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` before the cookie-only user API response and frontend.
- No migration, new secret, or external configuration is required.

### Git

- Branch: `main`
- Commit: `911498d`
- Push: `successful`

### Notes

Bearer fallback prevents disruption to existing sessions during the staged rollout and can be removed in a later hardening ticket.
## 2026-10-05 - Enforce work permissions

### Request

Protect every interactive work endpoint with the new role-permission model.

### Changes

- Parses signed role and permission claims into an authenticated principal.
- Requires explicit permissions for uploads, publishing, likes, and private profile feeds.
- Leaves the public artwork feed and work types public.

### Repositories

- `inkfig-main-system`: enforces work permissions.
- `inkfig-user-system`: issues the signed claims.
- `inkfig-user-FE`: hides and guards restricted actions.

### Files

- `src/interface/dependencies/authentication.py`: adds principal parsing and permission dependencies.
- `src/interface/api/routes/works.py`: declares permission requirements.

### API

- `POST /api/v1/works/uploads` and `POST /api/v1/works/{work_id}/publish`: require works.upload.
- `PUT|DELETE /api/v1/works/{work_id}/like`: require works.like.
- `GET /api/v1/works/me` and `GET /api/v1/works/likes`: require profile.read_own.
- Missing authentication returns 401; missing permission returns 403.

### Database

No migration required.

### Permissions and scope

- Viewer has no protected work permissions.
- User, supervisor, admin, and system-administrator retain current work abilities.
- Authorization is validated by this backend from signed claims.

### Frontend

No frontend changes in this repository.

### Verification

- `[passed] py -3.12 -m pytest -q - 14 tests passed`
- `[passed] py -3.12 -m mypy src tests - 44 files`
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy after user-system migration 007 and backend deployment.
- No environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `a0ac6c9`
- Push: `successful`

### Notes

Public homepage reads remain intentionally unauthenticated.

## 2026-10-05 - Persist authenticated artwork saves

### Request

Allow registered users to save published artwork and expose their saved collection on their profile.

### Changes

- Added persistent per-user artwork saves with idempotent save and unsave operations.
- Added viewer-specific saved state to every published-work response.
- Added an authenticated saved-artwork feed scoped exclusively from the verified current user.
- Protected save mutations with the new works.save permission and saved-feed reads with profile.read_own.
- Added service coverage for authenticated saved-feed scope and save delegation.

### Repositories

- inkfig-main-system: save persistence, API endpoints, saved feed, migration, authorization, and tests.
- inkfig-user-system: grants works.save to registered interactive roles in a paired migration.
- inkfig-user-FE: adds the bookmark interaction and Saved profile tab.

### Files

- migrations/20261005_004_create_work_saves.sql: creates the secured work_saves relation and user/date index.
- src/infrastructure/db/postgres/models/work.py: maps saved works.
- src/entities/dto/works.py: exposes saved_by_me.
- src/entities/repositories/works.py: extends save and saved-feed contracts.
- src/infrastructure/repositories/work_repository.py: persists saves and queries viewer/profile state.
- src/app/services/work_service.py: adds saved profile scope and save workflow.
- src/interface/api/routes/works.py: adds saved-feed and save/unsave routes with backend permissions.
- tests/test_work_service.py: covers save scope and service delegation.
- AGENT_FEATURE_LOG.md: records this ticket.

### API

- GET /api/v1/works/saves returns the authenticated user's saved published works.
- PUT /api/v1/works/{work_id}/save saves a published work.
- DELETE /api/v1/works/{work_id}/save removes it from saved works.
- Published work responses now include saved_by_me.
- Save mutations return 401 without authentication, 403 without works.save, and 404 for unavailable works.

### Database

- Migration: migrations/20261005_004_create_work_saves.sql.
- Creates work_saves with a cascading work foreign key, unique work/user primary key, created timestamp, user/date index, RLS, and service-role-only access.

### Permissions and scope

- Save mutations require a signed works.save claim.
- Saved-feed reads require profile.read_own.
- User identity always comes from the verified backend principal; no client-supplied user ID is accepted.
- Only published works can be saved.

### Frontend

No frontend files changed in this repository. Paired frontend work adds the bookmark and Saved tab.

### Verification

- [passed] git diff --check
- [passed] focused static review of migration, route permissions, service scope, repository parameters, and response mapping.
- [not run] pytest, mypy, Ruff, and compileall - no usable Python runtime or project runner is installed in this session.

### Deployment

- First apply inkfig-user-system migration 20261005_008_add_work_save_permission.sql and deploy the user system.
- Then apply migrations/20261005_004_create_work_saves.sql and deploy inkfig-main-system.
- Deploy inkfig-user-FE last.
- No new environment variables or secrets are required.

### Git

- Branch: main
- Commit: this ticket's focused commit.
- Push: pushed directly to origin/main after synchronization.

### Notes

Existing sessions must refresh or sign in again after the permission migration so their signed access claim includes works.save.
## 2026-10-06 - Optimize artwork database indexes

### Request

Review and optimize the database and indexing for current InkFig workloads, and make query/index review a standard consideration for future database work.

### Changes

- Replaced the mismatched published-work index on `published_at` with partial composite indexes matching the actual `created_at` feed order.
- Added workload-specific published-feed indexes for the global, work-type, and owner views.
- Added user-first composite indexes for liked and saved profile collections.
- Removed the redundant work-link ordering index because the existing unique `(work_id, position)` constraint already provides the same B-tree prefix.
- Changed optional feed filters from nullable `OR` expressions to fixed conditional predicates and joins so PostgreSQL can select the relevant partial/composite index.
- Added a stable `work_id` ordering tie-breaker while preserving the existing timestamp cursor API.
- Left authorization, storage, API contracts, and frontend behavior unchanged.

### Repositories

- `inkfig-main-system`: optimized artwork query construction and database indexes.

### Files

- `src/infrastructure/repositories/work_repository.py`: made feed SQL index-friendly and deterministically ordered.
- `migrations/20261006_005_optimize_query_indexes.sql`: replaced redundant/mismatched indexes and added workload-aligned indexes.
- `tests/test_query_indexes.py`: added regression coverage for index definitions and query shape.

### API

No API changes.

### Database

- Migration: `20261006_005_optimize_query_indexes.sql`
- Replaces the old public-feed and owner indexes with partial published-work indexes on global `(created_at DESC, work_id DESC)`, type `(type_id, created_at DESC, work_id DESC)`, and owner `(owner_user_id, created_at DESC, work_id DESC)` access paths.
- Adds `(user_id, created_at DESC, work_id DESC)` indexes to likes and saves, and removes the redundant work-link ordering index.
- No data backfill, constraint, default, or foreign-key changes are required. Rollback can drop the new indexes and recreate the prior indexes, with no data loss.

### Permissions and scope

- Public published-feed reads remain available without a permission.
- `profile.read_own` remains required for owned, liked, and saved profile feeds.
- `works.like` and `works.save` remain required for their respective mutations.
- Role and user scope rules are unchanged and continue to be validated by the backend.

### Frontend

No frontend changes.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q — 19 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 45 files`
- `[passed] uv run --with-requirements requirements.txt ruff check src/infrastructure/repositories/work_repository.py tests/test_query_indexes.py`
- `[passed] uv run --with-requirements requirements.txt python -m compileall -q src tests`
- `[passed] python -m migrations.run — migration applied and works tables/storage verified`
- `[passed] live pg_indexes query — all artwork indexes and partial predicates verified on Supabase`
- `[failed] uv run --with-requirements requirements.txt ruff check src tests — unrelated pre-existing findings in src/interface/dependencies/authentication.py`

### Deployment

- Deploy `inkfig-main-system`.
- Run `20261006_005_optimize_query_indexes.sql` before deploying the application; it has already been applied to the configured Supabase database.
- No environment-variable or configuration changes.

### Git

- Branch: `main`
- Commit: `bfdae62`
- Push: `successful`

### Notes

- Future database tickets must compare query predicates, join direction, ordering, and pagination with existing indexes and avoid redundant or low-selectivity indexes.
- Query plans should be reassessed using production-scale statistics as table cardinality grows; small tables may correctly use sequential scans despite having suitable indexes.
## 2026-10-06 - Expose public profile artwork feeds

### Request

Allow a profile page to display all published artworks owned by the selected InkFig account.

### Changes

- Added a public profile artwork use case that scopes the feed to the requested owner while preserving viewer-specific like and save state.
- Reused the optimized published-owner feed query and indexes.
- Left upload, ownership mutation, likes, saves, and private profile collections unchanged.

### Repositories

- `inkfig-main-system`: exposes published work for a selected owner.
- `inkfig-user-system`: owns profile data and follow relationships.
- `inkfig-user-FE`: consumes the profile artwork endpoint.

### Files

- `src/app/services/work_service.py`: adds the public profile feed workflow.
- `src/interface/api/routes/works.py`: adds the owner-specific published-work route.
- `tests/test_work_service.py`: verifies separation of requested owner and current viewer scope.

### API

- `GET /api/v1/works/users/{user_id}`: returns published artworks owned by `user_id`; accepts the existing `limit` and `before` pagination fields, includes viewer-specific like/save state when authenticated, and remains publicly readable.

### Database

- No migration required.
- The endpoint uses the existing partial `works_published_owner_feed_idx` plus primary/relationship indexes.

### Permissions and scope

- No permission is required to view published artwork.
- Optional authentication only personalizes like and save state.
- The backend fixes owner scope from the path UUID and never accepts owner scope from response or client state.

### Frontend

No frontend changes in this repository. The coordinated profile UI is in `inkfig-user-FE`.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q — 20 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 45 files`
- `[passed] ruff check on all changed main-backend files`
- `[passed] python -m compileall -q src tests`

### Deployment

- Deploy `inkfig-main-system`.
- No migrations or configuration changes are required.

### Git

- Branch: `main`
- Commit: `f153b54`
- Push: `successful`

### Notes

None

## 2026-10-06 - Hide inactive-account artwork and activity

Updated published-work queries to require an active owner and to count likes only from active accounts. This keeps deactivated or administrator-suspended profiles, works, and like activity out of public and profile feeds while retaining data for safe reactivation.

- No API or migration in this repository.
- Verification: `git diff --check` passed.
- Deployment: deploy after the user-system account-status migration.
- Branch: `feature/account-status-lifecycle`; push to `main` after synchronization.
## 2026-10-06 - Voyage semantic artwork search

### Request

Add Voyage AI to let visitors find artworks from English or Arabic text descriptions, with production-safe Lambda permissions and optimized vector storage.

### Changes

- Added a clean-architecture Voyage multimodal embedding adapter backed by AWS Secrets Manager.
- Embedded newly published artwork images without making publication fail when Voyage is temporarily unavailable.
- Added bounded automatic catch-up indexing for previously published artworks and missed embeddings.
- Added cosine-similarity artwork search with optional work-type filtering and active-account enforcement.
- Kept existing feeds, likes, saves, uploads, and profile behavior unchanged.

### Repositories

- `inkfig-main-system`: added semantic embedding, retrieval, persistence, API, migration, and Lambda configuration.
- `inkfig-user-FE`: consumes the search API in the public home search experience.

### Files

- `src/infrastructure/integrations/voyage_embeddings.py`: calls Voyage multimodal embeddings and loads its API key securely.
- `src/app/services/work_service.py`: orchestrates indexing, bounded catch-up, and semantic search.
- `src/infrastructure/repositories/work_repository.py`: persists vectors and performs indexed cosine search.
- `src/interface/api/routes/works.py`: exposes the semantic search endpoint.
- `migrations/20261006_006_add_work_embeddings.sql`: enables pgvector and creates vector storage and an HNSW index.
- `template.yaml`: configures Voyage and grants narrowly scoped Secrets Manager access.
- `tests/test_work_service.py`: verifies search, catch-up, and failure resilience.
- `tests/test_voyage_embeddings.py`: verifies Voyage request semantics.

### API

- `GET /api/v1/works/search`: accepts required `query` (2-500 characters), optional `type_code`, and `limit` (1-50); returns ranked published works, preserves optional viewer like/save state, and returns 503 when semantic search is unavailable.

### Database

- Migration: `20261006_006_add_work_embeddings.sql`
- Enables the Supabase `vector` extension, creates `work_embeddings` with a cascading work foreign key, 1024-dimensional embeddings, model metadata and timestamps, and adds an HNSW cosine index. Rollback requires dropping `work_embeddings`; the shared vector extension should only be dropped after confirming no other feature uses it.

### Permissions and scope

- Public viewers and all roles may search published works; authentication remains optional and only enriches like/save state.
- Only published works owned by active accounts are returned.
- Existing `works.upload` backend authorization still controls publication; no new application permission is required.
- Lambda can only read Secrets Manager resources matching `inkfig/main/voyage-*`; backend query scope is enforced by SQL.

### Frontend

- The existing localized home search bar now sends debounced semantic searches after two characters.
- Category filters are passed to semantic search, and localized loading, empty, and unavailable states are shown.
- Existing responsive artwork cards, navigation, detail modal, likes, saves, RTL/LTR behavior, and feed behavior remain unchanged.

### Verification

- `[passed] py -3.12 -m pytest` (25 tests)
- `[passed] py -3.12 -m mypy src`
- `[passed] sam build --cached`
- `[passed] sam validate --lint` (template valid; local SAM telemetry metadata emitted a filesystem warning)
- `[passed] npm.cmd test` (43 tests in `inkfig-user-FE`)
- `[passed] npm.cmd run build` in `inkfig-user-FE`

### Deployment

- Deploy `inkfig-main-system` first; its workflow must run migration `20261006_006_add_work_embeddings.sql` before Lambda deployment.
- Deploy `inkfig-user-FE` after the backend is healthy.
- AWS Secrets Manager secret `inkfig/main/voyage` must contain `VOYAGE_API_KEY`; no Voyage key is exposed to the frontend or GitHub variables.

### Git

- Branch: `main`
- Commit: `6c9f896`
- Push: `successful`

### Notes

The first searches may take longer while at most five missing artwork embeddings are generated per request. Failed items remain eligible for a later retry, and normal publication remains available during Voyage outages.
## 2026-10-06 - Restore Voyage deployment pipeline

### Request

Complete and deploy the Voyage semantic artwork search integration.

### Changes

- Made the optional `boto3` import type annotation portable across local development and GitHub Actions environments.
- Left application behavior, API behavior, database schema, and authorization unchanged.

### Repositories

- `inkfig-main-system`: fixed CI type-check compatibility.

### Files

- `src/infrastructure/integrations/voyage_embeddings.py`: accepts both missing-module and untyped-module MyPy classifications.

### API

No API changes.

### Database

- Migration: `20261006_006_add_work_embeddings.sql`
- No additional migration required; the Voyage migration was successfully applied by the restored deployment.

### Permissions and scope

- No permission changes.
- Existing public-search and active-account scope remains validated by the backend.

### Frontend

No frontend changes.

### Verification

- `[passed] py -3.12 -m pytest` (25 tests)
- `[passed] py -3.12 -m mypy src tests` (47 source files)
- `[passed] GitHub Actions run 37504256584`
- `[passed] AWS CloudFormation stack status UPDATE_COMPLETE`
- `[passed] GET https://main-api.inkfig-hu.com/health`
- `[failed] GET /api/v1/works/search?query=moon — Voyage returned HTTP 429 because the organization has no payment method and is limited to 3 requests per minute`

### Deployment

- `inkfig-main-system` deployed successfully, including the pgvector migration and Lambda policy.
- Add a payment method to the Voyage organization to unlock standard rate limits; Voyage states the free Voyage 3 token allowance remains available afterward.

### Git

- Branch: `main`
- Commit: `4f59663`
- Push: `successful`

### Notes

The stored key, Secrets Manager secret, Lambda configuration, CloudFormation deployment, and database migration are correct. Reliable production search is externally blocked only by the Voyage account's reduced 3-RPM limit.
## 2026-10-06 - Delete all existing artworks

### Request

Permanently remove all previously uploaded artwork records so future works enter the Voyage embedding process from publication.

### Changes

- Added a one-time migration that deletes every row from the parent `works` table.
- Relied on existing cascading foreign keys to delete associated links, likes, saves, and embeddings atomically.
- Intentionally left users, work types, permissions, and Supabase Storage objects unchanged.

### Repositories

- `inkfig-main-system`: added the destructive artwork-data reset migration and regression test.

### Files

- `migrations/20261006_007_delete_existing_works.sql`: deletes all existing artwork database records.
- `tests/test_delete_existing_works_migration.py`: verifies the reset targets only the parent works table and does not directly manipulate Storage metadata.

### API

No API changes.

### Database

- Migration: `20261006_007_delete_existing_works.sql`
- Deletes all rows from `public.works`; foreign-key cascades delete matching `work_links`, `work_likes`, `work_saves`, and `work_embeddings` rows. This data deletion has no automatic rollback or backfill. Users and canonical work types remain intact.

### Permissions and scope

- No application permissions or role access changed.
- This deployment-time migration affects artworks belonging to every user and bypasses application endpoints by design.
- Normal backend authorization remains unchanged after the reset.

### Frontend

No frontend changes. Existing feeds and profiles display their normal empty states after the migration.

### Verification

- `[passed] py -3.12 -m pytest` (26 tests)
- `[passed] py -3.12 -m mypy src tests` (48 source files)
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system`; GitHub Actions must apply `20261006_007_delete_existing_works.sql` before deploying Lambda.
- No environment-variable changes are required.
- Supabase Storage image objects are not deleted and may be purged separately through the Storage API if required.

### Git

- Branch: `main`
- Commit: `60175da`
- Push: `successful`

### Notes

The database deletion is permanent. Preserving Storage objects avoids unsupported direct SQL deletion from Supabase Storage but leaves orphaned image files until an explicit Storage cleanup is performed.
## 2026-10-07 - Reset artworks after semantic-search testing

### Request

Permanently remove every current artwork after testing the Voyage text-to-image search workflow.

### Changes

- Added a second one-time migration that deletes every current row from `public.works`.
- Existing cascading foreign keys delete associated links, likes, saves, and embeddings atomically.
- Intentionally left users, work types, permissions, and Supabase Storage objects unchanged.

### Repositories

- `inkfig-main-system`: added and tested the second destructive artwork reset migration.

### Files

- `migrations/20261007_008_delete_existing_works.sql`: deletes all current artwork database records.
- `tests/test_delete_existing_works_migration.py`: verifies both reset migrations use the cascading parent delete and do not directly modify Storage metadata.

### API

No API changes.

### Database

- Migration: `20261007_008_delete_existing_works.sql`
- Deletes all `public.works` rows and cascades to `work_links`, `work_likes`, `work_saves`, and `work_embeddings`. The deletion has no automatic rollback. User accounts and canonical work types remain unchanged.

### Permissions and scope

- No roles or permissions changed.
- The deployment migration affects artworks owned by every account and intentionally runs outside application endpoint authorization.
- Normal backend authorization remains enforced after the reset.

### Frontend

No frontend changes. Artwork feeds and profiles use their existing empty states after deletion.

### Verification

- `[passed] py -3.12 -m pytest` (26 tests)
- `[passed] py -3.12 -m mypy src tests` (48 source files)
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system`; GitHub Actions must apply `20261007_008_delete_existing_works.sql` before Lambda deployment.
- No environment-variable changes are required.
- Supabase Storage objects are intentionally retained and require separate Storage API cleanup if physical deletion is later requested.

### Git

- Branch: `main`
- Commit: `bed6735`
- Push: `successful`

### Notes

This migration permanently deletes the current artwork database data. Preserved Storage objects become orphaned and are not visible through InkFig feeds.
## 2026-10-07 - Support oversized artwork embeddings and relevant search results

### Request

Fix semantic search so high-resolution artworks are embedded, unrelated nearest-neighbor results are excluded, reset existing works, and prepare the system for live two-image testing.

### Changes

- Downloads each published artwork into Lambda memory and creates an aspect-ratio-preserving JPEG derivative capped at two million pixels for Voyage.
- Keeps the original Supabase Storage object and its displayed resolution unchanged.
- Added a configurable cosine-similarity threshold so weak matches are excluded instead of always returning the nearest indexed artwork.
- Added structured exception logging for publication and catch-up embedding failures.
- Added a one-time reset migration that deleted the current works and their cascading related records before retesting.

### Repositories

- `inkfig-main-system`: added safe image preprocessing, relevance filtering, diagnostics, reset migration, and tests.

### Files

- `src/infrastructure/integrations/voyage_embeddings.py`: fetches, safely validates, resizes, and encodes artwork derivatives for Voyage.
- `src/infrastructure/repositories/work_repository.py`: applies the minimum semantic similarity filter.
- `src/app/services/work_service.py`: passes search thresholds and logs embedding failures.
- `src/infrastructure/config/settings.py`: adds the semantic similarity configuration.
- `migrations/20261007_009_delete_works_before_search_retest.sql`: removes current artwork data before controlled retesting.
- `tests/test_voyage_embeddings.py`: verifies in-memory resizing and aspect-ratio preservation.
- `tests/test_query_indexes.py`: verifies semantic relevance filtering.

### API

- `GET /api/v1/works/search`: response shape is unchanged; results below `VOYAGE_MIN_SIMILARITY` are now omitted.

### Database

- Migration: `20261007_009_delete_works_before_search_retest.sql`
- Deletes all `public.works` rows and cascades to links, likes, saves, and embeddings. The deletion has no automatic rollback. No schema or index changes were required.

### Permissions and scope

- No roles or permissions changed.
- Search remains public and only returns published works owned by active accounts.
- Upload and publication remain protected by `works.upload`, with authorization validated by the backend.

### Frontend

No frontend changes. Original images continue to be displayed from Supabase Storage at their uploaded resolution.

### Verification

- `[passed] py -3.12 -m pytest` (28 tests)
- `[passed] py -3.12 -m mypy src tests` (48 source files)
- `[passed] sam build --cached`
- `[passed] GitHub Actions run 37546735220`
- `[passed] GET /api/v1/works returned an empty feed after migration`
- `[passed] close-up-full-bloom-flower.jpg confirmed as 3328x4864 (16,187,392 pixels), reproducing the previous Voyage limit failure`
- `[passed] images (1).jfif confirmed as 415x740 (307,100 pixels)`
- `[not run] authenticated browser uploads and UI searches — browser-control runtime is unavailable in this session`

### Deployment

- `inkfig-main-system` and migration `20261007_009_delete_works_before_search_retest.sql` deployed successfully.
- Added Lambda dependency `Pillow==11.3.0`.
- Added `VOYAGE_MIN_SIMILARITY=0.20`; no secret changes are required.

### Git

- Branch: `main`
- Commit: `7ed81e9`
- Push: `successful`

### Notes

The two requested files are available under `C:\Users\mohaamad\Downloads`. Live authenticated upload verification remains pending until browser control is available or the user uploads both files manually.

## 2026-10-07 - Expose semantic search ranking

### Request

Return each semantic-search result's rank to the frontend so artworks are displayed from most to least similar.

### Changes

- Added a search-specific response contract containing a one-based `search_rank` and cosine `similarity_score` for every returned artwork.
- Preserved database ordering by ascending cosine distance, then assigned ranks in that exact order.
- Kept ordinary home, profile, liked, and saved feed response contracts unchanged.
- Preserved the existing similarity threshold, category filter, active-owner scope, viewer-specific like/save state, and Voyage workflow.
- Intentionally left the existing local `samconfig.toml` modification unchanged.

### Repositories

- `inkfig-main-system`: exposes explicit semantic rank and similarity metadata.
- `inkfig-user-FE`: consumes rank metadata and renders search results in rank order.

### Files

- `src/entities/dto/works.py`: adds search-only artwork and feed response DTOs.
- `src/entities/repositories/works.py`: updates the semantic-search repository contract.
- `src/app/services/work_service.py`: returns the search-specific feed contract.
- `src/infrastructure/repositories/work_repository.py`: selects cosine similarity and assigns deterministic one-based ranks.
- `src/interface/api/routes/works.py`: publishes the search-specific response model.
- `tests/test_query_indexes.py`: verifies similarity selection and rank assignment.
- `tests/test_work_service.py`: verifies search ranking metadata validation.

### API

- `GET /api/v1/works/search`: each item now includes required `search_rank` and `similarity_score`; results remain ordered from highest to lowest similarity and weak results remain excluded by `VOYAGE_MIN_SIMILARITY`.
- Request fields, category filtering, limits, public access, and 503 behavior are unchanged.

### Database

No migration required. Similarity and rank are calculated at query/request time from existing pgvector embeddings; no stored schema, indexes, constraints, defaults, foreign keys, or backfill behavior changed.

### Permissions and scope

- No permission is required for public semantic search.
- Authenticated viewers continue receiving only their own like/save state.
- Only published works owned by active accounts are eligible.
- Authorization and data scope remain validated by the backend.

### Frontend

- The frontend receives `search_rank` and `similarity_score` and defensively sorts semantic results by ascending rank.
- No visual rank label, route, navigation, layout, localization, loading, empty, responsive, or error-state changes were requested or added.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 29 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests - no issues in 48 source files`
- `[passed] focused ruff check - all checks passed`
- `[passed] git diff --check`
- `[passed] frontend npm.cmd test - 44 passed`
- `[passed] frontend npm.cmd run build - TypeScript and Vite production build succeeded`

### Deployment

- Deploy `inkfig-main-system`, then deploy `inkfig-user-FE`.
- No migration must run before deployment.
- No environment-variable, secret, or configuration changes are required.

### Git

- Branch: `main`
- Commit: `328bcee`
- Push: `successful`

### Notes

`similarity_score` is cosine similarity, not a probability or confidence percentage.

## 2026-10-07 - Paginate semantic artwork search

### Request

Complete pagination across InkFig so artwork feeds and ranked semantic-search results can load beyond their first page.

### Changes

- Added a bounded continuation cursor to semantic search and returns `next_cursor` when more ranked results exist.
- Fetches one extra search row to determine whether another page exists without issuing a separate count query.
- Preserves continuous one-based search ranks across pages by starting each page at its cursor offset.
- Kept existing timestamp cursor pagination for public, profile, liked, and saved feeds unchanged.
- Preserved similarity thresholds, category filtering, active-account scope, and viewer-specific interaction state.
- Intentionally left the existing local `samconfig.toml` modification unchanged.

### Repositories

- `inkfig-main-system`: adds ranked semantic-search continuation support.
- `inkfig-user-FE`: consumes pagination for home, search, profile posts, likes, and saved works.

### Files

- `src/entities/dto/works.py`: adds `next_cursor` to semantic-search feeds.
- `src/entities/repositories/works.py`: adds repository offset input.
- `src/app/services/work_service.py`: computes the next search cursor using a limit-plus-one query.
- `src/infrastructure/repositories/work_repository.py`: applies the bounded offset and continuous rank numbering.
- `src/interface/api/routes/works.py`: accepts the validated search cursor.
- `tests/test_query_indexes.py`: verifies pagination query and rank behavior.
- `tests/test_work_service.py`: verifies continuation cursors, page size, and continuous ranks.

### API

- `GET /api/v1/works/search`: accepts optional `cursor` from 0 through 10,000 and returns nullable integer `next_cursor`; `limit`, `query`, `type_code`, ranking metadata, validation, public access, thresholding, and 503 behavior remain.
- `GET /api/v1/works`, `/me`, `/likes`, `/saves`, and `/users/{user_id}` retain their existing `before` timestamp cursor and nullable `next_cursor` behavior.

### Database

No migration required. Pagination uses existing ordering, pgvector search, feed indexes, and runtime query parameters. No schema, constraint, default, foreign-key, index, backfill, or rollback change is required.

### Permissions and scope

- Public feed and search pagination require no permission.
- Profile likes and saves still require `profile.read_own`.
- Search continues to return only published works owned by active accounts.
- Viewer like/save personalization and all authorization remain backend-validated.

### Frontend

- Home feed, semantic search, profile posts, likes, and saved works now consume continuation cursors through a localized Load more flow.
- Search ranking remains continuous and ordered across pages.
- Duplicate artwork IDs are excluded while appending pages.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 30 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests - no issues in 48 source files`
- `[passed] focused ruff check - all checks passed`
- `[passed] git diff --check`
- `[passed] frontend npm.cmd test - 44 passed`
- `[passed] frontend npm.cmd run build - TypeScript and Vite production build succeeded`

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`.
- No migrations must run before deployment.
- No environment-variable, secret, or configuration changes are required.

### Git

- Branch: `main`
- Commit: `c5e8c03`
- Push: `successful`

### Notes

Semantic-search continuation is bounded to 10,000 ranked results to prevent unbounded database offsets.
## 2026-10-07 - Scope artwork feeds and semantic search to a selected account

### Request

When an account is selected through the frontend `@` search, return that user's matching works; when no artwork words accompany the selected account, return all public works for that user.

### Changes

- Added an optional immutable owner-user filter to the public artwork feed.
- Added the same owner filter to ranked semantic image search.
- Preserved category filtering, pagination, active-account scope, published-only scope, ranking, and viewer interaction state.
- Left uploads, likes, saves, embeddings, thresholds, and existing profile-feed routes unchanged.

### Repositories

- `inkfig-main-system`: owner-scoped public feed and semantic-search API behavior.
- `inkfig-user-system`: supplies privacy-safe account IDs from live account discovery.
- `inkfig-user-FE`: chooses between owner-only feed and owner-scoped semantic search.

### Files

- `src/entities/repositories/works.py`: extends semantic-search persistence with an optional owner ID.
- `src/app/services/work_service.py`: propagates owner scope through feed and search use cases.
- `src/infrastructure/repositories/work_repository.py`: applies a parameterized owner predicate to semantic search.
- `src/interface/api/routes/works.py`: accepts `owner_user_id` on public feed and search endpoints.
- `tests/test_work_service.py`: verifies owner scope for both paths.

### API

- `GET /api/v1/works`: accepts optional UUID `owner_user_id`; returns only published works from that active owner, with existing `type_code`, `before`, `limit`, and interaction behavior unchanged.
- `GET /api/v1/works/search`: accepts optional UUID `owner_user_id`; ranks only that active owner's published embedded works against the existing required `query`, with existing `type_code`, `cursor`, `limit`, threshold, ranking fields, validation, and 503 behavior unchanged.

### Database

- Migration: `No migration required`
- Owner filtering uses the existing owner/feed indexes and embedding structures. No schema, default, constraint, foreign-key, backfill, or rollback change is required.

### Permissions and scope

- No authenticated permission is required for public feed or search access.
- Viewer, user, supervisor, admin, and system-administrator clients receive published works belonging to active accounts only.
- The backend validates the UUID and enforces owner, publication, account-status, category, threshold, and pagination scope.

### Frontend

- `@Selected Account` with no other words uses the owner-filtered chronological feed.
- Artwork text combined with a selected account uses owner-filtered semantic ranking.
- Existing cards, category filters, responsive masonry layout, pagination, and interaction controls remain unchanged.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 32 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests - no issues in 48 source files`
- `[passed] focused ruff check for all changed main-backend files`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` after `inkfig-user-system` and before `inkfig-user-FE`.
- No migrations must run for this repository.
- No environment-variable or configuration changes are required.

### Git

- Branch: `main`
- Commit: `c1fd31d`
- Push: `successful`

### Notes

The existing local `samconfig.toml` modification was intentionally left unchanged and excluded from the commit.
## 2026-10-07 - Add owner-controlled work editing and complete deletion

### Request

Allow users to edit and delete only their own posts, prohibit image replacement during editing, and remove every post-owned database and storage resource when deleting.

### Changes

- Added owner-scoped metadata editing for title, description, category, and up to ten unique HTTP/HTTPS links.
- Deliberately excluded image, storage path, MIME type, and file size from the update contract.
- Added owner-scoped deletion that deletes and verifies the Supabase object before removing the work row.
- Relies on existing database cascades to remove the work's links, likes, saves, and Voyage embedding with the work row.
- Added validation for nonblank normalized titles and focused ownership/deletion-order tests.

### Repositories

- `inkfig-main-system`: backend contracts, authorization, persistence, storage deletion, tests, and this log.
- `inkfig-user-FE`: owner controls, editor, deletion confirmation, profile layout, and localization.
- `inkfig-user-system`: no changes required.

### API

- `PATCH /api/v1/works/{work_id}` updates owner-controlled metadata only.
- `DELETE /api/v1/works/{work_id}` permanently deletes the authenticated owner's work.
- Both endpoints require `works.upload`; repository predicates independently enforce `owner_user_id`.

### Database

- No migration required.
- Existing `ON DELETE CASCADE` constraints remove `work_links`, `work_likes`, `work_saves`, and `work_embeddings` records.

### Permissions and SnapStart

- Only the authenticated owner can mutate a work; non-owned and missing works return the same not-found response.
- Storage clients remain request-scoped and retain AWS Lambda SnapStart compatibility.

### Verification

- `[passed] git diff --check`
- `[passed] cascade audit` - every work-owned relational table uses `ON DELETE CASCADE`.
- `[added] service tests` - cover metadata-only editing, storage-before-database deletion, and non-owner rejection.
- `[not run] pytest and mypy` - no usable Python runtime or repository virtual environment is installed on this machine; GitHub Actions will run both.

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`.
- No migration, secret, or environment-variable changes are required.

### Git

- Branch: `feature/owner-work-management`
- Commit, rebase, push, merge, and main push: pending final synchronization.

## 2026-10-07 - Repair previous artwork resets by deleting orphaned storage objects

### Request

Update the previous migrations that deleted all artworks so the corresponding files are also removed from Supabase Storage rather than deleting only database rows and links.

### Changes

- Added a tracked Python storage-migration mechanism alongside existing SQL migrations.
- Added an idempotent cleanup that finds objects in the exact `works` bucket whose paths are no longer referenced by any current `works.storage_path`.
- Deletes orphaned objects through the authenticated Supabase Storage API in bounded batches.
- Validates the configured bucket, rejects unsafe paths, verifies no orphaned objects remain, and records the migration only after successful completion.
- Deleted 13 orphaned artwork files left by the three earlier database-only reset migrations.
- Preserved every storage object referenced by a current artwork row and left current artwork records unchanged.
- Intentionally left the existing local `samconfig.toml` modification unchanged.

### Repositories

- `inkfig-main-system`: storage migration runner, orphan cleanup, verification tests, and applied cleanup.

### Files

- `migrations/run.py`: discovers ordered `*_storage.py` migrations, loads their async `apply` function, and records them in `schema_migrations` after success.
- `migrations/20261007_010_delete_orphaned_work_storage.py`: validates and removes only unreferenced objects from the Supabase works bucket.
- `tests/test_delete_existing_works_migration.py`: verifies discovery, database-reference exclusion, exact-bucket protection, API deletion, and post-delete verification.

### API

No API changes.

### Database

- Migration: `20261007_010_delete_orphaned_work_storage.py`
- Reads `storage.objects` and `public.works.storage_path` to identify orphaned files, deletes exact paths through Supabase Storage, verifies zero remaining orphans, and records the filename in `public.schema_migrations`.
- No schema, default, constraint, index, foreign-key, or application-row change is required.
- No automatic rollback is possible for deleted binary objects; database-referenced current artwork files are excluded before deletion.

### Permissions and scope

- Requires backend-only `SUPABASE_SECRET_KEY`, `SUPABASE_URL`, `DATABASE_URL`, and exact `WORKS_BUCKET=works` configuration.
- No end-user role or permission can invoke this migration through an API.
- Scope is enforced by exact bucket validation, database reference exclusion, path validation, bounded batching, and post-delete verification.
- Backend migration execution controls authorization; secrets remain server-side.

### Frontend

No frontend changes.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 33 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests migrations - no issues in 50 source files`
- `[passed] focused ruff check - all changed migration and test files pass`
- `[passed] uv run --env-file .env --with-requirements requirements.txt python -m migrations.run - deleted 13 orphaned objects and applied migration`
- `[passed] migration post-check - works tables and public storage bucket verified`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` so future environments run Python storage migrations.
- Migration `20261007_010_delete_orphaned_work_storage.py` must run with database and Supabase service credentials; it has already been applied to the configured Supabase project.
- No new environment variables are required.

### Git

- Branch: `main`
- Commit: `d61bf30`
- Push: `successful`

### Notes

Future destructive artwork-reset migrations can use the tracked storage-migration mechanism. External file deletion is irreversible, so each cleanup must explicitly document scope and rollback limitations.

## 2026-10-07 - Add audited administrator work deletion

### Request

Allow system administrators and administrators to delete any work only after entering a deletion reason.

### Changes

- Added a moderation deletion workflow protected by `works.delete_any`.
- Requires a normalized reason between 10 and 1000 characters.
- Deletes the work's Supabase Storage object and its database record.
- Persists an audit snapshot containing the work, owner, moderator, reason, storage metadata, and deletion time.
- Left the existing owner-delete workflow unchanged.

### Repositories

- `inkfig-main-system`: implemented the endpoint, service, repository transaction, audit model, migration, and tests.
- `inkfig-user-system`: added the administrator permission.
- `inkfig-user-FE`: added the permission-gated deletion experience.

### Files

- `src/entities/dto/works.py`: added validated moderation request and target DTOs.
- `src/entities/repositories/works.py`: added moderation repository operations.
- `src/app/services/work_service.py`: added storage and database deletion orchestration.
- `src/infrastructure/db/postgres/models/work.py`: added the deletion-audit model.
- `src/infrastructure/repositories/work_repository.py`: snapshots, audits, and deletes the work transactionally.
- `src/interface/api/routes/works.py`: added the protected moderation endpoint.
- `migrations/20261007_011_create_work_deletion_audits.sql`: creates the audit table, indexes, and RLS policy.
- `tests/test_work_service.py`: covers moderation deletion and reason validation.

### API

- `DELETE /api/v1/works/{work_id}/moderation`: requires `works.delete_any` and JSON body `{ "reason": string }`; reason must be 10–1000 normalized characters; returns 204, 404 when the published work does not exist, and 503 when storage deletion fails.

### Database

- Migration: `20261007_011_create_work_deletion_audits.sql`
- Creates `work_deletion_audits` with UUID identifiers, moderator/owner/work snapshot fields, reason length constraint, deletion timestamp, and indexes for work, owner/time, and moderator/time lookup.
- The audit intentionally has no foreign key to the deleted work so history survives deletion; rollback drops the audit table but cannot restore deleted files or works.

### Permissions and scope

- Required permission: `works.delete_any`.
- Accessible only to `admin` and `system_administrator` through user-service permission claims.
- The main backend validates the authenticated JWT and permission before loading or deleting a work.
- The permission applies system-wide rather than only to works owned by the actor.

### Frontend

- The API supports the home and profile moderation controls implemented in `inkfig-user-FE`.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q` — 39 tests passed.
- `[passed] uv run --with-requirements requirements.txt mypy src tests migrations`
- `[passed] Ruff check and format check for all changed Python files`
- `[passed] git diff --check`
- `[passed] migration runner applied 20261007_011_create_work_deletion_audits.sql and verified work tables/storage bucket`

### Deployment

- Deploy `inkfig-main-system` after the user-service permission deployment.
- Migration has already run against the configured Supabase database.
- No environment-variable changes.

### Git

- Branch: `main`
- Commit: `5e525a0`
- Push: `successful`

### Notes

Storage deletion happens before the database transaction. If the later database operation fails, the storage object cannot be restored automatically, although the database transaction itself rolls back.

## 2026-10-08 - Emit work interaction notifications

### Request

Notify work owners when another user likes or saves their post.

### Changes

- Emits persistent like/save notifications from the authoritative backend transactions.
- Suppresses self-notifications and refreshes an existing deduplicated event when an interaction is repeated.
- Work deletion cascades to its notification records through the shared schema.

### API and database

- No API contract changes and no migration in this repository.
- Depends on user-system migration `20261008_015_create_notifications.sql`.

### Verification

- `[passed] git diff --check`
- `[added] like/save notification regression test`
- `[not run] pytest/mypy` - Python is unavailable locally; GitHub Actions will run both.

### Deployment and Git

- Deploy after `inkfig-user-system` and before `inkfig-user-FE`.
- Branch: `feature/full-notifications`; commit/push pending final synchronization.

## 2026-10-08 - Publish work notifications live

### Request

Push like and save notification changes to connected recipients immediately.

### Changes

- Added best-effort API Gateway WebSocket publishing after persistent like/save notification creation.
- Added stale connection cleanup and deployment discovery of the user-system WebSocket API.

### Repositories

- `inkfig-main-system`: publisher, IAM, deployment wiring, and tests.

### Files

- `src/infrastructure/integrations/notification_realtime.py`: publishes invalidations.
- `src/infrastructure/repositories/work_repository.py`: triggers delivery after commit.
- `template.yaml`: endpoint configuration and scoped IAM.
- `.github/workflows/deploy.yml`: loads the shared API ID.

### API

No REST API changes. Sends WebSocket event `notifications.changed`.

### Database

No migration required; uses the shared connection table.

### Permissions and scope

- Delivery targets only connection IDs belonging to the work owner.
- Lambda IAM is scoped to the shared production WebSocket connections.

### Frontend

No direct frontend changes in this repository.

### Verification

- `[passed] pytest -q` — 41 tests passed.
- `[passed] mypy src tests`
- `[passed] sam validate --lint`
- `[incomplete] local sam build — dependency copy remained running`

### Deployment

- Deploy after `inkfig-user-system`; workflow resolves its WebSocket API output automatically.

### Git

- Branch: `main`
- Commit: `c47411a`
- Push: `successful`

### Notes

Persistent notification creation remains authoritative even if realtime delivery is temporarily unavailable.

## 2026-10-08 - Stop save notifications

### Request

Keep artwork saving behavior but stop notifying the work owner when another user saves it.

### Changes

- Removed notification creation and WebSocket delivery from the successful save workflow.
- Preserved saving, unsaving, authorization, persistence, and existing historical notification compatibility.
- Like and follow notifications remain unchanged.

### Repositories

- `inkfig-main-system`: removed the save-notification producer and updated regression coverage.

### Files

- `src/infrastructure/repositories/work_repository.py`: no longer records a notification after saving.
- `tests/test_social_notifications.py`: verifies only likes use the work-interaction notification path.

### API

No API contract changes. Existing save endpoints retain their request and response behavior.

### Database

No migration required. Historical save notifications remain readable; no new ones are created.

### Permissions and scope

- Existing save permissions and backend authorization are unchanged.
- Notification recipient scoping for remaining events remains backend-enforced.

### Frontend

No frontend changes. Saving still updates the work state normally.

### Verification

- `[passed] pytest -q` — 41 tests passed.
- `[passed] mypy src tests`
- `[passed] focused Ruff check and format check`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` through the existing GitHub Actions workflow.
- No migration, secret, or environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `c0c8590`
- Push: `successful`

### Notes

The database event-type constraint and frontend rendering retain `save` solely so old records remain compatible.

## 2026-10-09 - Add public exact-artwork lookup

### Request

Allow a like notification to open the exact published artwork card instead of relying on the current home feed.

### Changes

- Added an exact published-artwork lookup through the work service and repository.
- Reused the published-feed authorization and visibility rules, including active-owner filtering and optional viewer like/save state.
- Returns not found for missing, deleted, unpublished, or otherwise invisible artwork.
- Intentionally left feed, search, upload, moderation, and storage behavior unchanged.

### Repositories

- `inkfig-main-system`: adds exact public artwork retrieval.
- `inkfig-user-system`: adds artwork titles to notification responses.
- `inkfig-user-FE`: consumes this endpoint for notification deep links.

### Files

- `src/entities/repositories/works.py`: adds optional exact-work repository scope.
- `src/infrastructure/repositories/work_repository.py`: filters the published query by work ID.
- `src/app/services/work_service.py`: resolves one visible published artwork or raises not found.
- `src/interface/api/routes/works.py`: exposes the exact-artwork route.
- `tests/test_work_service.py`: verifies exact work scoping and missing-work behavior.

### API

- `GET /api/v1/works/{work_id}`: returns one published artwork; accepts optional viewer authentication for personalized interaction state; returns 404 when unavailable.

### Database

No migration required. The endpoint uses existing indexed artwork identifiers and existing visibility columns.

### Permissions and scope

- Public viewers may retrieve published artwork belonging to an active account.
- Authenticated viewers additionally receive their existing like/save state.
- Unpublished, deleted, and inactive-owner artwork is excluded by backend query rules.
- Authorization and visibility are validated by the backend.

### Frontend

- Enables the frontend to open an artwork modal from a stable notification URL.
- No main-system UI changes.

### Verification

- `[passed] uv run --with ruff ruff check src/entities/repositories/works.py src/infrastructure/repositories/work_repository.py src/app/services/work_service.py src/interface/api/routes/works.py tests/test_work_service.py`
- `[passed] uv run --with ruff ruff format --check src/entities/repositories/works.py src/infrastructure/repositories/work_repository.py src/app/services/work_service.py src/interface/api/routes/works.py tests/test_work_service.py`
- `[passed] uv run --with-requirements requirements.txt --with pytest --with pytest-asyncio pytest -q tests/test_work_service.py` — 25 passed
- `[passed] uv run --with-requirements requirements.txt pytest -q` — 41 passed
- `[passed] uv run --with-requirements requirements.txt mypy src` — 50 source files
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system`.
- No migrations are required before deployment.
- No environment-variable or configuration changes.

### Git

- Branch: `main`
- Commit: `a5a440a`
- Push: `successful`

### Notes

The practical clean-architecture guidance kept HTTP handling, application behavior, repository contracts, and SQL filtering in their respective layers.

# 2026-10-11 — Infinite image feed, review stage 1

- Added backward-compatible `GET /api/v1/feed` with lightweight cards and `{items, nextCursor, hasNextPage}`; default 20, maximum 50.
- Versioned filter-scoped cursors use `(created_at, work_id)` keyset ordering, preventing skipped equal-timestamp posts and supporting deleted cursor posts.
- Existing published/active-owner visibility, optional viewer like/save state, category and artist filters remain enforced. Personalized responses prohibit shared caching.
- Added route-specific API Gateway throttling: 20 requests/second, burst 40 (shared, not per user).
- Reused existing composite indexes; no migration or environment changes. Resources remain request-scoped for future SnapStart compatibility.
- Files: new feed DTO, cursor codec, route, tests, and `docs/infinite-feed.md`; extended repository/service contracts, SQL implementation, router registration and SAM template.
- Verification: 57 tests passed; mypy passed for 55 source files; targeted Ruff checks passed; SAM template validation with lint passed.
- Image-only scope confirmed. This is the first requested review point: existing frontend/masonry is unchanged. Hook/list, media metadata/variants, stable masonry positioning, virtualization, and integrated UI tests remain for subsequent stages.
- Deployment: normal main-system GitHub Actions deployment; no frontend/user-system deployment needed.

## 2026-10-11 - Complete infinite image feed media support

### Request and scope

Complete the remaining image-only infinite-feed stages while preserving natural
artwork proportions, current requirements and future SnapStart compatibility.
Main-system owns media preparation/storage/schema; frontend owns feed interaction
and layout. User-system is unchanged.

### Changes and files

- Added validated `ImageMedia` DTO and optional media in feed/detail/profile/search responses.
- Added `works.media` JSONB through `20261011_012_add_work_media.sql` and its ORM mapping.
- Added request-time `ArtworkMediaProcessor`: verified content, EXIF-aware dimensions, dominant color, byte/pixel bounds, off-event-loop rendering and concurrent WebP uploads. Static variants use up to 236/474/736/1080px without upscaling; animated originals remain animated.
- Publication persists metadata before publishing; invalid images return 422 and storage/preparation failures return 503. No import-time clients, connections, credentials, timestamps or image processing were added.
- Extended storage integration to download bounded originals, upload cacheable variants and delete only an artwork's own variants with its original.
- Added resumable `scripts/backfill_work_media.py` and a post-deployment GitHub workflow step using existing secrets; originals and artwork records are retained.
- Updated repository/service contracts, SQL projections, dependency injection, tests, README and `docs/infinite-feed.md`.

### API, permissions and database

- `/feed` pagination contract is unchanged; card responses now include optional `{url,width,height,dominantColor,sizes:[{w,url}]}` in `media`.
- Existing upload permission/ownership and published/active-owner visibility remain enforced. No role or permission changes.
- Migration: `20261011_012_add_work_media.sql`; no new environment variables. Existing composite cursor indexes are reused.
- Personalized feed responses remain private/no-store; generated images use long-lived cache headers.

### Verification

- 65 backend tests passed, including metadata/variants/animation, byte/pixel limits, scoped variant cleanup and publication integration.
- mypy passed on `src tests scripts` (61 files); targeted Ruff checks/formatting and SAM validation with lint passed.
- Frontend contract consumed and verified separately; no UI implementation belongs in this repository.

### Deployment and limitations

Apply migration, deploy main-system, finish the additive resumable backfill, then
deploy frontend. Workflow reports failed backfill records visibly and they remain
retryable. Semantic search retains its existing ranked numeric pagination; profile
feeds retain their existing endpoint. Physical-phone FPS and field CLS targets are
not certified by these checks. Push directly to main after pull/rebase under the
standing workflow; no user-system changes or deployment required.

## 2026-10-11 - Support large existing JPEGs during media backfill

- Production verification found a valid existing 7000x4667 JPEG (4.7MB) exceeded the initial 25-million-pixel header bound; 29 other public artworks were prepared successfully. Backend deployment itself succeeded; the backfill correctly reported failure rather than skipping it silently.
- Added JPEG decoder subsampling before rendering, retaining original EXIF-normalized dimensions while bounding the decoded working canvas at 25 million pixels. Header limit is now 80 million pixels, below Pillow's default bomb-warning threshold. Non-subsampled formats still enforce the decoded bound.
- Color sampling uses a small thumbnail instead of a full-size second RGB canvas, reducing request-time memory. No original image, user record, permission, API shape or environment configuration is changed.
- Updated image-processing regression tests (large JPEG and EXIF rotation), documentation, and removed a terminal blank line from the additive migration.
- Verification: 67 backend tests passed, with clean type/lint checks; the resumable backfill retries only missing metadata on the next normal main deployment.
- Deployment: main-system follow-up, then frontend after backfill success. Processing still runs at request/execution time for future SnapStart compatibility.

## 2026-10-18 - Exhibitions, participation and moderation

### Request

Enable exhibitions with names, descriptions, dates, optional banners, participation windows, owned-work submissions, approval/rejection reasons and participant blocking. User explicitly confirmed that supervisors manage all exhibitions.

### Changes

- Added public exhibition lists/details and management create/edit operations.
- Added database-backed permission checks against current active verified accounts rather than relying on stale JWT roles.
- Added pending submissions for owned published works, approval/rejection with required reason, owner-visible status and management queues.
- Enforced opening/closing timestamps, duplicate protection and exhibition-specific participant blocks.
- Blocks hide existing approved entries until unblocked; shared exhibition-row locks serialize submissions, blocks and reviews.
- Added scoped signed banner uploads, bounded image verification/processing, and replacement cleanup of the preceding banner and variants.
- Kept existing public artwork publication, search, interactions, social notifications and storage behavior intact.

### Repositories

- `inkfig-main-system`: exhibition API, application service, repository, schema, storage integration and tests.
- `inkfig-user-FE`: bilingual exhibition pages and upload-and-submit workflow.
- `inkfig-user-system`: no code changes; shared role-permission tables receive new grants from this migration.

### Files

- `migrations/20261018_013_create_exhibitions.sql`: schema, indexes, grants and banner bucket.
- `src/entities/dto/exhibitions.py`: validated dates, descriptions, reasons, uploads and response contracts.
- `src/entities/repositories/exhibitions.py`: persistence contract.
- `src/app/services/exhibition_service.py`: permissions, review, participation and banner orchestration.
- `src/infrastructure/repositories/exhibition_repository.py`: async persistence, visibility and transaction locks.
- `src/interface/dependencies/exhibitions.py`: request-time wiring.
- `src/interface/api/routes/exhibitions.py`: bounded public/protected endpoints.
- `src/main.py`: router and application-error registration.
- `tests/test_exhibitions.py`: permission, date, reason and storage-scope tests.
- `tests/test_exhibition_database.py`: opt-in full workflow integration inside a rolled-back transaction.
- `docs/exhibitions.md`: API, lifecycle, scope and deployment reference.

### API

- `GET /api/v1/exhibitions` and `GET /api/v1/exhibitions/{id}`: public listing/details.
- `POST /api/v1/exhibitions` and `PUT /api/v1/exhibitions/{id}`: manage name, description, event date and participation dates.
- `GET|POST /api/v1/exhibitions/{id}/submissions`: public/mine/manage scopes or submit an owned work.
- `PATCH /api/v1/exhibitions/{id}/submissions/{submission_id}`: approve/reject, with required rejection reason.
- `GET /api/v1/exhibitions/{id}/blocks`, `PUT|DELETE /api/v1/exhibitions/{id}/blocks/{user_id}`: bounded blocked list, block with reason, unblock.
- `POST /api/v1/exhibitions/{id}/banner-uploads` and `/banner-uploads/complete`: image upload/validation and assignment.
- Lists default to 20, maximum 50; offset continuation cursor. Dates require timezone and open < close <= event. 401 unauthenticated, 403 forbidden/blocked, 404 missing target, 409 closed/duplicate, 422 invalid values, 503 storage failure.

### Database

- Migration: `20261018_013_create_exhibitions.sql` — applied successfully to Supabase.
- Adds exhibitions, exhibition_submissions and exhibition_blocks with FKs, cascading membership deletion, unique exhibition/work constraint, validated status/reasons/dates and ordered queue indexes.
- Enables RLS and denies anon/authenticated table access; service role owns persistence.
- Adds exhibitions.manage and exhibitions.participate grants to existing roles.
- Creates exhibition-banners bucket, public reads, bounded image formats/size and signed backend-controlled writes.
- No destructive backfill. Withdraw UI/API before rollback; retain data/banners unless deletion is explicitly authorized.

### Permissions and scope

- `exhibitions.manage`: every supervisor, admin and system administrator can manage every exhibition.
- `exhibitions.participate`: user, supervisor, admin and system administrator can submit owned published works.
- Guests see exhibition details and approved unblocked entries only. Pending/rejected entries are restricted to their owner or managers.
- Backend validates permissions, active/verified account, ownership, participation window and block state.

### Frontend

- Companion frontend replaces exhibition placeholder with public cards/details and permission-scoped management forms, review queue, my-submissions section and blocking controls.
- Students select existing works or upload/publish a new work then submit for approval.
- Arabic/English, light/dark, responsive layout and bounded continuation loading.

### Verification

- `[passed] uv run --python 3.12 --with-requirements requirements.txt pytest -q` — 76 passed, optional DB test skipped by default.
- `[passed] INKFIG_EXHIBITION_DB_TEST=1 pytest -q tests/test_exhibition_database.py` — full real Supabase workflow; all test data rolled back.
- `[passed] uv run --python 3.12 --with-requirements requirements.txt mypy src tests scripts` — 69 files.
- `[passed] targeted ruff check/format`
- `[passed] sam validate --lint`
- `[passed] python -m migrations.run` — exhibition migration applied and database verified.
- `[passed] git diff --check`
- `[failed] initial checks — list method shadowed built-in annotations and row mapping needed typing; corrected before successful full rerun.
- `[failed] first DB fixture setup — existing auto-role trigger created default roles; corrected test fixture to upsert and reran successfully.

### Deployment

- Deploy main backend after migration, then frontend. Existing workflows handle deployments.
- No new environment variables or IAM privileges. No user-backend deployment required.

### Git

- Branch: `main`
- Commit: `af44dcb`
- Push: pending final synchronization; recorded in the final handoff.

### Notes

Application decisions live in the service, SQL/storage details in infrastructure, and HTTP parsing in routes as required by the architecture guidance. No import-time clients or clock-dependent state were introduced for future SnapStart compatibility. Existing profile works remain public; review gates exhibition membership. Exhibition WebSocket events and scheduled banner orphan retries are not part of this release; immediate banner cleanup can fail after assignment and should be monitored.

## 2026-10-18 - Upcoming and past exhibition pagination

### Request

Separate the exhibitions page into Upcoming Exhibitions and Past Exhibitions with screen-height-bounded cards.

### Changes

- Added optional upcoming/past classification using database time and each exhibition's scheduled event date.
- Upcoming results sort nearest first; past results sort most recent first.
- Each section has its own bounded continuation page, avoiding client-side classification of a single incomplete combined page.
- Retained default all-results ordering, permissions, participation/review rules, and banner handling.

### Repositories

- `inkfig-main-system`: period-filtered listing and pagination.
- `inkfig-user-FE`: separate sections and viewport-sized exhibition cards.

### Files

- `src/interface/api/routes/exhibitions.py`: validates all/upcoming/past period query.
- `src/app/services/exhibition_service.py`: passes listing period through the application boundary.
- `src/entities/repositories/exhibitions.py`: extends the repository contract.
- `src/infrastructure/repositories/exhibition_repository.py`: indexed date predicates and ordering.
- `tests/test_exhibitions.py`: independent period/cursor delegation test.
- `tests/test_exhibition_database.py`: real database verification of disjoint upcoming/past results.
- `docs/exhibitions.md`: documents period query and ordering.

### API

- `GET /api/v1/exhibitions?period=all|upcoming|past&limit=20&cursor=0`: optional validated period, defaults to all; upcoming uses event_at > now(), past uses event_at <= now().
- Pagination limits, response shape, public visibility and invalid-query 422 behavior retained.

### Database

No migration required. Reuses exhibitions_event_idx in forward/reverse traversal for date predicates and deterministic event_at/exhibition_id ordering.

### Permissions and scope

- Listing remains public for all periods.
- Existing management, ownership and participation authorization remains enforced by the backend.

### Frontend

- Companion release consumes independently paginated upcoming/past results and displays short card previews with full details linked.

### Verification

- `[passed] pytest -q` — 77 passed, 1 opt-in database test skipped by default.
- `[passed] INKFIG_EXHIBITION_DB_TEST=1 pytest -q tests/test_exhibition_database.py` — real period-filter and lifecycle verification; all fixtures rolled back.
- `[passed] mypy src tests scripts` — 69 files.
- `[passed] targeted Ruff check and formatting`
- `[passed] git diff --check`

### Deployment

- Deploy main backend before frontend through existing workflows.
- No migration, secret, environment or IAM changes.

### Git

- Branch: `main`
- Commit: `806c1bc`
- Push: final synchronization and push reported in handoff.

### Notes

Past Exhibitions describes events whose scheduled start has passed; exhibitions currently have no separate end timestamp. Existing architecture boundaries and request-time database clocks are preserved for SnapStart compatibility.

## 2026-10-18 - Eligible exhibitions and ten-work participation limit

### Request

Support assigning profile works or uploading one work at a time to eligible exhibitions, require review, limit each user's active participation to ten works per exhibition and provide personal approved/pending pages.

### Changes

- Added authenticated, paginated eligibility lookup filtered by open participation, future event start, blocks, active quota and optional owned work/already-submitted exclusion.
- Enforced at most ten pending/approved entries per user/exhibition while holding the existing exhibition transaction lock.
- Rejected entries free capacity; reconsidering rejected entries checks capacity before approval. Existing duplicate constraints and rejection reasons remain.
- Added status filtering before pagination without weakening public/mine/manage visibility.
- Existing uploads remain public profile works; approval controls exhibition membership. Authentication, storage cleanup and unrelated APIs unchanged.

### Repositories

- `inkfig-main-system`: eligibility API, quota enforcement, filtered pagination and index.
- `inkfig-user-FE`: assignment dialog, upload participation, toolbar and personal submission page.

### Files

- `src/interface/api/routes/exhibitions.py`: eligible route and validated status query.
- `src/app/services/exhibition_service.py`: current participation authorization and paginated eligibility/status delegation.
- `src/entities/repositories/exhibitions.py`: extended repository contracts.
- `src/infrastructure/repositories/exhibition_repository.py`: eligibility query and locked quota checks.
- `migrations/20261018_014_index_active_exhibition_submissions.sql`: active owner quota index.
- `tests/test_exhibitions.py`: permission and owner/status delegation tests.
- `tests/test_exhibition_database.py`: real rolled-back eligibility, duplicate, quota, review and status lifecycle checks.
- `docs/exhibitions.md`: contract, lifecycle and deployment decisions.

### API

- `GET /api/v1/exhibitions/eligible`: current verified/active actor requires exhibitions.participate; optional work_id must be owned/published (404 otherwise), optional exhibition_id targets one exhibition. Defaults limit20, max50, cursor0. Excludes closed/started, blocked, full and already-assigned entries.
- `GET /api/v1/exhibitions/{id}/submissions`: optional status pending|approved|rejected filters before pagination while retaining ownership/management/public checks; invalid status422.
- `POST /api/v1/exhibitions/{id}/submissions`: one work_id per request; pending by default; full active quota409, duplicate409, closed409, blocked403, foreign/unpublished work404.
- `PATCH /api/v1/exhibitions/{id}/submissions/{submission_id}`: approving a previously rejected entry returns409 if active quota is full. Required rejection reason unchanged.

### Database

- Migration: `20261018_014_index_active_exhibition_submissions.sql` - applied successfully to Supabase.
- Adds partial index on exhibition_id/user_id for pending/approved rows; no schema fields, defaults, constraints, FKs or stored data changed.
- Existing row locks serialize quota checks with submissions/reviews/blocks. No destructive backfill; existing over-limit entries retained, new additions refused.
- Rollback: drop public.exhibition_submissions_active_owner_idx after withdrawing new application behavior if rolling back the feature.

### Permissions and scope

- exhibitions.participate: user/supervisor/admin/system_administrator; current active/verified account and database permissions checked by backend.
- exhibitions.manage: supervisors/admins/system administrators manage all exhibitions.
- Eligibility is actor-specific, optional work must belong to actor, private status sections remain owner-only; guests only see public approved entries.
- Backend validates every submission independent of frontend eligibility/preflight.

### Frontend

- Companion frontend supplies eligible assignment dialog, single-file exhibition upload, blurred action toolbar and independently paginated personal status sections.

### Verification

- `[passed] pytest -q` - 80 passed, optional DB test skipped by default.
- `[passed] INKFIG_EXHIBITION_DB_TEST=1 pytest -q tests/test_exhibition_database.py` - real Supabase lifecycle, all fixtures rolled back and no storage writes.
- `[passed] mypy src tests scripts` - 69 source files, no issues.
- `[passed] targeted Ruff format/check`
- `[passed] python -m migrations.run` via dotenv-loaded configuration - migration014 applied and database verified.
- `[passed] git diff --check`
- `[failed] initial test run - expected repository call omitted new optional status parameter; updated assertion and final rerun passed.
- `[failed] initial sandbox Python discovery - installed uv Python directory inaccessible; approved environment rerun passed.

### Deployment

- Migration applied before backend release. Deploy main backend, then frontend through existing main workflows.
- No new environment variables, IAM permissions or user-backend deployment.

### Git

- Branch: `main`
- Commit: `cb9b330`
- Push: pending final synchronization; verified outcome reported in handoff.

### Notes

Architecture skill kept HTTP contracts, service authorization and infrastructure SQL separate. No import-time clients or clocks introduced. Available means participation currently open and event start not passed because exhibitions have no end timestamp. Existing profile publication, banner cleanup limitations and non-realtime exhibition moderation remain unchanged.
## 2026-10-18 - Moderated exhibition withdrawals and launch visibility

### Request

Hide exhibition works before launch, provide owner/manager record lists with status filters, allow pending deletion and require reason plus manager approval to remove approved submissions.

### Changes

- Public submission queries return no memberships until database event time, without restricting private owner/manager scopes.
- Added owner withdrawal: pending membership removed directly; approved membership retains approval while a required-reason deletion request is pending.
- Added manager approval/rejection of deletion requests, with rejection reasons and durable decision audits. Approval removes membership only, never the profile work or storage image.
- Redacted withdrawal metadata from public responses and retained current role/owner checks.
- Guarded original profile deletion before storage access while any approved membership exists; work locks coordinate with submission approval to prevent bypass.
- Existing moderator deletion privileges, quota rules, duplicate controls and unrelated services remain unchanged.

### Repositories

- `inkfig-main-system`: protected withdrawal workflow, visibility gate and audit persistence.
- `inkfig-user-FE`: fixed navbar, unified owner/review records, filters, card context and decision dialogs.

### Files

- `migrations/20261018_015_exhibition_withdrawal_requests.sql`: withdrawal metadata and audited decisions.
- `src/entities/dto/exhibitions.py`: withdrawal input and private response fields.
- `src/entities/repositories/exhibitions.py`: new persistence contracts.
- `src/app/services/exhibition_service.py`: current permission checks and workflow delegation.
- `src/interface/api/routes/exhibitions.py`: owner withdrawal and manager decision routes.
- `src/infrastructure/repositories/exhibition_repository.py`: locked transitions, start-time visibility, redaction and audit inserts.
- `src/infrastructure/repositories/work_repository.py`: approved-membership owner deletion guard before storage removal.
- `tests/test_exhibitions.py`, `tests/test_exhibition_database.py`: authorization, state transitions, preservation, redaction and launch checks.
- `docs/exhibitions.md`: API/lifecycle/deployment documentation.

### API

- `POST /api/v1/exhibitions/{id}/submissions/{submission_id}/withdrawal`: current participation permission and ownership; body reason optional for pending, required/nonblank for approved, max2000. Returns204; foreign/missing404, missing approved reason422, duplicate request or rejected membership409.
- `PATCH /api/v1/exhibitions/{id}/submissions/{submission_id}/withdrawal`: management permission; approved/rejected decision, required rejection reason. Returns204; no pending deletion request409. Approval removes only exhibition membership; rejection preserves approval.
- `GET /api/v1/exhibitions/{id}/submissions`: public memberships hidden before start; mine/manage include private withdrawal status/reason/review reason, public fields redacted. Existing bounded status pagination retained.
- `DELETE /api/v1/works/{id}`: owner receives409 before image deletion if an approved exhibition membership remains. Moderator deletion behavior unchanged.

### Database

- Migration: `20261018_015_exhibition_withdrawal_requests.sql` - applied successfully to Supabase.
- Adds nullable withdrawal status/reason/request time/review reason/reviewer FK/review time; existing rows remain NULL, with approved-state/reason constraints.
- Adds partial pending-request index and RLS-protected exhibition_withdrawal_audits table with event/decision index. Work/user/reviewer audit FKs use SET NULL; membership identifier survives membership deletion, event FK cascades on exhibition deletion.
- Audit writes and membership mutations share the same transaction and exhibition lock. No original works, vectors or storage objects deleted by withdrawals.
- Rollback requires withdrawing UI/API, handling pending requests and exporting audit history before dropping new columns/table/indexes. No destructive backfill performed.

### Permissions and scope

- exhibitions.participate: only current verified active owners can withdraw their own entries, regardless of whether participation is now closed.
- exhibitions.manage: supervisors, admins and system administrators review all exhibitions, including deletion requests.
- Backend validates ownership, permissions and transition state on every mutation; private reasons never appear in public exhibition results.
- Existing works.delete_any moderator authority remains intact and audited separately.

### Frontend

- Companion release adds fixed responsive action bar, separate review route and one paginated record list per owner/manager view with dropdown status filters.

### Verification

- `[passed] pytest -q` - 81 passed, opt-in database test skipped by default.
- `[passed] INKFIG_EXHIBITION_DB_TEST=1 pytest -q tests/test_exhibition_database.py` - full real Supabase lifecycle, all fixtures rolled back; no storage writes/deletes.
- `[passed] mypy src tests scripts` - no issues in 69 source files.
- `[passed] targeted Ruff format/check`
- `[passed] migration runner` - migration015 applied and database verified.
- `[passed] git diff --check`
- `[failed] initial real DB review check - PostgreSQL inferred conflicting varchar/text parameter types; explicit casts fixed it and final reruns passed.

### Deployment

- Migration applied before main backend release. Deploy main backend first, then frontend through existing workflows.
- No new environment variables, IAM privileges or user-backend deployment required.

### Git

- Branch: `main`
- Commit: `9e4aec9`
- Push: pending final synchronization; outcome reported in handoff.

### Notes

The architecture skill preserved DTO/service/interface/infrastructure boundaries; atomic ownership/state rules are checked under transaction locks. Deletion here means exhibition membership, not the underlying artwork. Supabase testing preserved original works and audit reasons while exercising real SQL. No exhibition WebSocket behavior added; existing banner cleanup limitation unchanged.

## 2026-10-18 - Creator avatar metadata for artwork cards

### Request and changes

Added optional artist_avatar_url to work, semantic-search and infinite-feed responses. Existing profile joins select avatar_object_path and construct its public profile-avatars URL using the shared storage origin and encoded path. Grouped queries include the avatar path. This supplies creator pictures without per-card profile HTTP requests; null paths remain null and active-owner visibility is retained.

### Repositories and deployment

Matching feature/gallery-creator-rows branches in main-system and user-FE. Deploy main-system before frontend creator rows. No migration, permissions, secrets, environment variables or SnapStart initialization change.

### Verification

Added SQL selection and encoded/missing avatar URL regression coverage. Local python -m mypy src tests could not execute because Python is unavailable; pytest also requires CI. git diff --check passed. Frontend 216 tests and strict TypeScript/Vite build passed, including stable masonry appends with identity-row geometry.

### Git

Branch: feature/gallery-creator-rows. Fetch/rebase before push and authorized fast-forward main merge/push. Commit and push outcomes reported in handoff; previous entries preserved.

## 2026-10-18 - Add Other artwork category

### Request and changes

Added the active Other / أخرى work type with stable code other through a new idempotent seed migration. Existing categories, work records, APIs, authorization and SnapStart behavior are unchanged. Added a focused migration regression test.

### Repositories and files

inkfig-main-system: migrations/20261018_016_add_other_work_category.sql, tests/test_other_work_category.py and this log. Matching frontend branch adds the homepage filter and localized labels; user-system unchanged.

### Verification

git diff --check passed. Python pytest and mypy could not run because Python is unavailable locally; CI verification required. Frontend 228 tests and TypeScript/Vite production build passed.

### Deployment

Run migration 20261018_016_add_other_work_category.sql through the existing deployment migration runner before deploying the frontend filter. Existing types API supplies the new category to upload forms; no environment or permission changes. Live database migration not executed locally.

### Git

Branch: feature/other-artwork-category. Focused commit, fetch/rebase, branch push and authorized fast-forward main merge/push; exact hashes and outcomes reported in handoff. Previous entries preserved.

## 2026-10-18 - Include artist avatars in exhibition submission records

### Request and changes

Support the administrator review layout with each artist's avatar beside their name. Added nullable artist_avatar_url to Submission and selected avatar_object_path through the existing user_profiles join. Converts the path using the existing encoded public profile-avatar URL helper, removes the internal alias before DTO construction and performs no extra profile query/network request per card.

### Repositories and files

All three repositories checked clean and main pulled. Matching feature/layout-review-refinements branches in inkfig-main-system and inkfig-user-FE; user-system unchanged. Files: exhibition DTO/repository, new test_submission_avatars.py and this log. Incoming Other category changes retained.

### API, database, permissions and scope

Submission lists add optional artist_avatar_url (null without a photo), consistent with existing public artwork/profile avatar metadata. Existing scope/owner/manager authorization, publication/active-account filters, bounded pagination and private withdrawal redaction remain unchanged. No migration, index, storage write, embedding, permissions, configuration or IAM changes. Existing join reused; no import-time clients, clocks or other SnapStart-sensitive state added.

### Verification

85 backend tests passed; one opt-in live database test skipped by default. Mypy passed on src/tests/scripts (71 files), and git diff --check passed. New mocked repository tests cover missing/encoded avatar paths, one-query mapping, active/published filtering and no internal path field in the response. Initial new test used reversed viewer/scope arguments; fixed after mypy identified it and complete tests/type checks rerun successfully. Python verification used an isolated temporary environment because the PATH Python alias was unusable; no project dependencies changed. Existing Starlette/AnyIO deprecation warning remains. No live database or storage writes performed.

### Deployment and Git

Deploy main-system first through its existing workflow, then frontend layout changes. No migration or user-system deployment needed; frontend tolerates older responses with initials. Branch: feature/layout-review-refinements. Fetch/rebase before branch push, authorized fast-forward main merge/push; exact commit, push/conflicts and deployment outcomes reported in handoff. Prior log entries preserved.

## 2026-10-19 - Administrator exhibition deletion

### Request and changes

Add an administrator option to permanently delete an exhibition alongside the submission-interface refinements. Added DELETE /api/v1/exhibitions/{id}, service/repository ports and implementation. Checks current active/verified management permission and current database role admin/system_administrator; supervisors cannot delete. Locks the exhibition row, removes its assigned banner and derived variants through the existing storage helper before committing SQL deletion. Existing cascades remove submissions, participation blocks and withdrawal audits. Original artists' works, media and embeddings are deliberately preserved. Storage/network cleanup failures roll back SQL and return retryable 503; missing exhibition returns 404. Storage/SQL cannot be atomic: a later SQL failure may leave a removed banner until deletion is retried, documented explicitly.

### Repositories and files

All three repositories checked clean and main pulled before changes. Matching feature/exhibition-interaction-polish branches in main-system and user-FE; user-system unchanged. Files: exhibition route, service, repository protocol/implementation, docs/exhibitions.md, new test_exhibition_delete.py, extended opt-in database workflow and this log.

### API, database, permissions and scope

New authenticated DELETE endpoint returns 204 with no body; 401/403/404/503 errors retain the standard detail response. No migration or new permission seed: existing foreign keys and role/permission tables suffice. No new dependencies, configuration, secrets, IAM or import-time clients/state; SnapStart compatibility preserved. No real exhibition, artwork or production storage deleted during verification.

### Verification

99 tests passed; one opt-in rolled-back database integration test skipped. Mypy src/tests passed on 71 files; git diff --check passed. New tests cover anonymous/denied/supervisor/admin authorization, endpoint contracts, banner-before-SQL ordering, no-banner deletion, missing exhibition, rollback on storage/SQL errors and existing cascade schema. Opt-in workflow additionally checks actual cascade deletion and original-work preservation when explicitly enabled. Initial test type-inference issue corrected and full checks rerun. Existing Starlette/AnyIO deprecation warning remains.

### Deployment

Deploy main-system through existing GitHub Actions before companion frontend publication. No migration or user-system deployment required. Production workflow result reported in final handoff; local SAM deployment not performed.

### Git

Branch: feature/exhibition-interaction-polish. Commit message: Add administrator-only exhibition deletion. Fetch/rebase before branch push, then explicitly authorized fast-forward main merge/push. Exact commit hash, push/merge/conflict and deployment outcomes reported in final handoff. Earlier log entries preserved.

## 2026-10-19 - Live exhibition requests, student decisions and manager counters

### Request and scope

Students get saved decision notifications and live My submissions updates; managers get open-queue refresh only, plus pending counters on related navigation/review controls. Main-system owns transactions/events/count queries, user-system owns notification schema/read APIs, frontend owns presentation and request gating.

### Changes and files

- src/infrastructure/repositories/exhibition_repository.py inserts decision notifications before commit and emits invalidations afterward. Same submission decision retries do not create new notifications. Withdrawal decisions save their notification before membership removal; original artwork remains untouched. Submit/withdraw/block/delete operations update affected live views.
- src/infrastructure/integrations/notification_realtime.py scopes exhibitions.changed to active verified managers and the affected user. Sends notifications.changed for decision recipients. Transport errors are isolated after commit and stale connections cleaned; clients/credentials resolve at execution time for SnapStart.
- src/app/services/exhibition_service.py, src/entities/repositories/exhibitions.py and src/interface/api/routes/exhibitions.py add permission-gated GET /exhibitions/pending-counts with overall and per-exhibition pending submission/withdrawal counts.
- tests/test_exhibition_live.py and docs/exhibitions.md cover contracts, atomicity, duplicate handling, counters, permission scope and delivery-failure behavior. This log records work.

### API, database and permissions

New GET /api/v1/exhibitions/pending-counts requires exhibitions.manage; returns {total,items:[{exhibition_id,submissions,withdrawals}]}. Existing decision APIs/permission checks remain. Events contain exhibition ID only, not private decision reasons; clients retrieve protected canonical data. No main-system migration: requires user-system 20261019_023_exhibition_notifications.sql before this deployment. No new grants, environment variables or secrets. Self notifications remain excluded; there are no manager notification rows for new requests.

### Verification

108 pytest tests passed, one existing opt-in database test skipped; mypy src/tests passed on 72 files, targeted Ruff and git diff --check passed. Actual SQL migration and transaction flow verified inside fully rolled-back PostgreSQL transactions: rejection, identical retry, approval, withdrawal request/count, approved withdrawal, notification retention, original-work preservation and existing social upserts. WebSocket delivery was mocked in DB verification. Unit tests verify recipient scope, post-commit delivery, atomic notification failure and safe transport failure. Initial diagnostic attempted multi-statement SQL through a prepared driver; corrected to raw migration execution and rerun successfully.

### Frontend, deployment and limitations

Manager trophy/mobile-menu and per-exhibition Review submissions controls show pending-action counts; student bell shows unread notifications. Lists subscribe only while mounted/open, preserve active filters and refresh after reconnect. Badge summary requests are intentionally allowed on other pages. Deploy user-system migration/API first, then main-system, then frontend via main workflows; no production fixture records or messages retained. Delivery is best effort, not a durable WebSocket outbox; canonical REST state and saved notifications recover on reconnect/open.

## 2026-10-19 - Stored-vector related artwork feed

### Request, baseline and rollback record

Support dedicated public artwork pages with bounded related homepage cards and preserve a reversible implementation record. Clean main pulled first. Main-system baseline b11e077f0e60abb25a6a044ce5f63df3de1fb58c; frontend baseline c925263f8ec2bdc74a911c52bff1e9dc62c22c08. docs/artwork-detail-page-rollback.md records change inventory and safe revert procedure: frontend first, backend second, only ticket commits, no reset/force push or database rollback. Exact hashes in handoff.

### Changes and files

Added DTO/repository protocol/service/SQL repository for GET /api/v1/works/{work_id}/related, dependency wiring and route, tests/test_related_artworks.py, rollback document and this log. Existing stored model-compatible pgvector cosine scores >=0.20 rank first; 0.02 bands prefer matching categories among near scores, then exact similarity and stable created_at/work_id order. Same-category results provide fallback when vectors are absent. Source and results must be published and owners active; current work excluded. Lightweight cards expose existing public avatar/media/category fields, active-user like count and personalized liked/saved state.

### API, database, permissions and SnapStart

Optional existing viewer authentication; source 404, invalid cursor 400 and limit 1..50. Private/no-store response with Cookie/Authorization Vary. Source-bound snapshot/offset cursor limits stored offset to 10000, bounds parsing and limits page query. Snapshot excludes newer uploads; deletions/edits/backfills can shift live ranked offsets, client deduplicates. Exact scoring scans eligible vectors, so production query cost should be monitored as the catalogue grows; no approximate index performance claim. No migrations, provider requests, new grants/dependencies/environment/IAM, storage writes or table mutations. Sessions/storage resolve through existing request-time dependencies; no new import-time clock/client/credential state.

### Verification and limitations

118 pytest checks passed, two opt-in database checks skipped; mypy src/tests passed on 77 files and git diff --check passed. Tests cover source scoping, snapshot pagination, invalid cursors/limits, unavailable source, visibility/model/category SQL guards and endpoint serialization/cache/error contracts. Read-only DB test provided with INKFIG_RELATED_DB_TEST=1; attempted execution could not connect because DATABASE_URL is not configured, prerequisite now explicitly skips. Actual new SQL execution is not claimed. Existing Starlette/AnyIO deprecation warning remains. No production data or storage changed during verification. Companion frontend 330 checks and strict production build passed.

### Git and deployment

Matching feature/artwork-detail-page branches in main-system and user-FE; user-system unchanged. Subject: Add stored-vector related artwork feed. Fetch/rebase before push, then previously authorized fast-forward main merge/push. Deploy existing main-system workflow first, frontend next; no migration prerequisite. Exact hashes, push/merge/conflict and deployment outcomes reported in final handoff; historical entries retained. Computer-use visual review was blocked by browser URL safety verification and is not claimed.

## 2026-10-20 - Require visual similarity for related artworks

### Request and changes

Only display related artworks with stored cosine similarity >=0.20; otherwise use the existing localized no-related-artwork state. Removed same-category eligibility and score-band/category ranking from the SQL repository. Exact descending similarity now determines order, with existing creation-date/ID tie breakers. Missing or incompatible embeddings cannot qualify. Current artwork exclusion, published/active-owner visibility, personalized interactions, snapshot/offset pagination and response shape remain unchanged.

### Repositories and files

Only inkfig-main-system changed: src/infrastructure/repositories/related_artworks_repository.py, tests/test_related_artworks.py, docs/artwork-detail-page-rollback.md and this log. Clean main pulled before edits; baseline 8a0cc5a80d218ec581870ea44621e3b801eb93af. Frontend inspected/pulled but unchanged: Feed already displays artwork.noRelated when loading completes with zero items, in English/Arabic. User-system unchanged. No design or masonry changes.

### API, database, permissions and SnapStart

GET /api/v1/works/{id}/related retains its API contract, optional existing authentication and private/no-store cache policy. No migration, data/storage mutations, permission, dependency, configuration, IAM or provider request changes. Existing indexes and exact vector comparison retained; no additional index needed for this predicate/ranking adjustment. Request-time clocks/dependencies and future SnapStart compatibility preserved.

### Verification

121 pytest tests passed, two existing opt-in database tests skipped; mypy src/tests passed on 77 files and git diff --check passed. Added offline execution of the actual relational SQL with only the pgvector operator replaced by a deterministic SQLite function: excludes weak same-category, missing and incompatible vectors and drafts, orders stronger cross-category matches first, and returns empty without a source embedding. Service test verifies no matches yields items=[] and next_cursor=null. Updated SQL guards and extended opt-in read-only PostgreSQL test to independently compare eligible IDs/order. SQLite checks do not claim PostgreSQL integration; DATABASE_URL remains unavailable locally. Existing Starlette/AnyIO deprecation warning remains. No production fixtures/writes used for verification.

### Deployment and rollback

Backend-only existing main-system workflow; no frontend/user-system deployment or migration. Record live read-only smoke check and workflow outcome in final handoff. Roll back only this follow-up commit to restore category fallback while retaining the artwork page; rollback document preserves the original ticket record and adds this follow-up baseline/scope. Do not reset or force-push.

### Git

Branch: fix/related-artwork-similarity. Commit subject: Require visual similarity for related artworks. Fetch/rebase newest origin/main before branch push, then previously authorized fast-forward main merge/push. Exact commit hash, push/merge/conflict and deployment outcomes reported in final handoff. Historical feature-log entries unchanged.

## 2026-10-20 - Exhibition end times and current period

### Request and changes

User selected administrator-set end dates to distinguish Current, Upcoming and Past exhibitions. Added timezone-aware event_ends_at with end-after-start validation, persistence and an additive current list period. Server time classifies current as start <= now < end, past as end <= now, upcoming before start; filters run before independent pagination. Existing/null legacy end times resolve to start +24 hours, editable by managers. Submission DTO/query adds public description and English/Arabic category names through one work-type join, supporting large split cards without per-card detail calls. Existing publication/active-account/approval/block/withdrawal privacy guards retained.

### Repositories and files

All three clean repositories pulled first. Matching feature/current-exhibition-gallery branches in main-system and user-FE; user-system unchanged. Files: exhibition DTO/repository/routes, migration 20261020_017_exhibition_end_time.sql, docs/exhibitions.md, new test_exhibition_periods.py, extended submission-avatar mapping test and this log.

### API, database, permissions and SnapStart

Migration adds nullable event_ends_at, backfills existing schedules to start +24 hours and adds end-after-start check. Nullable column supports rolling deployment/old-backend rollback; new API always resolves a value. Existing clients omitting the field receive the compatibility duration. New current query period and additive summary fields; no removed endpoints or permission changes. Create/edit remains backend-authorized with exhibitions.manage. No original artworks/storage/embeddings changed, new dependencies/configuration/secrets/IAM or import-time clock/client state. Managers should review legacy exhibition durations if different from 24 hours.

### Verification

129 pytest tests passed, two existing opt-in database tests skipped; mypy src/tests passed on 78 files, git diff --check passed. Tests cover end chronology/timezones/legacy duration, explicit persistence, independent SQL period predicates/cursors, current route/invalid period and category/description/avatar mapping. Existing permissions, live notifications and artwork similarity tests passed. Migration SQL inspected/tested offline; no local production DB mutation or PostgreSQL integration execution claimed. Existing Starlette/AnyIO deprecation warning remains.

### Deployment and Git

Apply migration through existing main-system workflow before API deployment, then deploy frontend; no user-system deployment. No production fixture exhibitions created or real reviews submitted. Branch: feature/current-exhibition-gallery. Commit subject: Add exhibition end dates and current period. Fetch/rebase before branch push and previously authorized fast-forward main merge/push. Exact hash, push/merge/conflict, migration and deployment outcomes reported in final handoff. Prior log entries preserved.

## 2026-10-20 - Minimum artwork dimensions of 200 by 300 pixels

### Request

Accept new artwork images only when width >=200 pixels AND height >=300 pixels, including exactly 200 x 300.

### Changes

- Added a pure domain rule and specific error; no area-only or orientation-swapping shortcut. EXIF-normalized display dimensions are checked from the uploaded file, not client claims.
- Work-upload dependency enables validation inside the existing background-thread image decoder before derivative generation/upload. Service independently validates returned dimensions before saving media/publishing; rejected works receive no embeddings.
- Shared processor keeps validation optional so exhibition banners and legacy media backfills preserve existing behavior. Existing published works/avatars unchanged.
- Existing signed upload/draft lifecycle remains: backend inspection occurs after direct storage upload; a bypassing client's rejected original remains in its existing draft workflow, not a published work. Normal frontend rejects before any upload.
- Preserved user-owned samconfig.toml changes, existing permissions, maximum limits, responsive feed and provider behavior.

### Repositories

- `inkfig-main-system`: authoritative publication validation, API error and tests.
- `inkfig-user-FE`: companion pre-upload validation and bilingual messages.

### Files

- `src/entities/work_image_rules.py`: inclusive minimum dimensions.
- `src/entities/exceptions/works.py`: WorkImageTooSmallError.
- `src/app/services/work_service.py`: publication guard.
- `src/infrastructure/integrations/work_media.py`: optional decoded-dimension callback before rendering variants.
- `src/interface/dependencies/works.py`: enables artwork-only validator.
- `src/interface/api/routes/works.py`: dedicated HTTP 422 message.
- `tests/test_work_media.py`: boundaries, orientation, no-publication/no-variant behavior and HTTP mapping.
- `README.md`: documented scope and width/height interpretation.
- `AGENT_FEATURE_LOG.md`: append-only ticket record.

### API

- `POST /api/v1/works/{work_id}/publish`: returns 422 with detail `Artwork images must be at least 200 pixels wide and 300 pixels tall.` if either bound fails. Existing ownership, works.upload permission, 204 success and other errors retained. Upload-initiation fields unchanged because dimensions must be checked against the real stored bytes.

### Database

No migration required. No schema, index, backfill or existing-data changes. No rollback migration needed.

### Permissions and scope

- Existing works.upload permission and backend draft ownership checks remain authoritative.
- Same new-artwork flow covers normal/exhibition uploads. Previously published works can still be assigned to exhibitions; no retroactive minimum or deletion imposed.
- No role, account, organization or exhibition-management scope changes.

### Frontend

Companion frontend validates before draft/storage creation, shows English/Arabic minimum hint and error, and retains retry/loading behavior. No card-size changes.

### Verification

- `[passed] uv --cache-dir D:/new/InkFig/.uv-cache run --with-requirements requirements.txt python -m pytest -q` - 141 passed, two existing opt-in database checks skipped.
- `[passed] same environment python -m mypy src tests` - no issues in 79 files.
- `[passed] targeted tests/test_work_media.py` - 19 tests.
- `[passed] git diff --check`
- `[failed] initial uv execution` - default cache directory unavailable; rerun with workspace cache succeeded.
- `[not run] live production upload/browser verification` - no real account, storage or provider writes used for testing. Existing Starlette/AnyIO deprecation warning remains.

### Deployment

Deploy main backend first, frontend second through existing main workflows. No migration, IAM, dependency, environment or configuration changes. Existing unrelated migration017 is not introduced or run by this ticket.

### Git

- Branch: `main`
- Commit: ticket subject `Enforce minimum artwork image dimensions` (hash reported in handoff).
- Push: pending final synchronization at entry creation; result reported in handoff.

### Notes

300 x 200 fails; 500 x 300 passes. No new import-time clients/connections/clocks or SnapStart concerns. Previous log entries and unrelated SAM configuration retained.
## 2026-11-01 - Artwork exhibition badge metadata

### Request and changes

Support exhibition year badges on artwork cards and details. Added shared WorkExhibition DTO and approved/public exhibition summaries to work/detail/search/feed/related/submission responses. Shared correlated SQL uses existing work/submission indexes inside each page query, avoiding per-card requests and row multiplication. Eligibility matches approved, started, unblocked public gallery participation. Past badges persist; approved withdrawals/deleted exhibitions disappear on fresh reads. Event year uses Asia/Hebron, not artwork creation. Existing ordering/pagination/authorization retained.

### Repositories and files

Main-system backend and companion user-FE only; user-system unchanged. Clean main pulled and complete log read. Backend baseline 653e98969f310f94bd92c72316c32fb228e11296. Files: dto/work_exhibitions.py, works/feed/exhibitions DTOs; repositories/work_exhibition_sql.py and work/related/exhibition repository queries; tests/test_work_exhibition_badges.py, test_feed_repository.py, test_related_artworks.py; docs/artwork-exhibition-badges.md and this log.

### API, database, permissions and scope

Additive exhibitions array contains exhibition_id/name/year and defaults empty. No migration, schema/index/data mutation, permission, IAM, dependency, environment or secret changes. Existing published/active-owner guards remain authoritative. No import-time clients/connections/clocks, preserving SnapStart behavior. No approval, rejection or withdrawal behavior changed.

### Verification

145 backend tests passed, two existing opt-in database checks skipped; mypy src tests passed across82 files; git diff --check passed. Relational fixture tests approved/pending/rejected/future/blocked eligibility, past retention and withdrawal deletion; feed test verifies metadata serialization in one query. Existing vector fixture omits only independently tested PostgreSQL badge JSON expression for SQLite compatibility; no vector checks bypassed. Full suite rerun after initial SQLite syntax failures. No live PostgreSQL plan/timezone-engine or production mutation testing; SQL explicitly uses named timezone and deterministic ordering. Existing AnyIO warning remains.

### Deployment and Git

Deploy this backend first, frontend second through existing main workflows; no migration or user-system deployment. Matching feature/artwork-exhibition-badges branches; backend subject Expose public exhibition membership on artwork responses. Fetch/rebase before branch push, then previously authorized fast-forward main merge/push. Exact commit/push/conflict and workflow results in handoff. Revert frontend first, then backend companion if requested; baseline and limits in docs. No reset/force push or historical log removal.

## 2026-11-01 - Lightweight artwork exhibition flags

### Request and changes

Reduce card payload/work for icon-only exhibition badges. Feed/related/search and profile/list responses now use has_exhibition SQL EXISTS with unchanged approved/started/unblocked public eligibility. FeedCardResponse carries only the boolean; WorkResponse lists retain an empty exhibitions array for compatibility. Only single-work lookup aggregates exhibition IDs/names/years. Exhibition submission/gallery no longer selects badge metadata, matching removal from exhibition-page artwork cards. No per-card requests, count/ordering/limit/cursor changes or metadata row fanout.

### Repositories and files

Companion main-system and user-FE only; user-system unchanged. Clean main pulled and complete log read; backend baseline48c570441f8f0e28387e9ce8d5b4b1d4ef48b51b. Files: works/feed/exhibitions DTOs; work_exhibition_sql/work/related/exhibition repositories; feed/related/badge tests; docs/artwork-exhibition-badges.md and this log.

### API, database, permissions and scope

Additive has_exhibition flag; full exhibitions data reserved for single-work detail. Feed/related/submission arrays removed from prior presentation metadata; coordinated frontend supports both old arrays and new flag. No migration, schema/index, permission, IAM, dependency, environment, secret or import-time state changes. Existing active/published/authorization guards retained. No SnapStart changes or production data mutations.

### Verification

147 tests passed, two existing opt-in database checks skipped; mypy src tests passed82 files and git diff --check passed. Tests verify boolean serialization without full metadata, detail-only aggregation, eligibility/withdrawal parity against relational fixtures, and unchanged related-vector/pagination behavior. Existing SQLite fixture omits only independently tested badge expression. No measured latency claim or real PostgreSQL query-plan certification. Existing AnyIO warning remains.

### Deployment and Git

Backend first, frontend next; existing main workflows, no migration or user-system deployment. Matching branch fix/lightweight-exhibition-badges; subject Use lightweight exhibition flags on artwork cards. Fetch/rebase before branch push then previously authorized fast-forward main merge/push. Exact hashes/push/conflict/deployment outcome in handoff. Revert paired revision commits to restore prior year badges; no destructive reset or data rollback. Previous log entries preserved.

## 2026-11-01 - Exhibition-scoped artwork ratings

### Request and changes

Added public1–5 ratings per exhibition/work/voter. New rating service/repository/dependency and PUT/DELETE exhibition-work rating endpoints authenticate session identity, validate strict integer scores, and enforce live account verification/activity/permission, active exhibition window, approved/published/unblocked participation, and no owner/organizer votes. Shared row locks coordinate with existing exhibition edits/reviews/withdrawals/blocking and account/work changes; atomic upsert prevents duplicates and same-score rewrites. Eligibility rechecked after mutation/waits; failures roll back. Server statement time uses inclusive start/exclusive end. Active voters' aggregates exclude inactive/unverified/blocked users and organizer/owner. Results persist after closing; changing/removing votes only while eligible.

Existing page queries now include latest publicly eligible exhibition average/count on feed/search/profile/related cards and separate totals per exhibition in single-artwork details. Gallery submissions include private my_rating/can_rate/reason in the same page request, with private/no-store/Vary headers. No per-card requests, count drift, cross-exhibition score merging, ranking or notifications. Gallery-only voting is frontend scope; no claim a server can prove HTTP callers' visible page. All real authorization is backend-owned.

### Repositories and files

Main-system and companion user-FE; user-system unchanged. Clean main pulled and complete log read. Backend baseline7dd7d40b0f99d651b2da374a14bd4ba028ff8628. New migration20261101_018_create_exhibition_ratings.sql, rating DTO/protocol/service/repository/SQL/dependency and tests; existing works/feed/exhibition/work_exhibitions DTO/query integrations, exhibitions routes, badge/feed/related SQL fixture tests, docs/exhibition-artwork-ratings.md and this log.

### API, database, permissions and scope

Migration required:20261101_018_create_exhibition_ratings.sql. Composite unique vote key, score1–5 check, composite participation FK and account FK with declared cascades, voter index, RLS and service-role-only grants. New exhibitions.rate permission granted to existing works.like roles. Existing/new JWTs use live DB eligibility; no user-system change. Public summaries contain no other-user scores/identities. Pending withdrawal retains visibility; approved withdrawal/submission/exhibition/work/account deletion cascades votes per FK. Account reactivation can restore retained eligible votes; closing is not an immutable score snapshot. No environment, IAM, dependency, credential or import-time state changes; no new SnapStart clocks/connections/clients.

### Verification

176 tests passed; two existing opt-in PostgreSQL checks skipped; mypy src tests passed89 files and git diff --check passed. New tests cover score strictness, session actor, route cache/privacy, lock/upsert/no-op replacement/removal, deny/rollback/missing scope/end-boundary cases and migration DDL/relational constraints, independent events, totals, account deactivation/reactivation/verification, blocking and cascades. SQLite adapts only PG JSON/time/cast syntax; existing related/badge fixtures omit independently tested rating expressions. Initial fixture/source assumptions corrected; full suite rerun. No production votes/reviews/uploads used for testing; no real concurrent PostgreSQL writer/load-plan certification. Existing AnyIO deprecation warning remains.

### Deployment and Git

Apply migration/backend first via existing main workflow, then frontend; no user-system deployment. Matching feature/exhibition-artwork-ratings branches. Backend subject Add exhibition-scoped artwork rating persistence and APIs. Fetch/rebase before branch push and previously authorized fast-forward main merge/push. Exact hashes, conflicts/push/merge and workflow results in handoff. Rollback frontend application commit first, then backend if necessary, preserving rating table/permission rows and votes. Export and explicit approval required before destructive schema rollback; no reset/drop or historical log removal. Detailed policy/limitations in docs.
