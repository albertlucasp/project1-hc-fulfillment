from generator.config import BRANCH, MAIN_BRANCH, SUB_BRANCH


def build_org_structure() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    for main_idx, main_branch in enumerate(MAIN_BRANCH, start=1):
        main_code = f"MB{main_idx:03d}"

        records.append(
            {
                "org_source_level": 1,
                "area_code": main_code,
                "area_name": main_branch,
                "subarea_code": main_code,
                "subarea_name": main_branch,
                "org_unit_code": main_code,
                "org_unit_name": main_branch,
                "main_branch_name": main_branch,
                "sub_branch_name": None,
                "branch_name": None,
            }
        )

        for sub_idx, sub_branch in enumerate(SUB_BRANCH, start=1):
            sub_code = f"{main_code}-SB{sub_idx:02d}"
            sub_name = f"{main_branch} - {sub_branch}"

            records.append(
                {
                    "org_source_level": 2,
                    "area_code": main_code,
                    "area_name": main_branch,
                    "subarea_code": sub_code,
                    "subarea_name": sub_name,
                    "org_unit_code": sub_code,
                    "org_unit_name": sub_name,
                    "main_branch_name": main_branch,
                    "sub_branch_name": sub_name,
                    "branch_name": None,
                }
            )

            for branch_idx, branch in enumerate(BRANCH, start=1):
                branch_code = f"{sub_code}-BR{branch_idx:02d}"
                branch_name = f"{sub_name} - {branch}"

                records.append(
                    {
                        "org_source_level": 3,
                        "area_code": main_code,
                        "area_name": main_branch,
                        "subarea_code": sub_code,
                        "subarea_name": sub_name,
                        "org_unit_code": branch_code,
                        "org_unit_name": branch_name,
                        "main_branch_name": main_branch,
                        "sub_branch_name": sub_name,
                        "branch_name": branch_name,
                    }
                )

    return records
