from datetime import date, datetime, timedelta
from pathlib import Path
import csv
import random

from generator.config import (
    EMPLOYEE_PROFILES,
    FORMATION_DIR,
    LEVEL1_JOBDESC,
    LEVEL2_JOBDESC,
    LEVEL3_JOBDESC,
    MASTER_DATA_DIR,
    MONTHLY_PROMOTION_RATE,
    MONTHLY_STATUS_CHANGE_RATE,
    MONTHLY_TERMINATION_RATE,
    MONTHLY_TRANSFER_RATE,
    SEED,
    SNAPSHOT_DATES,
    SNAPSHOT_ROW_MASTER,
)
from generator.org_structure import build_org_structure
from generator.source_messiness import (
    maybe_blank,
    messy_date,
    messy_gender,
    messy_job_title,
    messy_org_name,
)


FIRST_NAMES = [
    "Adi",
    "Ayu",
    "Bima",
    "Citra",
    "Dewi",
    "Eka",
    "Fajar",
    "Gita",
    "Hana",
    "Indra",
    "Joko",
    "Lestari",
    "Maya",
    "Nanda",
    "Putra",
    "Rani",
    "Sari",
    "Teguh",
    "Utami",
    "Wahyu",
    "Muhammad",
    "Agus",
    "Siti",
]

LAST_NAMES = [
    "Pratama",
    "Saputra",
    "Wijaya",
    "Putra",
    "Santoso",
    "Permata",
    "Laksana",
    "Mahendra",
    "Kusuma",
    "Purnama",
    "Anggraini",
    "Hidayat",
    "Nugroho",
    "Sari",
    "Wibowo",
    "Yuliana",
    "Fauzi",
    "Safitri",
    "Ramadhan",
]

BIRTH_CITIES = [
    "Jakarta",
    "Bandung",
    "Semarang",
    "Surabaya",
    "Medan",
    "Makassar",
    "Pontianak",
    "Jayapura",
    "Denpasar",
    "Yogyakarta",
    "Palembang",
    "Jambi",
    "Padang",
    "Bekasi",
]

MARITAL_STATUS = ["Single", "Married", "Divorced"]

MASTER_DATA_COLUMNS = [
    "employee_id",
    "employee_name",
    "grade_level",
    "pay_grade",
    "job_code",
    "job_title",
    "position_code",
    "position_title",
    "area_code",
    "area_name",
    "subarea_code",
    "subarea_name",
    "org_unit_code",
    "org_unit_name",
    "employment_status_code",
    "employment_status_name",
    "employment_group_code",
    "employment_group_name",
    "employment_subgroup_code",
    "employment_subgroup_name",
    "gender",
    "birth_date",
    "birth_city",
    "entry_program_code",
    "entry_program_name",
    "tax_number",
    "marital_status",
    "dependent_count",
    "company_join_date",
    "termination_date",
]


def snapshot_token(snapshot_date: str) -> str:
    """Convert 2025-01-01 -> 01Jan25 for the raw source filename."""
    return datetime.strptime(snapshot_date, "%Y-%m-%d").strftime("%d%b%y")


def parse_snapshot(snapshot_date: str) -> date:
    return datetime.strptime(snapshot_date, "%Y-%m-%d").date()


def job_titles_for_level(org_source_level: int) -> list[str]:
    if org_source_level == 1:
        return LEVEL1_JOBDESC
    if org_source_level == 2:
        return LEVEL2_JOBDESC
    return LEVEL3_JOBDESC


def random_date_between(rng: random.Random, start: date, end: date) -> date:
    day_span = max((end - start).days, 1)
    return start + timedelta(days=rng.randint(0, day_span))


def choose_profile(rng: random.Random) -> dict[str, object]:
    weights = [int(profile["weight"]) for profile in EMPLOYEE_PROFILES]
    return rng.choices(EMPLOYEE_PROFILES, weights=weights, k=1)[0]


def assign_org_and_job(
    employee: dict[str, object],
    org_unit: dict[str, object],
    rng: random.Random,
) -> None:
    org_level = int(org_unit["org_source_level"])
    job_title = rng.choice(job_titles_for_level(org_level))

    employee["job_title"] = job_title
    employee["position_title"] = f"{job_title} - {org_unit['org_unit_name']}"
    employee["area_code"] = org_unit["area_code"]
    employee["area_name"] = org_unit["area_name"]
    employee["subarea_code"] = org_unit["subarea_code"]
    employee["subarea_name"] = org_unit["subarea_name"]
    employee["org_unit_code"] = org_unit["org_unit_code"]
    employee["org_unit_name"] = org_unit["org_unit_name"]


def make_employee(
    employee_number: int,
    snapshot: date,
    rng: random.Random,
    org_units: list[dict[str, object]],
) -> dict[str, object]:
    profile = choose_profile(rng)
    min_age, max_age = profile["age_range"]  # type: ignore[index]
    min_grade, max_grade = profile["grade_range"]  # type: ignore[index]
    entry_code, entry_name = profile["entry_program"]  # type: ignore[index]
    group_code, group_name, subgroup_code, subgroup_name = profile["employment_group"]  # type: ignore[index]

    birth_date = random_date_between(
        rng,
        date(snapshot.year - max_age, 1, 1),
        date(snapshot.year - min_age, 12, 31),
    )
    company_join_date = random_date_between(rng, date(snapshot.year - 25, 1, 1), snapshot)
    grade_number = rng.randint(min_grade, max_grade)

    employee = {
        "employee_id": f"E{employee_number:08d}",
        "employee_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        "grade_level": f"G{grade_number:02d}",
        "pay_grade": f"P{min(max(grade_number - 1, 1), 8):02d}",
        "job_code": f"J{rng.randint(100000, 999999)}",
        "position_code": f"PST{rng.randint(100000, 999999)}",
        "employment_status_code": "A",
        "employment_status_name": "Active",
        "employment_group_code": group_code,
        "employment_group_name": group_name,
        "employment_subgroup_code": subgroup_code,
        "employment_subgroup_name": subgroup_name,
        "gender": rng.choice(["Male", "Female"]),
        "birth_date": birth_date,
        "birth_city": rng.choice(BIRTH_CITIES),
        "entry_program_code": entry_code,
        "entry_program_name": entry_name,
        "tax_number": str(rng.randint(10**14, 10**15 - 1)),
        "marital_status": rng.choice(MARITAL_STATUS),
        "dependent_count": rng.randint(0, 5),
        "company_join_date": company_join_date,
        "termination_date": None,
        "profile_name": profile["name"],
    }
    assign_org_and_job(employee, rng.choice(org_units), rng)
    return employee


def terminate_employee(employee: dict[str, object], snapshot: date) -> dict[str, object]:
    terminated = employee.copy()
    terminated["employment_status_code"] = "T"
    terminated["employment_status_name"] = "Terminated"
    terminated["termination_date"] = snapshot
    return terminated


def transfer_employee(
    employee: dict[str, object],
    org_units: list[dict[str, object]],
    rng: random.Random,
) -> None:
    current_org = employee["org_unit_code"]
    candidates = [unit for unit in org_units if unit["org_unit_code"] != current_org]
    assign_org_and_job(employee, rng.choice(candidates), rng)


def promote_employee(employee: dict[str, object], rng: random.Random) -> None:
    current_grade = int(str(employee["grade_level"])[1:])
    new_grade = min(current_grade + rng.choice([1, 1, 2]), 10)
    employee["grade_level"] = f"G{new_grade:02d}"
    employee["pay_grade"] = f"P{min(max(new_grade - 1, 1), 8):02d}"
    employee["position_code"] = f"PST{rng.randint(100000, 999999)}"


def change_status(employee: dict[str, object], rng: random.Random) -> None:
    status_options = [
        ("A", "Active"),
        ("L", "Long Leave"),
        ("M", "Retirement Preparation"),
    ]
    code, name = rng.choice(status_options)
    employee["employment_status_code"] = code
    employee["employment_status_name"] = name


def sample_indexes(rng: random.Random, roster_size: int, rate: float) -> set[int]:
    if roster_size == 0:
        return set()
    count = max(int(roster_size * rate), 1)
    return set(rng.sample(range(roster_size), min(count, roster_size)))


def apply_monthly_events(
    active_roster: list[dict[str, object]],
    snapshot: date,
    rng: random.Random,
    org_units: list[dict[str, object]],
) -> list[dict[str, object]]:
    terminated_this_month: list[dict[str, object]] = []
    terminate_indexes = sample_indexes(rng, len(active_roster), MONTHLY_TERMINATION_RATE)
    transfer_indexes = sample_indexes(rng, len(active_roster), MONTHLY_TRANSFER_RATE)
    promotion_indexes = sample_indexes(rng, len(active_roster), MONTHLY_PROMOTION_RATE)
    status_indexes = sample_indexes(rng, len(active_roster), MONTHLY_STATUS_CHANGE_RATE)

    survivors = []
    for index, employee in enumerate(active_roster):
        if index in terminate_indexes:
            terminated_this_month.append(terminate_employee(employee, snapshot))
            continue

        if index in transfer_indexes:
            transfer_employee(employee, org_units, rng)
        if index in promotion_indexes:
            promote_employee(employee, rng)
        if index in status_indexes:
            change_status(employee, rng)
        elif employee["employment_status_code"] != "A" and rng.random() < 0.55:
            employee["employment_status_code"] = "A"
            employee["employment_status_name"] = "Active"

        survivors.append(employee)

    active_roster[:] = survivors
    return terminated_this_month


def export_employee(employee: dict[str, object], rng: random.Random) -> dict[str, object]:
    job_title = messy_job_title(str(employee["job_title"]), rng)
    org_name = messy_org_name(str(employee["org_unit_name"]), rng)
    area_name = messy_org_name(str(employee["area_name"]), rng)
    subarea_name = messy_org_name(str(employee["subarea_name"]), rng)

    return {
        "employee_id": employee["employee_id"],
        "employee_name": employee["employee_name"],
        "grade_level": maybe_blank(employee["grade_level"], rng, rate=0.025),
        "pay_grade": maybe_blank(employee["pay_grade"], rng, rate=0.025),
        "job_code": employee["job_code"],
        "job_title": job_title,
        "position_code": employee["position_code"],
        "position_title": f"{job_title} - {org_name}",
        "area_code": employee["area_code"],
        "area_name": area_name,
        "subarea_code": employee["subarea_code"],
        "subarea_name": subarea_name,
        "org_unit_code": employee["org_unit_code"],
        "org_unit_name": org_name,
        "employment_status_code": employee["employment_status_code"],
        "employment_status_name": employee["employment_status_name"],
        "employment_group_code": employee["employment_group_code"],
        "employment_group_name": employee["employment_group_name"],
        "employment_subgroup_code": employee["employment_subgroup_code"],
        "employment_subgroup_name": employee["employment_subgroup_name"],
        "gender": messy_gender(str(employee["gender"]), rng),
        "birth_date": messy_date(employee["birth_date"], rng, blank_rate=0.01),  # type: ignore[arg-type]
        "birth_city": maybe_blank(employee["birth_city"], rng, rate=0.03),
        "entry_program_code": employee["entry_program_code"],
        "entry_program_name": employee["entry_program_name"],
        "tax_number": employee["tax_number"],
        "marital_status": employee["marital_status"],
        "dependent_count": employee["dependent_count"],
        "company_join_date": messy_date(employee["company_join_date"], rng),  # type: ignore[arg-type]
        "termination_date": messy_date(employee["termination_date"], rng),  # type: ignore[arg-type]
    }


def write_snapshot(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=MASTER_DATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def generate_master_data() -> list[Path]:
    MASTER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    FORMATION_DIR.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)
    org_units = build_org_structure()
    active_roster: list[dict[str, object]] = []
    next_employee_number = 1
    written_files: list[Path] = []

    for snapshot_date in SNAPSHOT_DATES:
        snapshot = parse_snapshot(snapshot_date)
        target_rows = SNAPSHOT_ROW_MASTER[snapshot_date]
        terminated_this_month = []

        if active_roster:
            terminated_this_month = apply_monthly_events(active_roster, snapshot, rng, org_units)

        while len(active_roster) + len(terminated_this_month) < target_rows:
            active_roster.append(make_employee(next_employee_number, snapshot, rng, org_units))
            next_employee_number += 1

        rows = [export_employee(employee, rng) for employee in active_roster + terminated_this_month]
        rng.shuffle(rows)

        output_path = MASTER_DATA_DIR / f"report_Master Data_{snapshot_token(snapshot_date)}.csv"
        write_snapshot(output_path, rows)
        written_files.append(output_path)

    return written_files


if __name__ == "__main__":
    for file_path in generate_master_data():
        print(file_path)
