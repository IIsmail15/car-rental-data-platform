{{ config(materialized='table') }}

with rental_dates as (
    select distinct pickup_date as date_value
    from {{ ref('stg_rentals') }}
)

select
    date_value,
    year(date_value) as year,
    month(date_value) as month,
    dayofmonth(date_value) as day,
    dayofweek(date_value) - 1 as weekday,
    quarter(date_value) as quarter,
    weekofyear(date_value) as week_of_year,
    dayofweek(date_value) in (1, 7) as is_weekend
from rental_dates