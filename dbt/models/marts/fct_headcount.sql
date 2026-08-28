-- Actual headcount fact. One row per employee per snapshot_date (same grain as int_master_data)

with

master_data as (
    select * from {{ ref('int_master_data') }}
),

org as (
    select * from {{ ref('dim_org') }}
),

job_title as (
    select * from {{ ref('dim_job_title') }}
),

joined_org as (
    select
        md.*,
        o.org_key
    from master_data md
    left join org o
        on md.org_level = o.org_level
        and md.main_branch_name = o.main_branch_name
        and coalesce(md.sub_branch_name, '') = coalesce(o.sub_branch_name, '')
        and coalesce(md.branch_name, '') = coalesce(o.branch_name, '')
),

final as (
    select
        snapshot_date,
        employee_id,
        employment_status_code,
        employment_status_name,
        jo.org_key,
        jo.job_title,
        jt.job_title_key
    from joined_org jo
    left join job_title jt
        on jo.org_level = jt.org_level
        and jo.job_title = jt.job_title
)

select * from final
