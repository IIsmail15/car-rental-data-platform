{{ config(materialized='table') }}

with drivers as (
    select * from {{ source('staging', 'drivers') }}
)

select
    licensenumber,
    licenseexpiration,
    drivername,
    birthdate
from drivers