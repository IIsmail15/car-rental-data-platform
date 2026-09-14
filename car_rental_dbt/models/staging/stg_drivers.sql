with source as (
    select * from {{ source('staging', 'drivers') }}
)

select
    licensenumber as license_number,
    licenseexpiration as license_expiration,
    drivername as driver_name,
    birthdate
from source
