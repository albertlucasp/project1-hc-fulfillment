with source as (
    select *
    from {{ source('raw', 'master_data') }}
),

renamed as (
    select
    --identifier
        cast(snapshot_date as date) as snapshot_date,
        cast(nullif(trim(employee_id), '') as varchar) as employee_id,

    --employee information
        cast(nullif(trim(employee_name), '') as varchar) as employee_name,
        cast(nullif(trim(grade_level), '') as varchar) as grade_level,
        cast(nullif(trim(pay_grade), '') as varchar) as pay_grade,
        cast(nullif(upper(trim(job_code)), '') as varchar) as job_code,
        cast(nullif(trim(job_title), '') as varchar) as job_title,
        cast(nullif(upper(trim(position_code)), '') as varchar) as position_code,
        cast(nullif(trim(position_title), '') as varchar) as position_title,
        cast(nullif(upper(trim(area_code)), '') as varchar) as area_code,
        cast(nullif(trim(area_name), '') as varchar) as area_name,
        cast(nullif(upper(trim(subarea_code)), '') as varchar) as subarea_code,
        cast(nullif(trim(subarea_name), '') as varchar) as subarea_name,
        cast(nullif(upper(trim(org_unit_code)), '') as varchar) as org_unit_code,
        cast(nullif(trim(org_unit_name), '') as varchar) as org_unit_name,
        cast(nullif(upper(trim(employment_status_code)), '') as varchar) as employment_status_code,
        cast(nullif(trim(employment_status_name), '') as varchar) as employment_status_name,
        cast(nullif(trim(employment_group_code), '') as varchar) as employment_group_code,
        cast(nullif(trim(employment_group_name), '') as varchar) as employment_group_name,
        cast(nullif(upper(trim(employment_subgroup_code)), '') as varchar) as employment_subgroup_code,
        cast(nullif(trim(employment_subgroup_name), '') as varchar) as employment_subgroup_name,
        cast(nullif(trim(gender), '') as varchar) as gender,
        nullif(trim(birth_date), '') as birth_date,
        cast(nullif(trim(birth_city), '') as varchar) as birth_city,
        cast(nullif(trim(entry_program_code), '') as varchar) as entry_program_code,
        cast(nullif(trim(entry_program_name), '') as varchar) as entry_program_name,
        cast(nullif(trim(tax_number), '') as varchar) as tax_number,
        cast(nullif(trim(marital_status), '') as varchar) as marital_status,
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