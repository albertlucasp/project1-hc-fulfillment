-- Business rule validated in docs/data_exploratory_2/advance_expore.md:
-- a sub_branch_name must always belong to exactly one main_branch_name.
-- This test fails (returns rows) if any sub_branch_name is shared across
-- more than one main branch.

select
    sub_branch_name,
    count(distinct main_branch_name) as parent_main_branch_count
from {{ source('raw', 'formation_level2') }}
group by sub_branch_name
having count(distinct main_branch_name) <> 1
