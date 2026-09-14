"""
hc_fulfillment_pipeline

Orchestrates the existing manual pipeline (see CLAUDE.md):

    generate -> ingest -> dbt deps -> dbt build

Each task shells out via `uv run`, against the whole project bind-mounted
into every Airflow container at /opt/hc_fulfillment (see docker-compose.yaml
- the `- ${AIRFLOW_PROJ_DIR:-.}:/opt/hc_fulfillment` mount). Airflow's own
Python environment is never used to run this project's code; `uv run`
resolves generator/ingestion/dbt dependencies from pyproject.toml/uv.lock at
task runtime instead, keeping Airflow's own large dependency set untouched.

Scoping note (shows up in the Airflow UI via doc_md below): the generator is
deterministic and regenerates the same fixed Jan-Dec 2025 dataset every run.
A monthly schedule here demonstrates orchestration mechanics - dependency
chaining, idempotent re-ingestion, retries - not real data growth.
"""

from datetime import timedelta

from airflow.sdk import dag, task

PROJECT_DIR = "/opt/hc_fulfillment"


@dag(
    schedule="@monthly",
    catchup=False,  # fixed dataset - backfilling historical runs is meaningless here
    default_args={"retries": 1, "retry_delay": timedelta(minutes=2)},
    doc_md=__doc__,
)
def hc_fulfillment_pipeline():
    @task.bash(cwd=PROJECT_DIR)
    def generate() -> str:
        """Regenerate synthetic source CSVs into data/raw/."""
        return "uv run python -m generator.main"

    @task.bash(cwd=PROJECT_DIR)
    def ingest() -> str:
        """Ingest the generated CSVs into staging tables."""
        return "uv run python -m ingestion.main"

    @task.bash(cwd=PROJECT_DIR)
    def dbt_deps() -> str:
        """Install dbt dependencies."""
        return "uv run dbt deps --project-dir dbt --profiles-dir dbt"

    @task.bash(cwd=PROJECT_DIR)
    def dbt_build() -> str:
        """dbt buld: run & test models."""
        return "uv run dbt build --project-dir dbt --profiles-dir dbt"

    generate() >> ingest() >> dbt_deps() >> dbt_build()


hc_fulfillment_pipeline()
