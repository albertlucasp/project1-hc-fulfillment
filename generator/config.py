from pathlib import Path

SEED = 42
OUTPUT_DIR = Path("data/raw")
MASTER_DATA_DIR = OUTPUT_DIR / "master_data"
FORMATION_DIR = OUTPUT_DIR / "formation"

SNAPSHOT_ROW_MASTER = {
    "2025-01-01": 2500,
    "2025-02-01": 2540,
    "2025-03-01": 2514,
    "2025-04-01": 2590,
    "2025-05-01": 2676,
    "2025-06-01": 2666,
    "2025-07-01": 2697,
    "2025-08-01": 2690,
    "2025-09-01": 2726,
    "2025-10-01": 2775,
    "2025-11-01": 2809,
    "2025-12-01": 2823,
}

SNAPSHOT_DATES = list(SNAPSHOT_ROW_MASTER.keys())

MAIN_BRANCH = [
    "R01 Sumatera Utara",
    "R02 Sumatera Barat",
    "R03 Sumatera Tengah",
    "R04 Kalimantan Utara",
    "R05 Kalimantan Tengah",
    "R06 Kalimantan Selatan",
    "R07 Sulawesi Utara",
    "R08 Sulawesi Tengah",
    "R09 Sulawesi Selatan",
    "R10 Papua Barat",
    "R11 Papua Tengah",
    "R12 Papua Selatan",
    "R13 Semarang",
    "R14 DKI Jakarta",
    "R15 Jawa Tengah",
    "R16 Jawa Barat",
    "R17 Jawa Timur",
]

SUB_BRANCH = [
    "Sub Branch A",
    "Sub Branch B",
    "Sub Branch C",
]

BRANCH = [
    "Branch 1",
    "Branch 2",
    "Branch 3",
    "Branch 4",
    "Branch 5",
]

LEVEL1_JOBDESC = [
    "Main Branch CEO",
    "Vice President Director",
    "Main Branch Department A Head",
    "Main Branch Department B Head",
    "Main Branch Department C Head",
]

LEVEL2_JOBDESC = [
    "Sub Branch Leader",
    "Manager",
    "Assistant Manager",
    "Team Leader",
]

LEVEL3_JOBDESC = [
    "Supervisor",
    "Coordinator",
    "Senior Staff",
    "Junior Staff",
    "Associate Staff",
]

MONTHLY_TERMINATION_RATE = 0.014
MONTHLY_TRANSFER_RATE = 0.030
MONTHLY_PROMOTION_RATE = 0.012
MONTHLY_STATUS_CHANGE_RATE = 0.006
SOURCE_MESSINESS_RATE = 0.075

EMPLOYEE_PROFILES = [
    {
        "name": "regular_staff",
        "weight": 58,
        "age_range": (25, 48),
        "grade_range": (3, 7),
        "employment_group": ("PERM", "Permanent Employee", "REG", "Regular Staff"),
        "entry_program": ("REG", "Regular Hiring"),
    },
    {
        "name": "management",
        "weight": 12,
        "age_range": (35, 57),
        "grade_range": (7, 10),
        "employment_group": ("PERM", "Permanent Employee", "MGT", "Management"),
        "entry_program": ("EXP", "Experienced Professional"),
    },
    {
        "name": "trainee",
        "weight": 10,
        "age_range": (22, 28),
        "grade_range": (1, 3),
        "employment_group": ("TRN", "Trainee", "DEV", "Development Program"),
        "entry_program": ("GDP", "Graduate Development Program"),
    },
    {
        "name": "contract",
        "weight": 12,
        "age_range": (23, 45),
        "grade_range": (2, 6),
        "employment_group": ("CONT", "Contract Employee", "OPS", "Operations"),
        "entry_program": ("REG", "Regular Hiring"),
    },
    {
        "name": "outsourced",
        "weight": 8,
        "age_range": (21, 50),
        "grade_range": (1, 4),
        "employment_group": ("OUT", "Outsourced", "EXT", "External Workforce"),
        "entry_program": ("EXP", "Experienced Professional"),
    },
]
