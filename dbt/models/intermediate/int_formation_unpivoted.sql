-- Reshapes formation targets from "wide" (one column per job title) into
-- "long" format (one row per org unit + job title + target_count).
--
-- Why this model exists: stg_formation_level1/2/3 have one row per org unit
-- with job titles spread across columns. stg_master_data has one row per
-- employee, with job_title as a VALUE in a single column. Those two shapes
-- cannot be compared or joined directly. This model reshapes the formation
-- side so it matches the "long" shape of the employee side - that is what
-- makes fct_fulfillment_rate possible later.
--
-- org_level tells you which org-unit grain a given job title's target
-- applies to:
--   1 = main_branch, 2 = sub_branch, 3 = branch
-- sub_branch_name / branch_name are null when not applicable at that level
-- (e.g. a level-1 target like "Main Branch CEO" has no sub_branch/branch).

with level1 as (
    select
        1 as org_level,
        main_branch_name,
        cast(null as varchar) as sub_branch_name,
        cast(null as varchar) as branch_name,
        'Main Branch CEO' as job_title,
        main_branch_ceo as target_count
    from {{ ref('stg_formation_level1') }}

    union all

    select
        1 as org_level,
        main_branch_name,
        cast(null as varchar) as sub_branch_name,
        cast(null as varchar) as branch_name,
        'Vice President Director' as job_title,
        vice_president_director as target_count
    from {{ ref('stg_formation_level1') }}

    union all

    select
        1 as org_level,
        main_branch_name,
        cast(null as varchar) as sub_branch_name,
        cast(null as varchar) as branch_name,
        'Main Branch Department A Head' as job_title,
        main_branch_department_a_head as target_count
    from {{ ref('stg_formation_level1') }}

    union all

    select
        1 as org_level,
        main_branch_name,
        cast(null as varchar) as sub_branch_name,
        cast(null as varchar) as branch_name,
        'Main Branch Department B Head' as job_title,
        main_branch_department_b_head as target_count
    from {{ ref('stg_formation_level1') }}

    union all

    select
        1 as org_level,
        main_branch_name,
        cast(null as varchar) as sub_branch_name,
        cast(null as varchar) as branch_name,
        'Main Branch Department C Head' as job_title,
        main_branch_department_c_head as target_count
    from {{ ref('stg_formation_level1') }}
),

level2 as (
    select
        2 as org_level,
        main_branch_name,
        sub_branch_name,
        cast(null as varchar) as branch_name,
        'Sub Branch Leader' as job_title,
        sub_branch_leader as target_count
    from {{ ref('stg_formation_level2') }}

    union all

    select
        2 as org_level,
        main_branch_name,
        sub_branch_name,
        cast(null as varchar) as branch_name,
        'Manager' as job_title,
        manager as target_count
    from {{ ref('stg_formation_level2') }}

    union all

    select
        2 as org_level,
        main_branch_name,
        sub_branch_name,
        cast(null as varchar) as branch_name,
        'Assistant Manager' as job_title,
        assistant_manager as target_count
    from {{ ref('stg_formation_level2') }}

    union all

    select
        2 as org_level,
        main_branch_name,
        sub_branch_name,
        cast(null as varchar) as branch_name,
        'Team Leader' as job_title,
        team_leader as target_count
    from {{ ref('stg_formation_level2') }}
),

level3 as (
    select
        3 as org_level,
        main_branch_name,
        sub_branch_name,
        branch_name,
        'Supervisor' as job_title,
        supervisor as target_count
    from {{ ref('stg_formation_level3') }}

    union all

    select
        3 as org_level,
        main_branch_name,
        sub_branch_name,
        branch_name,
        'Coordinator' as job_title,
        coordinator as target_count
    from {{ ref('stg_formation_level3') }}

    union all

    select
        3 as org_level,
        main_branch_name,
        sub_branch_name,
        branch_name,
        'Senior Staff' as job_title,
        senior_staff as target_count
    from {{ ref('stg_formation_level3') }}

    union all

    select
        3 as org_level,
        main_branch_name,
        sub_branch_name,
        branch_name,
        'Junior Staff' as job_title,
        junior_staff as target_count
    from {{ ref('stg_formation_level3') }}

    union all

    select
        3 as org_level,
        main_branch_name,
        sub_branch_name,
        branch_name,
        'Associate Staff' as job_title,
        associate_staff as target_count
    from {{ ref('stg_formation_level3') }}
),

unioned as (
    select * from level1
    union all
    select * from level2
    union all
    select * from level3
)

select * from unioned
