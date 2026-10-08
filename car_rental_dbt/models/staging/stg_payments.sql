with source as (
	select * from {{ source('staging', 'payments') }}
)

select
	plate,
	pickup_date,
	amount,
	discount,
    payment_mode
from source
