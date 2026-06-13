from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


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


FORMATION_LEVEL1_COLUMNS = [
    "main_branch_name",
    "Main Branch CEO",
    "Vice President Director",
    "Main Branch Department A Head",
    "Main Branch Department B Head",
    "Main Branch Department C Head",
]


FORMATION_LEVEL2_COLUMNS = [
    "main_branch_name",
    "sub_branch_name",
    "Sub Branch Leader",
    "Manager",
    "Assistant Manager",
    "Team Leader",
]


FORMATION_LEVEL3_COLUMNS = [
    "main_branch_name",
    "sub_branch_name",
    "branch_name",
    "Supervisor",
    "Coordinator",
    "Senior Staff",
    "Junior Staff",
    "Associate Staff",
]


@dataclass(frozen=True)
class SourceContract:
    source_name: str
    target_table: str
    path_glob: str
    expected_columns: tuple[str, ...]
    primary_key: tuple[str, ...]
    source_type: str
    snapshot_from_filename: bool = False
    formation_level: int | None = None

    @property
    def source_dir(self) -> Path:
        return RAW_DATA_DIR


SOURCE_CONTRACTS = (
    SourceContract(
        source_name="master_data",
        target_table="raw.master_data",
        path_glob="master_data/report_Master Data_*.csv",
        expected_columns=tuple(MASTER_DATA_COLUMNS),
        primary_key=("snapshot_date", "employee_id"),
        source_type="monthly_snapshot",
        snapshot_from_filename=True,
    ),
    SourceContract(
        source_name="formation_level1",
        target_table="raw.formation_level1",
        path_glob="formation/Formation Main Branch.csv",
        expected_columns=tuple(FORMATION_LEVEL1_COLUMNS),
        primary_key=("source_file_name", "main_branch_name"),
        source_type="formation_target",
        formation_level=1,
    ),
    SourceContract(
        source_name="formation_level2",
        target_table="raw.formation_level2",
        path_glob="formation/Formation Sub Branch.csv",
        expected_columns=tuple(FORMATION_LEVEL2_COLUMNS),
        primary_key=("source_file_name", "main_branch_name", "sub_branch_name"),
        source_type="formation_target",
        formation_level=2,
    ),
    SourceContract(
        source_name="formation_level3",
        target_table="raw.formation_level3",
        path_glob="formation/Formation Branch.csv",
        expected_columns=tuple(FORMATION_LEVEL3_COLUMNS),
        primary_key=("source_file_name", "main_branch_name", "sub_branch_name", "branch_name"),
        source_type="formation_target",
        formation_level=3,
    ),
)
