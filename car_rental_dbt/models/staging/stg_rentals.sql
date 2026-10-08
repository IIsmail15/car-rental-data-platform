with source as (
	select * from {{ source('staging', 'rentals') }}
)

select
	plate,
	pickup_date,
	dropoff_date,
	pickup_place,
	dropoff_place,
	miles
from source
