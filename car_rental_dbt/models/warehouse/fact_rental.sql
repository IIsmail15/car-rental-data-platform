{{ config(materialized='table') }}

with rentals as (
    select * from {{ source('staging', 'rentals') }}
),

payments as (
    select * from {{ source('staging', 'payments') }}
),

insurances as (
    select
        plate,
        pickupdate,
        sum(cost) as insurance_cost
    from {{ source('staging', 'insurances') }}
    group by plate, pickupdate
),

drive as (
    select distinct on (plate, pickupdate)
        plate,
        pickupdate,
        licensenumber
    from {{ source('staging', 'drive') }}
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
        rentals.pickupdate,
        rentals.dropoffdate,
        rentals.pickupplace,
        rentals.dropoffplace,
        rentals.miles,
        payments.amount,
        payments.discount,
        payments.paymentmode,
        insurances.insurance_cost,
        drive.licensenumber
    from rentals
    left join payments
        on rentals.plate = payments.plate
        and rentals.pickupdate = payments.pickupdate
    left join insurances
        on rentals.plate = insurances.plate
        and rentals.pickupdate = insurances.pickupdate
    left join drive
        on rentals.plate = drive.plate
        and rentals.pickupdate = drive.pickupdate
)

select
    dim_car.plate                           as car_plate,
    dim_driver.licensenumber                as driver_license,
    dim_office_pickup.officename            as pickup_office,
    dim_office_dropoff.officename           as dropoff_office,
    dim_date.date_value                     as pickup_date,
    joined.dropoffdate,
    joined.miles,
    joined.amount,
    joined.discount,
    joined.paymentmode,
    joined.insurance_cost
from joined
left join dim_car
    on joined.plate = dim_car.plate
left join dim_driver
    on joined.licensenumber = dim_driver.licensenumber
left join dim_office as dim_office_pickup
    on joined.pickupplace = dim_office_pickup.officename
left join dim_office as dim_office_dropoff
    on joined.dropoffplace = dim_office_dropoff.officename
left join dim_date
    on joined.pickupdate = dim_date.date_value