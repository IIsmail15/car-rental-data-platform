-- Each car and pickup date must identify exactly one fact row.
select
    car_plate,
    pickup_date,
    count(*) as row_count
from {{ ref('fact_rental') }}
group by car_plate, pickup_date
having count(*) > 1
