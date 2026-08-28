-- Job title dimension. One row per canonical job title, with the org_level it belongs to.

with
source as (
    select distinct
        org_level,
        job_title
    from {{ ref('int_formation_unpivoted') }}

),

surrogate_keyed as (
    select
        {{ dbt_utils.generate_surrogate_key(['job_title']) }} as job_title_key,
        org_level,
        job_title
    from source
)

select * from surrogate_keyed
