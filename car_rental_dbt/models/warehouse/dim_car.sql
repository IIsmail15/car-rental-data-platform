{{ config(materialized='table') }}

with cars as (
    select * from {{ source('staging', 'cars') }}
),

optionals as (
    select
        plate,
        string_agg(optional, ', ') as optional
    from {{ source('staging', 'have_optional') }}
    group by plate
)

select
    cars.plate,
    cars.category,
    cars.model,
    cars.brand,
    cars.fuel,
    cars.registrationdate,
    optionals.optional
from cars
left join optionals on cars.plate = optionals.plate