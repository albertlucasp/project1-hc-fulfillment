-- Formation target fact. One row per org node + job title (same grain as int_formation_unpivoted)
with

formation as (
    select * from {{ ref('int_formation_unpivoted') }}
),

org as (
    select * from {{ ref('dim_org') }}
),

job_title as (
    select * from {{ ref('dim_job_title') }}
),

final as (
    select
        o.org_key,
        f.job_title COLLATE Latin1_General_CS_AS as job_title,
        jt.job_title_key,
        target_count
    from formation f
    left join org o
        on f.org_level = o.org_level
        and f.main_branch_name COLLATE Latin1_General_CS_AS = o.main_branch_name
        and coalesce(f.sub_branch_name, '') COLLATE Latin1_General_CS_AS = coalesce(o.sub_branch_name, '')
        and coalesce(f.branch_name, '') COLLATE Latin1_General_CS_AS = coalesce(o.branch_name, '')
    left join job_title jt
        on f.org_level = jt.org_level
        and f.job_title = jt.job_title
)

select * from final
