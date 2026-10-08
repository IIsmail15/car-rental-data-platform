-- A singular dbt test returns the rows that violate its rule.
select
    car_plate,
    pickup_date,
    dropoff_date
from {{ ref('fact_rental') }}
where pickup_date is null
   or dropoff_date is null
   or dropoff_date <= pickup_date
