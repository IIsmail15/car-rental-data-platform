with source as (
	select * from {{ source('staging', 'rentals') }}
)

select
	plate,
	pickupdate as pickup_date,
	dropoffdate as dropoff_date,
	pickupplace as pickup_place,
	dropoffplace as dropoff_place,
	miles
from source
