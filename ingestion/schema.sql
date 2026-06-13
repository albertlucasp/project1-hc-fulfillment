if not exists (select 1 from sys.schemas where name = 'raw')
    exec('create schema raw');

if not exists (select 1 from sys.schemas where name = 'audit')
    exec('create schema audit');

if object_id('audit.ingestion_runs', 'U') is null
begin
    create table audit.ingestion_runs (
        run_id uniqueidentifier not null primary key,
        source_name nvarchar(100) not null,
        target_table nvarchar(256) not null,
        source_file nvarchar(1000) not null,
        source_file_name nvarchar(255) not null,
        file_size_bytes bigint null,
        file_modified_at datetime2 null,
        row_count int not null default 0,
        status nvarchar(50) not null,
        started_at datetime2 not null,
        finished_at datetime2 null,
        error_message nvarchar(max) null
    );
end;

if object_id('audit.source_contract_checks', 'U') is null
begin
    create table audit.source_contract_checks (
        check_id bigint identity(1,1) not null primary key,
        run_id uniqueidentifier not null,
        source_name nvarchar(100) not null,
        source_file_name nvarchar(255) not null,
        check_name nvarchar(100) not null,
        status nvarchar(50) not null,
        expected_value nvarchar(max) null,
        actual_value nvarchar(max) null,
        checked_at datetime2 not null default sysdatetime()
    );
end;

if object_id('raw.master_data', 'U') is null
begin
    create table raw.master_data (
        snapshot_date date null,
        employee_id nvarchar(50) null,
        employee_name nvarchar(255) null,
        grade_level nvarchar(50) null,
        pay_grade nvarchar(50) null,
        job_code nvarchar(50) null,
        job_title nvarchar(255) null,
        position_code nvarchar(50) null,
        position_title nvarchar(500) null,
        area_code nvarchar(50) null,
        area_name nvarchar(255) null,
        subarea_code nvarchar(50) null,
        subarea_name nvarchar(255) null,
        org_unit_code nvarchar(100) null,
        org_unit_name nvarchar(500) null,
        employment_status_code nvarchar(50) null,
        employment_status_name nvarchar(100) null,
        employment_group_code nvarchar(50) null,
        employment_group_name nvarchar(100) null,
        employment_subgroup_code nvarchar(50) null,
        employment_subgroup_name nvarchar(100) null,
        gender nvarchar(50) null,
        birth_date nvarchar(50) null,
        birth_city nvarchar(100) null,
        entry_program_code nvarchar(50) null,
        entry_program_name nvarchar(100) null,
        tax_number nvarchar(50) null,
        marital_status nvarchar(50) null,
        dependent_count nvarchar(50) null,
        company_join_date nvarchar(50) null,
        termination_date nvarchar(50) null,
        source_file nvarchar(1000) not null,
        source_file_name nvarchar(255) not null,
        source_row_number int not null,
        loaded_at datetime2 not null default sysdatetime()
    );
end;

if object_id('raw.formation_level1', 'U') is null
begin
    create table raw.formation_level1 (
        main_branch_name nvarchar(255) null,
        [Main Branch CEO] nvarchar(50) null,
        [Vice President Director] nvarchar(50) null,
        [Main Branch Department A Head] nvarchar(50) null,
        [Main Branch Department B Head] nvarchar(50) null,
        [Main Branch Department C Head] nvarchar(50) null,
        formation_level int not null default 1,
        source_file nvarchar(1000) not null,
        source_file_name nvarchar(255) not null,
        source_row_number int not null,
        loaded_at datetime2 not null default sysdatetime()
    );
end;

if object_id('raw.formation_level2', 'U') is null
begin
    create table raw.formation_level2 (
        main_branch_name nvarchar(255) null,
        sub_branch_name nvarchar(255) null,
        [Sub Branch Leader] nvarchar(50) null,
        [Manager] nvarchar(50) null,
        [Assistant Manager] nvarchar(50) null,
        [Team Leader] nvarchar(50) null,
        formation_level int not null default 2,
        source_file nvarchar(1000) not null,
        source_file_name nvarchar(255) not null,
        source_row_number int not null,
        loaded_at datetime2 not null default sysdatetime()
    );
end;

if object_id('raw.formation_level3', 'U') is null
begin
    create table raw.formation_level3 (
        main_branch_name nvarchar(255) null,
        sub_branch_name nvarchar(255) null,
        branch_name nvarchar(255) null,
        [Supervisor] nvarchar(50) null,
        [Coordinator] nvarchar(50) null,
        [Senior Staff] nvarchar(50) null,
        [Junior Staff] nvarchar(50) null,
        [Associate Staff] nvarchar(50) null,
        formation_level int not null default 3,
        source_file nvarchar(1000) not null,
        source_file_name nvarchar(255) not null,
        source_row_number int not null,
        loaded_at datetime2 not null default sysdatetime()
    );
end;

if not exists (select 1 from sys.indexes where name = 'ix_raw_master_data_snapshot' and object_id = object_id('raw.master_data'))
    create index ix_raw_master_data_snapshot on raw.master_data (snapshot_date);

if not exists (select 1 from sys.indexes where name = 'ix_raw_master_data_source_file' and object_id = object_id('raw.master_data'))
    create index ix_raw_master_data_source_file on raw.master_data (source_file_name);

if not exists (select 1 from sys.indexes where name = 'ix_raw_formation_level1_source_file' and object_id = object_id('raw.formation_level1'))
    create index ix_raw_formation_level1_source_file on raw.formation_level1 (source_file_name);

if not exists (select 1 from sys.indexes where name = 'ix_raw_formation_level2_source_file' and object_id = object_id('raw.formation_level2'))
    create index ix_raw_formation_level2_source_file on raw.formation_level2 (source_file_name);

if not exists (select 1 from sys.indexes where name = 'ix_raw_formation_level3_source_file' and object_id = object_id('raw.formation_level3'))
    create index ix_raw_formation_level3_source_file on raw.formation_level3 (source_file_name);
