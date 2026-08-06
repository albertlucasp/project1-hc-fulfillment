-- Business rule validated in docs/data_exploratory_2/advance_expore.md:
-- a branch_name must always belong to exactly one (main_branch_name,
-- sub_branch_name) parent path. This test fails (returns rows) if any
-- branch_name is shared across more than one parent path.

select
    branch_name,
    count(distinct concat(main_branch_name, '|', sub_branch_name)) as parent_path_count
from {{ source('raw', 'formation_level3') }}
group by branch_name
having count(distinct concat(main_branch_name, '|', sub_branch_name)) <> 1
