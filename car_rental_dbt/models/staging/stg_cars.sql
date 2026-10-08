with source as (
    select * from {{ source('staging', 'cars') }}
)

select
    plate,
    category,
    model,
    brand,
    fuel,
    registration_date
from source
