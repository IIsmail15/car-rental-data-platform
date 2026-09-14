with source as (
    select * from {{ source('staging', 'cars') }}
)

select
    plate,
    category,
    model,
    brand,
    fuel,
    registrationdate as registration_date
from source
