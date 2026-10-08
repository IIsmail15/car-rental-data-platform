with source as (
    select * from {{ source('staging', 'drivers') }}
)

select
    license_number,
    license_expiration,
    driver_name,
    birth_date
from source
