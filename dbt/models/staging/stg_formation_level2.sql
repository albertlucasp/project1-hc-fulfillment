with source as (
    select *
    from {{ source('raw', 'formation_level2') }}
),

renamed as (
    select
    --identifier
        cast(nullif(trim(main_branch_name), '') as varchar(255)) as main_branch_name,
        cast(nullif(trim(sub_branch_name), '') as varchar(255)) as sub_branch_name,

    --formation targets (by job title)
        cast([Sub Branch Leader] as int) as sub_branch_leader,
        cast([Manager] as int) as manager,
        cast([Assistant Manager] as int) as assistant_manager,
        cast([Team Leader] as int) as team_leader,

    --hierarchy metadata
        formation_level,

    --metadata
        source_file,
        source_file_name,
        source_row_number,
        loaded_at
    from source
)

select * from renamed