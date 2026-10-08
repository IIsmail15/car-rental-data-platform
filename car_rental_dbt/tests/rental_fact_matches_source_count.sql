-- Compare current counts, rather than hard-coding the sample's 200 rentals.
with source_count as (
    select count(*) as source_rows
    from {{ ref('stg_rentals') }}
),

fact_count as (
    select count(*) as fact_rows
    from {{ ref('fact_rental') }}
)

select
    source_rows,
    fact_rows
from source_count
cross join fact_count
where source_rows <> fact_rows
