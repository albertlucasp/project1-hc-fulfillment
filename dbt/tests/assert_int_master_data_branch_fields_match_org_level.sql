-- Business rule from how int_master_data derives sub_branch_name/branch_name:
--   org_level 1 -> sub_branch_name and branch_name must both be null
--   org_level 2 -> sub_branch_name must be populated, branch_name must be null
--   org_level 3 -> sub_branch_name and branch_name must both be populated
-- Any row that violates this means the org_level -> field derivation logic
-- in int_master_data.sql is broken. This is a cross-column invariant that
-- no stock generic test covers, so it's written here as a singular test.

select
    employee_id,
    snapshot_date,
    org_level,
    sub_branch_name,
    branch_name
from {{ ref('int_master_data') }}
where
    (org_level = 1 and (sub_branch_name is not null or branch_name is not null))
    or (org_level = 2 and (sub_branch_name is null or branch_name is not null))
    or (org_level = 3 and (sub_branch_name is null or branch_name is null))
