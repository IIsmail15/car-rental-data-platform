{{ config(materialized='table') }}

with cars as (
    select * from {{ ref('stg_cars') }}
),

optionals as (
    select
        plate,
        string_agg(optional, ', ') as optional
    from {{ ref('stg_have_optional') }}
    group by plate
)

select
    cars.plate,
    cars.category,
    cars.model,
    cars.brand,
    cars.fuel,
    cars.registration_date,
    optionals.optional
from cars
left join optionals on cars.plate = optionals.plate