import os
from pathlib import Path

import pymssql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL_PATH = PROJECT_ROOT / "ingestion" / "schema.sql"


def load_dotenv() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_dotenv()

SQLSERVER_HOST = os.getenv("HC_SQLSERVER_HOST", "localhost")
SQLSERVER_PORT = int(os.getenv("HC_SQLSERVER_PORT", "1433"))
SQLSERVER_USER = os.getenv("HC_SQLSERVER_USER", "sa")
SQLSERVER_PASSWORD = (
    os.getenv("HC_SQLSERVER_PASSWORD")
    or os.getenv("MSSQL_SA_PASSWORD")
    or "ChangeThis_StrongPassword_2026!"
)
SQLSERVER_DATABASE = os.getenv("HC_SQLSERVER_DATABASE", "hc_fulfillment")


def connect(database: str | None = None) -> pymssql.Connection:
    return pymssql.connect(
        server=SQLSERVER_HOST,
        port=SQLSERVER_PORT,
        user=SQLSERVER_USER,
        password=SQLSERVER_PASSWORD,
        database=database or SQLSERVER_DATABASE,
        autocommit=False,
    )


def ensure_database_exists() -> None:
    with connect(database="master") as conn:
        conn.autocommit(True)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                if db_id(%s) is null
                begin
                    declare @sql nvarchar(max) = concat('create database ', quotename(%s));
                    exec(@sql);
                end
                """,
                (SQLSERVER_DATABASE, SQLSERVER_DATABASE),
            )


def initialize_database(conn: pymssql.Connection) -> None:
    with conn.cursor() as cursor:
        cursor.execute(SCHEMA_SQL_PATH.read_text(encoding="utf-8"))
    conn.commit()
