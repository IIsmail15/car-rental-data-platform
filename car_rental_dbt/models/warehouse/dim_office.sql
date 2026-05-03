{{ config(materialized='table') }}

with offices as (
    select * from {{ source('staging', 'rental_offices') }}
)

select
    officename,
    city,
    area,
    state,
    country
from offices