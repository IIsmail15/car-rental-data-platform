{{ config(materialized='table') }}

with rental_dates as (
    select distinct pickupdate as date_value
    from {{ source('staging', 'rentals') }}
)

select
    date_value,
    extract(year from date_value)::int        as year,
    extract(month from date_value)::int       as month,
    extract(day from date_value)::int         as day,
    extract(dow from date_value)::int         as weekday,
    extract(quarter from date_value)::int     as quarter,
    extract(week from date_value)::int        as week_of_year,
    case when extract(dow from date_value) in (0, 6) 
         then true else false end             as is_weekend
from rental_dates