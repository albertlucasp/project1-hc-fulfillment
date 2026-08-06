-- Business rule validated in docs/data_exploratory_2/advance_expore.md:
-- each sub branch is expected to contain exactly 5 branches.
-- This test fails (returns rows) if any (main_branch_name, sub_branch_name)
-- pair has a branch count other than 5.

select
    main_branch_name,
    sub_branch_name,
    count(distinct branch_name) as branch_count
from {{ source('raw', 'formation_level3') }}
group by main_branch_name, sub_branch_name
having count(distinct branch_name) <> 5
