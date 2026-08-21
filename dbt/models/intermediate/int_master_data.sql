with source as (
    select * from {{ ref('stg_master_data') }}
),

-- keep only what feeds actual headcount, and drop permanent exits.
base as (
    select
        snapshot_date,
        employee_id,
        job_title,
        area_code,
        area_name,
        subarea_code,
        subarea_name,
        org_unit_code,
        org_unit_name
    from source
    where employment_status_code in ('A', 'L', 'M')
),

-- clean job_title: undo known abbreviations/casing.
transform_job_title as (
    select
        snapshot_date,
        employee_id,
        area_code,
        area_name,
        subarea_code,
        subarea_name,
        org_unit_code,
        org_unit_name,
        case upper(trim(job_title))
            when 'MAIN BRANCH CEO' then 'Main Branch CEO'
            when 'VICE PRESIDENT DIRECTOR' then 'Vice President Director'
            when 'COORD' then 'Coordinator'
            when 'COORDINATOR' then 'Coordinator'
            when 'SUB BRANCH LEADER' then 'Sub Branch Leader'
            when 'TEAM LEADER' then 'Team Leader'
            when 'TL' then 'Team Leader'
            when 'SENIOR STAFF' then 'Senior Staff'
            when 'SR STAFF' then 'Senior Staff'
            when 'ASSISTANT MANAGER' then 'Assistant Manager'
            when 'ASST MANAGER' then 'Assistant Manager'
            when 'MANAGER' then 'Manager'
            when 'MGR' then 'Manager'
            when 'SUPERVISOR' then 'Supervisor'
            when 'SPV' then 'Supervisor'
            when 'MAIN BRANCH DEPARTMENT A HEAD' then 'Main Branch Department A Head'
            when 'MAIN BRANCH DEPARTMENT B HEAD' then 'Main Branch Department B Head'
            when 'MAIN BRANCH DEPARTMENT C HEAD' then 'Main Branch Department C Head'
            when 'JUNIOR STAFF' then 'Junior Staff'
            when 'JR STAFF' then 'Junior Staff'
            when 'ASSOCIATE STAFF' then 'Associate Staff'
            when 'ASSOC STAFF' then 'Associate Staff'
            else trim(job_title)
        end as job_title
    from base
),

-- derive org_level (1/2/3) from the now-clean job_title
with_level as(
    select *,
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
    from transform_job_title
),

-- cleaning area_name
cleaned_area_names as(
    select
        *
    from (
        select
            area_code,
            area_name COLLATE Latin1_General_CS_AS as area_name,
            row_number() over (partition by area_code order by count(*) desc) as rn
        from with_level
        group by area_code, area_name COLLATE Latin1_General_CS_AS
    ) as ranked
    where rn = 1
),

-- cleaning subarea_name
cleaned_subarea_names as(
    select
        *
    from (
        select
            subarea_code,
            subarea_name COLLATE Latin1_General_CS_AS as subarea_name,
            row_number() over (partition by subarea_code order by count(*) desc) as rn
        from with_level
        group by subarea_code, subarea_name COLLATE Latin1_General_CS_AS
    ) as ranked
    where rn = 1
),

-- cleaning org_unit_name
cleaned_org_unit_names as(
    select
        *
    from (
        select
            org_unit_code,
            org_unit_name COLLATE Latin1_General_CS_AS as org_unit_name,
            row_number() over (partition by org_unit_code order by count(*) desc) as rn
        from with_level
        group by org_unit_code, org_unit_name COLLATE Latin1_General_CS_AS
    ) as ranked
    where rn = 1
),

combined as(
    select
        wl.snapshot_date,
        wl.employee_id,
        wl.job_title,
        wl.area_code,
        can_area.area_name as area_name,
        wl.subarea_code,
        can_subarea.subarea_name as subarea_name,
        wl.org_unit_code,
        can_org_unit.org_unit_name as org_unit_name,
        wl.org_level
    from with_level wl
    left join cleaned_area_names can_area
        on wl.area_code = can_area.area_code
    left join cleaned_subarea_names can_subarea
        on wl.subarea_code = can_subarea.subarea_code
    left join cleaned_org_unit_names can_org_unit
        on wl.org_unit_code = can_org_unit.org_unit_code
),

repivoted as (
    select
        snapshot_date,
        employee_id,
        job_title,
        area_code,
        area_name,
        subarea_code,
        subarea_name,
        org_unit_code,
        org_unit_name,
        org_level,
        area_name as main_branch_name,
        case when org_level in (2, 3) then subarea_name else null end as sub_branch_name,
        case when org_level = 3 then org_unit_name else null end as branch_name
    from combined
)

select * from repivoted
