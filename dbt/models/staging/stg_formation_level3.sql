with source as (
    select *
    from {{ source('raw', 'formation_level3') }}
),

renamed as (
    select
    --identifier
        cast(nullif(trim(main_branch_name), '') as varchar) as main_branch_name,
        cast(nullif(trim(sub_branch_name), '') as varchar) as sub_branch_name,
        cast(nullif(trim(branch_name), '') as varchar) as branch_name,

    --formation targets (by job title)
        cast([Supervisor] as int) as supervisor,
        cast([Coordinator] as int) as coordinator,
        cast([Senior Staff] as int) as senior_staff,
        cast([Junior Staff] as int) as junior_staff,
        cast([Associate Staff] as int) as associate_staff,

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

