with source as (
    select * from {{ source('staging', 'have_optional') }}
)

select
    plate,
    optional
from source
