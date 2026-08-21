with source as (
    select *
    from {{ source('raw', 'formation_level1') }}
),

renamed as (
    select
    --identifier
        cast(nullif(trim(main_branch_name), '') as varchar(255)) as main_branch_name,

    --formation targets (by job title)
        cast([Main Branch CEO] as int) as main_branch_ceo,
        cast([Vice President Director] as int) as vice_president_director,
        cast([Main Branch Department A Head] as int) as main_branch_department_a_head,
        cast([Main Branch Department B Head] as int) as main_branch_department_b_head,
        cast([Main Branch Department C Head] as int) as main_branch_department_c_head,

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
