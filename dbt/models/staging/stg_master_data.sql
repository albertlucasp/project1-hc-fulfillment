with source as (
    select *
    from {{ source('raw', 'master_data') }}
),

renamed as (
    select
    --identifier
        cast(snapshot_date as date) as snapshot_date,
        cast(nullif(trim(employee_id), '') as varchar(50)) as employee_id,

    --employee information
        cast(nullif(trim(employee_name), '') as varchar(255)) as employee_name,
        cast(nullif(trim(grade_level), '') as varchar(50)) as grade_level,
        cast(nullif(trim(pay_grade), '') as varchar(50)) as pay_grade,
        cast(nullif(upper(trim(job_code)), '') as varchar(50)) as job_code,
        cast(nullif(trim(job_title), '') as varchar(255)) as job_title,
        cast(nullif(upper(trim(position_code)), '') as varchar(50)) as position_code,
        cast(nullif(trim(position_title), '') as varchar(500)) as position_title,
        cast(nullif(upper(trim(area_code)), '') as varchar(50)) as area_code,
        cast(nullif(trim(area_name), '') as varchar(255)) as area_name,
        cast(nullif(upper(trim(subarea_code)), '') as varchar(50)) as subarea_code,
        cast(nullif(trim(subarea_name), '') as varchar(255)) as subarea_name,
        cast(nullif(upper(trim(org_unit_code)), '') as varchar(100)) as org_unit_code,
        cast(nullif(trim(org_unit_name), '') as varchar(500)) as org_unit_name,
        cast(nullif(upper(trim(employment_status_code)), '') as varchar(50)) as employment_status_code,
        cast(nullif(trim(employment_status_name), '') as varchar(100)) as employment_status_name,
        cast(nullif(trim(employment_group_code), '') as varchar(50)) as employment_group_code,
        cast(nullif(trim(employment_group_name), '') as varchar(100)) as employment_group_name,
        cast(nullif(upper(trim(employment_subgroup_code)), '') as varchar(50)) as employment_subgroup_code,
        cast(nullif(trim(employment_subgroup_name), '') as varchar(100)) as employment_subgroup_name,
        cast(nullif(trim(gender), '') as varchar(50)) as gender,
        nullif(trim(birth_date), '') as birth_date,
        cast(nullif(trim(birth_city), '') as varchar(100)) as birth_city,
        cast(nullif(trim(entry_program_code), '') as varchar(50)) as entry_program_code,
        cast(nullif(trim(entry_program_name), '') as varchar(100)) as entry_program_name,
        cast(nullif(trim(tax_number), '') as varchar(50)) as tax_number,
        cast(nullif(trim(marital_status), '') as varchar(50)) as marital_status,
        cast(nullif(trim(dependent_count), '') as smallint) as dependent_count,
        nullif(trim(company_join_date), '') as company_join_date,
        nullif(trim(termination_date), '') as termination_date,
    
    --metadata
        source_file,
        source_file_name,
        source_row_number,
        loaded_at
    from source
)

select * from renamed