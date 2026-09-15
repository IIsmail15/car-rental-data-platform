{{ config(materialized='table') }}

with offices as (
    select * from {{ ref('stg_rental_offices') }}
)

select
    office_name as officename,
    city,
    area,
    state,
    country
from offices