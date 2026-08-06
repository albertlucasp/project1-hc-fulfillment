-- Business rule validated in docs/data_exploratory_2/advance_expore.md:
-- each main branch is expected to contain exactly 3 sub branches.
-- This test fails (returns rows) if any main branch has a sub branch count
-- other than 3.

select
    main_branch_name,
    count(distinct sub_branch_name) as sub_branch_count
from {{ source('raw', 'formation_level2') }}
group by main_branch_name
having count(distinct sub_branch_name) <> 3
