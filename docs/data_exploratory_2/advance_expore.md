# Establish the raw-data grain
**exploratory via dbeaver-ce**
1. Inspect raw.master_data
    - schema properties :
    ![raw.master schema properties](images/Screenshot%202026-06-20%20153558.png)

    - sql syntax :
    ```sql
    select * from raw.master_data md ORDER by md.snapshot_date ;
    select count(*) from raw.master_data md ;
    select 
        md.snapshot_date,
        count(*) as total_records 
    from raw.master_data md
    group by md.snapshot_date;
    select snapshot_date, employee_id from raw.master_data md
    group by md.snapshot_date , md.employee_id 
    having count(*) > 1;

    select count(*) as null_count from raw.master_data md 
    where md.snapshot_date IS null or md.employee_id is null;

    select distinct employment_status_code,
    employment_status_name from raw.master_data md ;

    select count(distinct employee_id) from raw.master_data md ;

    select employment_status_name ,job_title from raw.master_data where employment_status_code in ('L', 'M')

    --prove how many employees appear in more than one monthly snapshot
    select count(*) as employees_in_multiple_snapshots
    from (
        select employee_id
        from raw.master_data
        group by employee_id
        having count(distinct snapshot_date) > 1
    ) as repeated_employees;

    --inspect several employee histories across snapshots
    select
        employee_id,
        snapshot_date,
        employment_status_code,
        employment_status_name,
        org_unit_code,
        org_unit_name,
        job_title
    from raw.master_data
    where employee_id in (
        select top 5 employee_id
        from raw.master_data
        group by employee_id
        having count(distinct snapshot_date) > 1
        order by count(distinct snapshot_date) desc, employee_id
    )
    order by employee_id, snapshot_date;
    ```

    ## summary
    1. grain : one employee in one monthly snapshot
    2. total records = 32,006 for 12 across full year
    3. no duplicates & null values for (snapshot_date, employee_id) -> key candidate
    4. 3,131 employees appear in more than 1 snapshot
    5. 3,183 distinct employees acrros full year
    6. Long Leave and Retirement Preparation involved to headcount calculation because the employee still occupy formation posistion

2. inspect raw.formation_level1, raw.formation_level2, raw.formation_level3
    - schema properties :
    ![schema properties formation_level1](images/Screenshot%202026-06-20%20171356.png)
    ![schema properties formation_level2](images/Screenshot%202026-06-20%20171502.png)
    ![schema properties formation_level3](images/Screenshot%202026-06-20%20171346.png)
    - sql syntax :
    ```sql
    --expected rows
    select count(*) from raw.formation_level1 fl;
    select count(*) from raw.formation_level2 fl;
    select count(*) from raw.formation_level3 fl;

    --candidate key uniqueness
    --Zero returned rows means no duplicate candidate keys were found.
    select main_branch_name, count(*) as record_count
    from raw.formation_level1
    group by main_branch_name
    having count(*) > 1;

    select main_branch_name, sub_branch_name, count(*) as record_count
    from raw.formation_level2
    group by main_branch_name, sub_branch_name
    having count(*) > 1;

    select main_branch_name, sub_branch_name, branch_name, count(*) as record_count
    from raw.formation_level3
    group by main_branch_name, sub_branch_name, branch_name
    having count(*) > 1;

    --candidate key not null or blank
    --NULLIF changes an empty string to NULL after surrounding spaces are removed.
    select count(*) as invalid_key_count
    from raw.formation_level1
    where nullif(ltrim(rtrim(main_branch_name)), '') is null;

    select count(*) as invalid_key_count
    from raw.formation_level2
    where nullif(ltrim(rtrim(main_branch_name)), '') is null
       or nullif(ltrim(rtrim(sub_branch_name)), '') is null;

    select count(*) as invalid_key_count
    from raw.formation_level3
    where nullif(ltrim(rtrim(main_branch_name)), '') is null
       or nullif(ltrim(rtrim(sub_branch_name)), '') is null
       or nullif(ltrim(rtrim(branch_name)), '') is null;

    --physical SQL data type
    --This describes storage only. It does not prove that the values are numeric.
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'raw'
      AND table_name = 'formation_level1'
    ORDER BY ordinal_position;

    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'raw'
      AND table_name = 'formation_level2'
    ORDER BY ordinal_position;

    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'raw'
      AND table_name = 'formation_level3'
    ORDER BY ordinal_position;

    --semantic target-value checks for level 1
    --CROSS APPLY temporarily turns target columns into rows for profiling.
    select
        target.job_title,
        count(*) as inspected_values,
        sum(case
            when nullif(ltrim(rtrim(target.target_value)), '') is null then 1
            else 0
        end) as null_or_blank_count,
        sum(case
            when nullif(ltrim(rtrim(target.target_value)), '') is not null
             and try_convert(int, ltrim(rtrim(target.target_value))) is null then 1
            else 0
        end) as non_numeric_count,
        sum(case
            when try_convert(int, ltrim(rtrim(target.target_value))) = 0 then 1
            else 0
        end) as zero_count,
        sum(case
            when try_convert(int, ltrim(rtrim(target.target_value))) < 0 then 1
            else 0
        end) as negative_count
    from raw.formation_level1 as fl
    cross apply (
        values
            ('Main Branch CEO', fl.[Main Branch CEO]),
            ('Vice President Director', fl.[Vice President Director]),
            ('Main Branch Department A Head', fl.[Main Branch Department A Head]),
            ('Main Branch Department B Head', fl.[Main Branch Department B Head]),
            ('Main Branch Department C Head', fl.[Main Branch Department C Head])
    ) as target(job_title, target_value)
    group by target.job_title
    order by target.job_title;

    --semantic target-value checks for level 2
    select
        target.job_title,
        count(*) as inspected_values,
        sum(case
            when nullif(ltrim(rtrim(target.target_value)), '') is null then 1
            else 0
        end) as null_or_blank_count,
        sum(case
            when nullif(ltrim(rtrim(target.target_value)), '') is not null
             and try_convert(int, ltrim(rtrim(target.target_value))) is null then 1
            else 0
        end) as non_numeric_count,
        sum(case
            when try_convert(int, ltrim(rtrim(target.target_value))) = 0 then 1
            else 0
        end) as zero_count,
        sum(case
            when try_convert(int, ltrim(rtrim(target.target_value))) < 0 then 1
            else 0
        end) as negative_count
    from raw.formation_level2 as fl
    cross apply (
        values
            ('Sub Branch Leader', fl.[Sub Branch Leader]),
            ('Manager', fl.[Manager]),
            ('Assistant Manager', fl.[Assistant Manager]),
            ('Team Leader', fl.[Team Leader])
    ) as target(job_title, target_value)
    group by target.job_title
    order by target.job_title;

    --semantic target-value checks for level 3
    select
        target.job_title,
        count(*) as inspected_values,
        sum(case
            when nullif(ltrim(rtrim(target.target_value)), '') is null then 1
            else 0
        end) as null_or_blank_count,
        sum(case
            when nullif(ltrim(rtrim(target.target_value)), '') is not null
             and try_convert(int, ltrim(rtrim(target.target_value))) is null then 1
            else 0
        end) as non_numeric_count,
        sum(case
            when try_convert(int, ltrim(rtrim(target.target_value))) = 0 then 1
            else 0
        end) as zero_count,
        sum(case
            when try_convert(int, ltrim(rtrim(target.target_value))) < 0 then 1
            else 0
        end) as negative_count
    from raw.formation_level3 as fl
    cross apply (
        values
            ('Supervisor', fl.[Supervisor]),
            ('Coordinator', fl.[Coordinator]),
            ('Senior Staff', fl.[Senior Staff]),
            ('Junior Staff', fl.[Junior Staff]),
            ('Associate Staff', fl.[Associate Staff])
    ) as target(job_title, target_value)
    group by target.job_title
    order by target.job_title;

    --A returned row means one sub-branch name has ambiguous main-branch parents.
    select
        sub_branch_name,
        count(distinct main_branch_name) as parent_main_branch_count
    from raw.formation_level2
    group by sub_branch_name
    having count(distinct main_branch_name) <> 1;

    --A returned row means one branch name has ambiguous parent paths.
    select
        branch_name,
        count(distinct concat(main_branch_name, '|', sub_branch_name)) as parent_path_count
    from raw.formation_level3
    group by branch_name
    having count(distinct concat(main_branch_name, '|', sub_branch_name)) <> 1;

    --Each main branch is expected to contain three sub-branches.
    select
        main_branch_name,
        count(distinct sub_branch_name) as sub_branch_count
    from raw.formation_level2
    group by main_branch_name
    having count(distinct sub_branch_name) <> 3;

    --Each sub-branch is expected to contain five branches.
    select
        main_branch_name,
        sub_branch_name,
        count(distinct branch_name) as branch_count
    from raw.formation_level3
    group by main_branch_name, sub_branch_name
    having count(distinct branch_name) <> 5;
    ```

    ## formation summary to complete after running the queries
    1. `formation_level1` grain: formation target for one main branch
    2. `formation_level1` candidate key: main_branch_name
    3. `formation_level1` row count: 17
    4. `formation_level1` target columns:5
    5. `formation_level2` grain: formation target for one sub branch within a main branch
    6. `formation_level2` candidate key: main_branch_name + sub_branch_name
    7. `formation_level2` row count: 51
    8. `formation_level2` target columns: 4
    9. `formation_level3` grain: formation target for one branch within a sub branch
    10. `formation_level3` candidate key: main_branch_name + sub_branch_name + branch_name
    11. `formation_level3` row count: 255
    12. `formation_level3` target columns: 5
    13. Null or blank target findings: Pass
    14. Non-numeric target findings: Pass
    15. Zero target findings: Pass
    16. Negative target findings: Pass
    17. Hierarchy ambiguity findings: Pass

    ```text
    level 1 = source rows x target columns = 85
    level 2 = source rows x target columns = 204
    level 3 = source rows x target columns = 1,275
    total = 1,564
    ```
