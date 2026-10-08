with source as (
  select * from {{ source('staging', 'drive') }}
)

select
  license_number,
  plate,
  pickup_date
from source
