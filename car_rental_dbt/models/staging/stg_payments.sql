with source as (
	select * from {{ source('staging', 'payments') }}
)

select
	plate,
	pickupdate as pickup_date,
	amount,
	discount,
	paymentmode as payment_mode
from source
