-- --- Warehouse schema creation commented out ---
-- Design decision: warehouse schema and all dimension/fact tables
-- are now managed by dbt. Running dbt run creates and maintains
-- these tables automatically from the models in car_rental_dbt/models/warehouse/.
-- Original manual definitions kept here for reference only.

--                     dim_car
--                        │
--    dim_driver ────── fact_rental ────── dim_office
--                        │
--                      dim_date


-- CREATE TABLE IF NOT EXISTS warehouse.dim_car(

--     car_id SERIAL PRIMARY KEY,
--     plate VARCHAR(255) UNIQUE NOT NULL,
--     category VARCHAR(255),
--     model VARCHAR(255),
--     brand VARCHAR(255),
--     fuel VARCHAR(255),
--     registration_date DATE,
--     options VARCHAR(255)
-- );

-- CREATE TABLE IF NOT EXISTS warehouse.dim_driver
-- (
--     driver_id SERIAL PRIMARY KEY,
--     license_number VARCHAR(255) UNIQUE NOT NULL,
--     license_expiration DATE,
--     driver_name VARCHAR(255),
--     birthdate DATE
-- );

-- CREATE TABLE IF NOT EXISTS warehouse.dim_office
-- (
--     office_id SERIAL PRIMARY KEY,
--     office_name VARCHAR(255) UNIQUE NOT NULL,
--     city varchar(255),
--     area varchar(255),
--     country varchar(255)

-- );

-- CREATE TABLE IF NOT EXISTS warehouse.dim_date
-- (
--     date_id Serial Primary key,
--     year int,
--     month int,
--     day int,
--     weekday int,
--     quarter int,
--     week_of_year int,
--     is_weekend boolean

-- );

-- CREATE TABLE IF NOT EXISTS warehouse.fact_rental
-- (
--     rental_id           SERIAL PRIMARY KEY,
--     car_id              INT REFERENCES warehouse.dim_car(car_id),
--     driver_id           INT REFERENCES warehouse.dim_driver(driver_id),
--     pickup_office_id    INT REFERENCES warehouse.dim_office(office_id),
--     dropoff_office_id   INT REFERENCES warehouse.dim_office(office_id),
--     pickup_date_id      INT REFERENCES warehouse.dim_date(date_id),
--     dropoff_date_id     INT REFERENCES warehouse.dim_date(date_id),
--     miles               INT,
--     amount              DECIMAL(10,2),
--     discount            DECIMAL(10,2),
--     payment_mode        VARCHAR(255),
--     insurance_cost      DECIMAL(10,2)
-- );
