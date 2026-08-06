-- The missing link between stg_master_data (one row per employee, messy org
-- names, no main/sub/branch columns) and int_formation_unpivoted (clean,
-- long-format targets keyed by main_branch_name/sub_branch_name/branch_name).
--
-- Two problems solved here:
--
-- 1. stg_master_data has no main_branch_name/sub_branch_name/branch_name
--    columns - only area_name/subarea_name/org_unit_name, whose meaning
--    depends on the employee's own org_level:
--      org_level 1 -> area_name = subarea_name = org_unit_name = main branch
--      org_level 2 -> area_name = main branch, subarea_name = org_unit_name = sub branch
--      org_level 3 -> area_name = main branch, subarea_name = sub branch, org_unit_name = branch
--    org_level itself isn't a column either - it's derived here from
--    job_title, since job titles never overlap across levels.
--
-- 2. area_name/subarea_name/org_unit_name/job_title are messy in ~7.5% of
--    rows (typos, abbreviations, inconsistent casing). The org_*_code
--    columns are never messy, so for each code we pick whichever name is
--    observed most often for that code as the canonical value - this
--    self-heals the messy minority without hardcoding every typo pattern.
--    job_title has no equivalent stable code to anchor on, so it is instead
--    cleaned with an explicit mapping of the known messy variants back to
--    the 14 canonical titles.

with source as (
    select * from {{ ref('stg_master_data') }}
),

base as (
    select
        snapshot_date,
        employee_id,
        employment_status_code,
        employment_status_name,
        area_code,
        area_name as raw_area_name,
        subarea_code,
        subarea_name as raw_subarea_name,
        org_unit_code,
        org_unit_name as raw_org_unit_name,

        -- clean job_title: undo known abbreviations and stray uppercasing
        case upper(trim(job_title))
            when 'MAIN BRANCH CEO' then 'Main Branch CEO'
            when 'VICE PRESIDENT DIRECTOR' then 'Vice President Director'
            when 'MAIN BRANCH DEPARTMENT A HEAD' then 'Main Branch Department A Head'
            when 'MAIN BRANCH DEPARTMENT B HEAD' then 'Main Branch Department B Head'
            when 'MAIN BRANCH DEPARTMENT C HEAD' then 'Main Branch Department C Head'
            when 'SUB BRANCH LEADER' then 'Sub Branch Leader'
            when 'MANAGER' then 'Manager'
            when 'MGR' then 'Manager'
            when 'ASSISTANT MANAGER' then 'Assistant Manager'
            when 'ASST MANAGER' then 'Assistant Manager'
            when 'TEAM LEADER' then 'Team Leader'
            when 'TL' then 'Team Leader'
            when 'SUPERVISOR' then 'Supervisor'
            when 'SPV' then 'Supervisor'
            when 'COORDINATOR' then 'Coordinator'
            when 'COORD' then 'Coordinator'
            when 'SENIOR STAFF' then 'Senior Staff'
            when 'SR STAFF' then 'Senior Staff'
            when 'JUNIOR STAFF' then 'Junior Staff'
            when 'JR STAFF' then 'Junior Staff'
            when 'ASSOCIATE STAFF' then 'Associate Staff'
            when 'ASSOC STAFF' then 'Associate Staff'
            else trim(job_title)
        end as job_title
    from source
),

-- derive each employee's own hierarchy level from their (now clean) job_title
with_level as (
    select
        *,
        case job_title
            when 'Main Branch CEO' then 1
            when 'Vice President Director' then 1
            when 'Main Branch Department A Head' then 1
            when 'Main Branch Department B Head' then 1
            when 'Main Branch Department C Head' then 1
            when 'Sub Branch Leader' then 2
            when 'Manager' then 2
            when 'Assistant Manager' then 2
            when 'Team Leader' then 2
            when 'Supervisor' then 3
            when 'Coordinator' then 3
            when 'Senior Staff' then 3
            when 'Junior Staff' then 3
            when 'Associate Staff' then 3
        end as org_level
    from base
),

-- canonical name per code = whichever name is observed most often for that
-- code (self-heals the messy ~7.5% minority)
area_name_counts as (
    select area_code, raw_area_name, count(*) as name_count
    from with_level
    group by area_code, raw_area_name
),
area_name_lookup as (
    select area_code, raw_area_name as canonical_area_name
    from (
        select
            area_code,
            raw_area_name,
            row_number() over (
                partition by area_code
                order by name_count desc, raw_area_name asc
            ) as rn
        from area_name_counts
    ) ranked
    where rn = 1
),

subarea_name_counts as (
    select subarea_code, raw_subarea_name, count(*) as name_count
    from with_level
    group by subarea_code, raw_subarea_name
),
subarea_name_lookup as (
    select subarea_code, raw_subarea_name as canonical_subarea_name
    from (
        select
            subarea_code,
            raw_subarea_name,
            row_number() over (
                partition by subarea_code
                order by name_count desc, raw_subarea_name asc
            ) as rn
        from subarea_name_counts
    ) ranked
    where rn = 1
),

org_unit_name_counts as (
    select org_unit_code, raw_org_unit_name, count(*) as name_count
    from with_level
    group by org_unit_code, raw_org_unit_name
),
org_unit_name_lookup as (
    select org_unit_code, raw_org_unit_name as canonical_org_unit_name
    from (
        select
            org_unit_code,
            raw_org_unit_name,
            row_number() over (
                partition by org_unit_code
                order by name_count desc, raw_org_unit_name asc
            ) as rn
        from org_unit_name_counts
    ) ranked
    where rn = 1
),

final as (
    select
        wl.snapshot_date,
        wl.employee_id,
        wl.employment_status_code,
        wl.employment_status_name,
        wl.org_level,
        wl.job_title,

        -- area_name is always the main branch, regardless of the
        -- employee's own org_level
        al.canonical_area_name as main_branch_name,

        -- sub_branch only means something at org_level 2 or 3
        case
            when wl.org_level in (2, 3) then sl.canonical_subarea_name
        end as sub_branch_name,

        -- branch only means something at org_level 3
        case
            when wl.org_level = 3 then ol.canonical_org_unit_name
        end as branch_name

    from with_level as wl
    inner join area_name_lookup as al on wl.area_code = al.area_code
    inner join subarea_name_lookup as sl on wl.subarea_code = sl.subarea_code
    inner join org_unit_name_lookup as ol on wl.org_unit_code = ol.org_unit_code
)

select * from final
