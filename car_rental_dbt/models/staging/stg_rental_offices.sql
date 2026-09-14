with source as (
	select * from {{ source('staging', 'rental_offices') }}
)

select
	officename as office_name,
	city,
	area,
	state,
	country
from source
