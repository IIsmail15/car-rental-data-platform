with source as (
  select * from {{ source('staging', 'drive') }}
)

select
  licensenumber as license_number,
  plate,
  pickupdate as pickup_date
from source
