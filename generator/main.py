from generator.config import (
    BRANCH,
    FORMATION_DIR,
    LEVEL1_JOBDESC,
    LEVEL2_JOBDESC,
    LEVEL3_JOBDESC,
    MAIN_BRANCH,
    MASTER_DATA_DIR,
    OUTPUT_DIR,
    SNAPSHOT_DATES,
    SNAPSHOT_ROW_MASTER,
    SUB_BRANCH,
)
from generator.generate_formation_data import generate_formation_data
from generator.generate_master_data import generate_master_data


def main() -> None:
    print("Synthetic HR Formation Fulfillment Generator")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Master Data Directory: {MASTER_DATA_DIR}")
    print(f"Formation Directory: {FORMATION_DIR}")
    print(f"Snapshots: {', '.join(SNAPSHOT_DATES)}")
    print(f"Snapshot Row Master: {', '.join([f'{date}: {rows}' for date, rows in SNAPSHOT_ROW_MASTER.items()])}")
    print(f"Main Branches: {', '.join(MAIN_BRANCH)}")
    print(f"Sub Branches: {', '.join(SUB_BRANCH)}")
    print(f"Branches: {', '.join(BRANCH)}")
    print(f"Level 1 Job Descriptions: {', '.join(LEVEL1_JOBDESC)}")
    print(f"Level 2 Job Descriptions: {', '.join(LEVEL2_JOBDESC)}")
    print(f"Level 3 Job Descriptions: {', '.join(LEVEL3_JOBDESC)}")

    written_files = generate_master_data()
    print(f"Generated {len(written_files)} master data files")
    for file_path in written_files:
        print(f"- {file_path}")

    formation_files = generate_formation_data()
    print(f"Generated {len(formation_files)} formation files")
    for file_path in formation_files:
        print(f"- {file_path}")


if __name__ == "__main__":
    main()
