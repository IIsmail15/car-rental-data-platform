{{ config(materialized='table') }}

with drivers as (
    select * from {{ ref('stg_drivers') }}
)

select
    license_number as licensenumber,
    license_expiration as licenseexpiration,
    driver_name as drivername,
    birthdate
from drivers