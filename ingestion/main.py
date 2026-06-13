from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import csv
import re
import traceback

from ingestion.database import connect, ensure_database_exists, initialize_database
from ingestion.source_contracts import SOURCE_CONTRACTS, SourceContract


SNAPSHOT_PATTERN = re.compile(r"(\d{2})([A-Za-z]{3})(\d{2})")
MONTH_MAP = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def split_table_name(table_name: str) -> tuple[str, str]:
    schema_name, relation_name = table_name.split(".", maxsplit=1)
    return schema_name, relation_name


def quote_identifier(identifier: str) -> str:
    return f"[{identifier.replace(']', ']]')}]"


def table_identifier(table_name: str) -> str:
    schema_name, relation_name = split_table_name(table_name)
    return f"{quote_identifier(schema_name)}.{quote_identifier(relation_name)}"


def extract_snapshot_date(path: Path) -> str | None:
    match = SNAPSHOT_PATTERN.search(path.name)
    if not match:
        return None

    day, month, year = match.groups()
    month_number = MONTH_MAP.get(month.lower())
    if not month_number:
        return None
    return f"20{year}-{month_number}-{day}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames or []), rows


def contract_check_rows(
    run_id: str,
    contract: SourceContract,
    path: Path,
    actual_columns: list[str],
    row_count: int,
) -> list[tuple[object, ...]]:
    expected_columns = list(contract.expected_columns)
    missing_columns = [column for column in expected_columns if column not in actual_columns]
    unexpected_columns = [column for column in actual_columns if column not in expected_columns]
    checks = [
        (
            run_id,
            contract.source_name,
            path.name,
            "required_columns_present",
            "pass" if not missing_columns else "fail",
            ",".join(expected_columns),
            ",".join(actual_columns),
        ),
        (
            run_id,
            contract.source_name,
            path.name,
            "no_unexpected_columns",
            "pass" if not unexpected_columns else "fail",
            "",
            ",".join(unexpected_columns),
        ),
        (
            run_id,
            contract.source_name,
            path.name,
            "has_rows",
            "pass" if row_count > 0 else "fail",
            ">0",
            str(row_count),
        ),
    ]

    if contract.snapshot_from_filename:
        snapshot_date = extract_snapshot_date(path)
        checks.append(
            (
                run_id,
                contract.source_name,
                path.name,
                "snapshot_date_from_filename",
                "pass" if snapshot_date else "fail",
                "DDMonYY token",
                snapshot_date or "",
            )
        )

    return checks


def insert_contract_checks(conn, checks: list[tuple[object, ...]]) -> None:
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            insert into audit.source_contract_checks (
                run_id,
                source_name,
                source_file_name,
                check_name,
                status,
                expected_value,
                actual_value
            )
            values (%s, %s, %s, %s, %s, %s, %s)
            """,
            checks,
        )


def fail_if_contract_failed(checks: list[tuple[object, ...]]) -> None:
    failed = [check for check in checks if check[4] == "fail"]
    if failed:
        names = ", ".join(str(check[3]) for check in failed)
        raise ValueError(f"Source contract failed: {names}")


def delete_existing_source_rows(conn, contract: SourceContract, path: Path) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            f"delete from {table_identifier(contract.target_table)} where source_file_name = %s",
            (path.name,),
        )


def insert_rows(conn, contract: SourceContract, path: Path, rows: list[dict[str, str]]) -> int:
    base_columns = list(contract.expected_columns)
    metadata_columns = ["source_file", "source_file_name", "source_row_number"]
    extra_columns = []
    if contract.snapshot_from_filename:
        extra_columns.append("snapshot_date")
    if contract.formation_level is not None:
        extra_columns.append("formation_level")

    insert_columns = base_columns + extra_columns + metadata_columns
    placeholder_sql = ", ".join(["%s"] * len(insert_columns))
    column_sql = ", ".join(quote_identifier(column) for column in insert_columns)
    statement = (
        f"insert into {table_identifier(contract.target_table)} "
        f"({column_sql}) values ({placeholder_sql})"
    )

    snapshot_date = extract_snapshot_date(path) if contract.snapshot_from_filename else None
    values = []
    for row_number, row in enumerate(rows, start=2):
        record = [row.get(column, "") for column in base_columns]
        if contract.snapshot_from_filename:
            record.append(snapshot_date)
        if contract.formation_level is not None:
            record.append(contract.formation_level)
        record.extend([str(path), path.name, row_number])
        values.append(record)

    if values:
        with conn.cursor() as cursor:
            cursor.executemany(statement, values)
    return len(values)


def insert_ingestion_run(
    conn,
    *,
    run_id: str,
    contract: SourceContract,
    path: Path,
    row_count: int,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    error_message: str | None = None,
) -> None:
    stat = path.stat()
    file_modified_at = datetime.fromtimestamp(stat.st_mtime)
    with conn.cursor() as cursor:
        cursor.execute(
            """
            insert into audit.ingestion_runs (
                run_id,
                source_name,
                target_table,
                source_file,
                source_file_name,
                file_size_bytes,
                file_modified_at,
                row_count,
                status,
                started_at,
                finished_at,
                error_message
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                run_id,
                contract.source_name,
                contract.target_table,
                str(path),
                path.name,
                stat.st_size,
                file_modified_at,
                row_count,
                status,
                started_at.replace(tzinfo=None),
                finished_at.replace(tzinfo=None),
                error_message,
            ),
        )


def matching_files(contract: SourceContract) -> list[Path]:
    return sorted(contract.source_dir.glob(contract.path_glob))


def ingest_file(conn, contract: SourceContract, path: Path) -> int:
    run_id = str(uuid4())
    started_at = utc_now()
    row_count = 0

    try:
        actual_columns, rows = read_csv_rows(path)
        checks = contract_check_rows(run_id, contract, path, actual_columns, len(rows))
        insert_contract_checks(conn, checks)
        conn.commit()
        fail_if_contract_failed(checks)

        delete_existing_source_rows(conn, contract, path)
        row_count = insert_rows(conn, contract, path, rows)
        insert_ingestion_run(
            conn,
            run_id=run_id,
            contract=contract,
            path=path,
            row_count=row_count,
            status="success",
            started_at=started_at,
            finished_at=utc_now(),
        )
        conn.commit()
        print(f"Loaded {contract.target_table} from {path.name}: {row_count} rows")
        return row_count
    except Exception as exc:
        conn.rollback()
        insert_ingestion_run(
            conn,
            run_id=run_id,
            contract=contract,
            path=path,
            row_count=row_count,
            status="failed",
            started_at=started_at,
            finished_at=utc_now(),
            error_message=f"{exc}\n{traceback.format_exc(limit=3)}",
        )
        conn.commit()
        raise


def ingest_all_sources() -> None:
    ensure_database_exists()
    with connect() as conn:
        initialize_database(conn)

        total_files = 0
        total_rows = 0
        for contract in SOURCE_CONTRACTS:
            files = matching_files(contract)
            if not files:
                raise FileNotFoundError(f"No files matched contract {contract.source_name}: {contract.path_glob}")

            for path in files:
                total_rows += ingest_file(conn, contract, path)
                total_files += 1

        print(f"Ingestion complete: {total_files} files, {total_rows} rows")


if __name__ == "__main__":
    ingest_all_sources()
