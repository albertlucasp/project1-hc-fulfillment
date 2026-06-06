from pathlib import Path
import csv
import random

from generator.config import (
    FORMATION_DIR,
    LEVEL1_JOBDESC,
    LEVEL2_JOBDESC,
    LEVEL3_JOBDESC,
    SEED,
)
from generator.org_structure import build_org_structure


FORMATION_FILES = {
    1: "Formation Main Branch.csv",
    2: "Formation Sub Branch.csv",
    3: "Formation Branch.csv",
}


def target_for_job(level: int, job_title: str, rng: random.Random) -> int:
    if level == 1:
        if "CEO" in job_title or "Head" in job_title:
            return rng.choice([1, 1, 1, 2])
        return rng.randint(2, 6)
    if level == 2:
        if "Leader" in job_title or "Manager" in job_title:
            return rng.choice([1, 1, 2])
        return rng.randint(2, 8)
    return rng.randint(1, 6)


def job_titles_for_level(level: int) -> list[str]:
    if level == 1:
        return LEVEL1_JOBDESC
    if level == 2:
        return LEVEL2_JOBDESC
    return LEVEL3_JOBDESC


def identifier_columns_for_level(level: int) -> list[str]:
    if level == 1:
        return ["main_branch_name"]
    if level == 2:
        return ["main_branch_name", "sub_branch_name"]
    return ["main_branch_name", "sub_branch_name", "branch_name"]


def formation_row(org_unit: dict[str, object], level: int, rng: random.Random) -> dict[str, object]:
    row = {
        "main_branch_name": org_unit["main_branch_name"],
        "sub_branch_name": org_unit["sub_branch_name"],
        "branch_name": org_unit["branch_name"],
    }
    for job_title in job_titles_for_level(level):
        row[job_title] = target_for_job(level, job_title, rng)
    return row


def write_formation_file(path: Path, rows: list[dict[str, object]], level: int) -> None:
    columns = identifier_columns_for_level(level) + job_titles_for_level(level)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate_formation_data() -> list[Path]:
    FORMATION_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED + 99)
    org_units = build_org_structure()
    written_files = []

    for level, file_name in FORMATION_FILES.items():
        rows = [
            formation_row(org_unit, level, rng)
            for org_unit in org_units
            if int(org_unit["org_source_level"]) == level
        ]
        path = FORMATION_DIR / file_name
        write_formation_file(path, rows, level)
        written_files.append(path)

    return written_files


if __name__ == "__main__":
    for file_path in generate_formation_data():
        print(file_path)
