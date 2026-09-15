{{ config(materialized='table') }}

with rentals as (
    select * from {{ ref('stg_rentals') }}
),

payments as (
    select * from {{ ref('stg_payments') }}
),

insurances as (
    select
        plate,
        pickup_date,
        sum(cost) as insurance_cost
    from {{ ref('stg_insurances') }}
    group by plate, pickup_date
),

drive as (
    select distinct on (plate, pickup_date)
        plate,
        pickup_date,
        license_number
    from {{ ref('stg_drive') }}
),

dim_car as (
    select * from {{ ref('dim_car') }}
),

dim_driver as (
    select * from {{ ref('dim_driver') }}
),

dim_office as (
    select * from {{ ref('dim_office') }}
),

dim_date as (
    select * from {{ ref('dim_date') }}
),

joined as (
    select
        rentals.plate,
        rentals.pickup_date,
        rentals.dropoff_date,
        rentals.pickup_place,
        rentals.dropoff_place,
        rentals.miles,
        payments.amount,
        payments.discount,
        payments.payment_mode,
        insurances.insurance_cost,
        drive.license_number
    from rentals
    left join payments
        on rentals.plate = payments.plate
        and rentals.pickup_date = payments.pickup_date
    left join insurances
        on rentals.plate = insurances.plate
        and rentals.pickup_date = insurances.pickup_date
    left join drive
        on rentals.plate = drive.plate
        and rentals.pickup_date = drive.pickup_date
)

select
    dim_car.plate                           as car_plate,
    dim_driver.licensenumber                as driver_license,
    dim_office_pickup.officename            as pickup_office,
    dim_office_dropoff.officename           as dropoff_office,
    dim_date.date_value                     as pickup_date,
    joined.dropoff_date,
    joined.miles,
    joined.amount,
    joined.discount,
    joined.payment_mode,
    joined.insurance_cost
from joined
left join dim_car
    on joined.plate = dim_car.plate
left join dim_driver
    on joined.license_number = dim_driver.licensenumber
left join dim_office as dim_office_pickup
    on joined.pickup_place = dim_office_pickup.officename
left join dim_office as dim_office_dropoff
    on joined.dropoff_place = dim_office_dropoff.officename
left join dim_date
    on joined.pickup_date = dim_date.date_value