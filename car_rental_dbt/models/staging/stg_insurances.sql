with source as (
	select * from {{ source('staging', 'insurances') }}
)

select
	risk,
	plate,
	pickupdate as pickup_date,
	cost
from source
