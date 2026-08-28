-- Org hierarchy dimension. One row per distinct org node (org_level + main_branch_name + sub_branch_name + branch_name), sourced from BOTH
-- int_master_data (actual headcount) and int_formation_unpivoted (formation targets).

with

master_data_org as (
    select distinct
        org_level,
        main_branch_name,
        sub_branch_name,
        branch_name
    from {{ ref('int_master_data') }}
),

formation_org as (
    select distinct
        org_level,
        main_branch_name COLLATE Latin1_General_CS_AS as main_branch_name,
        sub_branch_name COLLATE Latin1_General_CS_AS as sub_branch_name,
        branch_name COLLATE Latin1_General_CS_AS as branch_name
    from {{ ref('int_formation_unpivoted') }}
),

all_org_nodes as (
    select * from master_data_org
    union
    select * from formation_org

),

surrogate_keyed as (
    select
        {{ dbt_utils.generate_surrogate_key(['org_level', 'main_branch_name', 'sub_branch_name', 'branch_name']) }} as org_key,
        org_level,
        main_branch_name,
        sub_branch_name,
        branch_name
    from all_org_nodes
)

select * from surrogate_keyed
