# Airflow orchestration - build log

This documents how the Airflow orchestration layer for this project was
built, step by step, including the reasoning behind each decision - not
just the final config. Written hand-in-hand with the build itself (not
generated after the fact), so it reflects the actual order things were
figured out, including a few real mistakes and how they were diagnosed.

**Status as of this writing**: custom Docker image built and verified.
Compose merge (bringing `sqlserver` into the same file as the Airflow
services) and the actual DAG are not done yet - this doc will be extended
as those land.

## Why Airflow, and why hand-built

The manual pipeline (`generate -> ingest -> dbt build`, see main
[README.md](../README.md)) works, but running it by hand isn't how a real
production data pipeline operates. Airflow orchestrates that same
sequence on a schedule, with retry semantics and a UI to observe run
history - the standard tool for this in the data engineering field.

This was deliberately built by hand rather than generated, specifically to
build genuine Airflow fluency rather than inherit a working black box -
see the git history/commit messages on this project for that framing.

## Step 1: start from Airflow's own official reference, not a from-scratch file

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

Reasoning: nobody hand-invents an Airflow + Postgres + Docker wiring from
a blank file in practice - starting from the maintained official reference
and customizing it is the standard approach, and a very different thing
from copying a bespoke solution wholesale. The official file also comes
with genuinely non-obvious details already handled correctly (health
checks, `AIRFLOW_UID` permission handling, `depends_on` ordering) that
would be easy to get wrong writing from zero.

Reference: <https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html>

## Step 2: understand what's actually in the reference file before changing it

The official file defaults to `CeleryExecutor` - a fundamentally different
shape than what this project needs. Key concepts, plainly:

- **Executor** = decides *how/where* a task actually runs (separate from
  the *scheduler*, which decides *when* a task is ready to run).
  - `LocalExecutor` - runs tasks as subprocesses on the same machine as
    the scheduler. Standard choice for a single-node deployment.
  - `CeleryExecutor` - distributes tasks across a pool of separate worker
    processes/machines via a message queue. Built for horizontal scaling.
  - `SequentialExecutor` (older Airflow versions) - one task at a time,
    SQLite-backed. Airflow's own docs described it as test-only, and it
    was removed outright in Airflow 3.
- **Redis / RabbitMQ** - message brokers; the queue between the scheduler
  and Celery workers. Only exist to support `CeleryExecutor`.
- **`airflow-worker`** - the Celery worker process(es) pulling jobs off
  that queue. Only exists under `CeleryExecutor`.
- **Flower** - a web dashboard for monitoring Celery workers/queues
  specifically. Nothing to monitor without Celery running.

**Decision: `LocalExecutor` + Postgres**, not `CeleryExecutor`. This DAG
is 4 tasks, strictly linear, on one host - no parallel-worker requirement
that would justify Celery's added infrastructure (broker, worker pool,
Flower). `LocalExecutor` is not a "lesser" fallback; it's the standard
right-sized choice for a single-node deployment, especially now that
`SequentialExecutor` no longer exists as an even-simpler alternative.

**Change made**: removed `redis`, `airflow-worker`, and `flower` from
`services:`, set `AIRFLOW__CORE__EXECUTOR: LocalExecutor`, and removed the
now-dead `AIRFLOW__CELERY__*` env vars (their broker URL pointed at the
just-deleted `redis` service).

**Airflow 3's service topology** (different from the older 2.x
"webserver + scheduler" shape):
- `airflow-apiserver` (renamed from `webserver`) - UI + REST API.
- `airflow-scheduler` - watches DAGs/tasks, triggers ready task instances.
- `airflow-dag-processor` - parses DAG Python files into task graphs;
  split out from the scheduler as its own process in Airflow 3.
- `airflow-triggerer` - async event loop for deferrable tasks. Standard
  part of the service set even though this project's tasks don't use any.
- `airflow-init` - one-shot: DB migration + first-user creation, then
  exits (other services wait on it via `condition:
  service_completed_successfully`, not `service_healthy`).

## Step 3: auth manager - a deliberate, explicit choice

Airflow 3 changed its *default* login system to `SimpleAuthManager` - no
real user database; it auto-generates a random password per declared user
and prints it to the `airflow-apiserver` logs. Airflow's own docs describe
this as intended for development/testing, not production.

The official reference file explicitly opts back into the older
`FabAuthManager` (`AIRFLOW__CORE__AUTH_MANAGER: ...FabAuthManager`) - a
real, DB-backed user with a fixed username/password set via
`_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD` in
`airflow-init`.

**Decision: kept `FabAuthManager`** rather than switching to the new
default - same reasoning as the executor choice: when one option is
explicitly documented as dev/test-only and a mature, production-grade
alternative already exists in the same file, that's a real signal worth
following, not a coin flip.

## Step 4: confirm the baseline runs, standalone, before customizing further

```bash
docker compose -f docker-compose.yaml up -d
```

Then logged into `http://localhost:8080` with the `FabAuthManager`
credentials set above. Confirmed via the UI's Health panel: MetaDatabase,
Scheduler, Triggerer, and Dag Processor all green.

Reasoning: isolating variables. Proving the trimmed reference file works
*on its own*, with no project-specific customization yet, means any issue
that shows up later during integration can be attributed to the
integration itself - not to a fundamentally broken base config.

**Real gotcha hit at this step**: this project also has a separate
`docker-compose.yml` (lowercase, from the SQL Server setup in
[README.md](../README.md)). Docker Compose auto-discovers a config file
by name when no `-f` flag is given, and the commonly-documented precedence
is `compose.yaml > compose.yml > docker-compose.yaml > docker-compose.yml`.
**On the Compose version actually installed here (v5.1.3), the observed
behavior was the opposite for this pair** - a plain `docker compose up`
picked `docker-compose.yml` (the SQL-Server-only file), silently ignoring
the new Airflow file. Confirmed via Compose's own printed warning ("Found
multiple config files with supported names... Using docker-compose.yml"),
not by re-trusting the documented precedence order. This is exactly why
the two files need to be merged into one (planned next step, not done
yet) - it removes the ambiguity entirely, and is required anyway so
Airflow's containers can reach `sqlserver` by service name on a shared
default network.

## Step 5: a custom Docker image for project-specific tooling

The official Airflow image has neither `uv` nor `ODBC Driver 18 for SQL
Server` (required by `dbt-sqlserver`, since `dbt build` runs via ODBC).
File: [`Docker/Airflow/Dockerfile`](../Docker/Airflow/Dockerfile).

**What's deliberately *not* baked into the image**: this project's own
Python dependencies (`dbt-core`, `pandas`, `pymssql`, ...). Only `uv`
itself is installed - the project's dependencies resolve at task runtime
via `uv run` against the project's `pyproject.toml`/`uv.lock`, which will
be bind-mounted into the container (not `COPY`'d at build time) once the
compose file is wired up to run actual pipeline tasks. Reasoning:
- **Bind-mount over `COPY`**: code changes are visible immediately,
  without rebuilding the image - important for a project still being
  actively iterated on.
- **`uv run` at task runtime over baking dependencies into the image**:
  Airflow itself already has a large, version-pinned Python dependency set
  in its own image. Installing this project's dependencies into that same
  environment risks a real version conflict on some shared library -
  keeping them separate (resolved on-demand by `uv`, into their own venv)
  avoids that entirely.

**Base OS verification, empirically, not assumed**: rather than trust
generic docs (which often default to showing Ubuntu instructions),
confirmed the actual base OS directly:
```bash
docker run --rm --entrypoint cat apache/airflow:3.3.1-python3.11 /etc/os-release
```
Output confirmed **Debian 12 (bookworm)** - so the ODBC driver install
below follows Microsoft's Debian-specific instructions, not Ubuntu's
(they document genuinely different install mechanisms per distro for the
same end result).

Also worth noting for anyone poking around inside this image manually:
its `ENTRYPOINT` is the `airflow` CLI itself (inherited from the base
image) - a bare `docker run <image> cat ...` gets treated as an invalid
argument *to* `airflow`, not run as a shell command. Use `--entrypoint` to
override it, as in the command above.

**Dockerfile structure** (see the file itself for the full commented
version):
1. `FROM apache/airflow:3.3.1-python3.11` - pinned to the exact
   image/tag/Python-version already proven working in the baseline, to
   avoid silently running two different Airflow versions.
2. `USER root` - installing system (apt-level) packages requires it.
3. Install ODBC Driver 18 for SQL Server + `mssql-tools18` (`sqlcmd`/`bcp`,
   kept for manual debugging convenience even though the automated
   pipeline doesn't call them directly) + `unixodbc-dev`, per Microsoft's
   documented Debian 12 steps:
   <https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server>
4. `ENV PATH="${PATH}:/opt/mssql-tools18/bin"` - so `sqlcmd`/`bcp` are
   reachable by name. (`ENV` persists into the running container and
   later build steps; editing `~/.bashrc` inside a `RUN` does not - each
   `RUN` is its own separate shell process, and `.bashrc` is only read by
   interactive shells anyway.)
5. Install `uv` via Astral's own recommended Docker pattern - copying the
   static binary from their published image, no build step needed:
   <https://docs.astral.sh/uv/guides/integration/docker/>
   ```dockerfile
   COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
   ```
6. `USER airflow` - switch back off root before the image is done. Real
   security practice (smaller blast radius if anything running in the
   container is ever exploited), not just style - even though the compose
   file's `user:` override also forces this at runtime regardless.

### Real bugs hit and fixed while writing this file (kept here as a record)

A first draft had several genuine errors, each worth remembering the
*shape* of, not just the fix:

- **`sudo` used while already `USER root`** - redundant; if you're already
  root there's nothing to elevate to, and `sudo` may not even be
  installed in a minimal image.
- **A `#` comment placed inside a `\`-continued multi-line `RUN` command
  silently swallows every subsequent chained command.** Docker flattens
  `\`-continued lines into one single line before the shell ever sees it -
  a `#` then comments out everything after it on that now-single line,
  not just "the rest of the visible line." Comments belong on their own
  line, above the instruction, never inside a continued command.
- **Assumed Ubuntu's `VERSION_ID` format and repo path against a
  confirmed-Debian base** - `packages.microsoft.com/config/ubuntu/...`
  was simply the wrong repo path for this image.
- **A bare bash `exit` (no argument) returns the *previous* command's
  exit code**, not a fixed failure - an `echo "unsupported"; exit`
  sequence where `echo` succeeds actually exits 0, silently *not* failing
  the build despite the apparent intent.
- **A runtime OS-detection check was unnecessary complexity** once the
  base image is already pinned to one exact tag - the OS is already known
  at build time, so there's nothing to detect dynamically.

## Step 6: build and verify the image

```bash
docker build -t hc-fulfillment-airflow -f Docker/Airflow/Dockerfile .
```

`docker build` reads the given `-f` Dockerfile and produces an image
tagged (`-t`) `hc-fulfillment-airflow`. The trailing `.` is the *build
context* - the set of local files the build is allowed to `COPY` from.
This Dockerfile's only `COPY` pulls from a different, already-published
image (`--from=ghcr.io/...`), not from local project files, so the build
context isn't actually exercised by this particular build - it's a
required argument to the command regardless.

Verified the result actually works, not just that the build exited
cleanly:
```bash
docker images hc-fulfillment-airflow
docker run --rm --entrypoint bash hc-fulfillment-airflow -c "uv --version && odbcinst -j"
```
Confirmed: `uv` on `PATH` (`uv 0.11.21`), and `odbcinst -j` printing real
driver-manager config paths (`/etc/odbcinst.ini`, etc.) rather than an
empty/broken install.

## Not done yet

- Merge `docker-compose.yml` (SQL Server) into the Airflow compose file as
  one file - removes the file-precedence ambiguity from Step 4, and is
  required for Airflow's containers to reach `sqlserver` by service name.
- Point the Airflow services at the custom `hc-fulfillment-airflow` image
  (currently they still reference the vanilla `apache/airflow` image).
- Bind-mount the project into the Airflow containers and redirect `uv`'s
  venv location to a container-local path, not the bind-mounted directory
  itself (a container-built venv at the same path as the host's own
  `.venv` risks a platform/libc mismatch).
- Set `HC_SQLSERVER_HOST=sqlserver` on the Airflow containers (both
  `ingestion/database.py` and `dbt/profiles.yml` already read this as an
  env var defaulting to `localhost`, so no code changes needed there).
- Write the actual DAG (`generate -> ingest -> dbt deps -> dbt build`).

This section will be replaced with real steps as each of these is built.
