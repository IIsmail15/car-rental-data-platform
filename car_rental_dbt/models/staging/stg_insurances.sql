with source as (
	select * from {{ source('staging', 'insurances') }}
)

select
	risk,
	plate,
	pickup_date,
	cost
from source
