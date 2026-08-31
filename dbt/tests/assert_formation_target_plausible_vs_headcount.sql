-- Data-quality guardrail, not a business rule: formation targets are
-- generated independently of actual headcount (generator/
-- generate_formation_data.py), per org unit and job title. If a level's
-- per-row target range isn't scaled against how many org units exist at
-- that level, the summed target can balloon far past anything the actual
-- workforce could ever fulfill - this is exactly what happened before
-- LEVEL3_FORMATION_TARGET_RANGE was introduced: 255 branch-level org units
-- alone summed to ~4,460 targets against a ~2,700-person company (~1.8x
-- overshoot). This test fails if total formation target exceeds 1.5x the
-- latest month's actual headcount, catching that class of calibration bug
-- before it reaches a dashboard.

with

latest_snapshot as (
    select max(snapshot_date) as snapshot_date
    from {{ ref('fct_headcount') }}
),

actual_headcount as (
    select count(distinct h.employee_id) as headcount
    from {{ ref('fct_headcount') }} h
    inner join latest_snapshot ls
        on h.snapshot_date = ls.snapshot_date
),

total_target as (
    select sum(target_count) as target_total
    from {{ ref('fct_formation') }}
)

select
    actual_headcount.headcount,
    total_target.target_total,
    total_target.target_total * 1.0 / actual_headcount.headcount as target_to_actual_ratio
from actual_headcount
cross join total_target
where total_target.target_total > actual_headcount.headcount * 1.5
