from sqlalchemy import text
from etl.connect import engine


def setup():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS warehouse;"))
        print("Schemas created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.RENTAL_OFFICES (
                OfficeName VARCHAR(255) PRIMARY KEY,
                City VARCHAR(255),
                Area VARCHAR(255),
                State VARCHAR(255),
                Country VARCHAR(255)
            );
        """))
        print("staging.RENTAL_OFFICES table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.CARS(
                Plate VARCHAR(255) PRIMARY KEY,
                Category VARCHAR(255),
                Model VARCHAR(255),
                Brand VARCHAR(255),
                Fuel VARCHAR(255),
                RegistrationDate DATE
            );
        """))
        print("staging.CARS table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.HAVE_OPTIONAL(
                RentalID SERIAL PRIMARY KEY,
                Plate VARCHAR(255),
                Optional VARCHAR(255),
                FOREIGN KEY (Plate) REFERENCES staging.CARS(Plate)
            );
        """))
        print("staging.HAVE_OPTIONAL table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.RENTALS(
                Plate           VARCHAR(255),
                PickupDate      DATE,
                DropoffDate     DATE,
                PickupPlace     VARCHAR(255),
                DropoffPlace    VARCHAR(255),
                Miles           INT,
                PRIMARY KEY (Plate, PickupDate),
                FOREIGN KEY (Plate)
                    REFERENCES staging.CARS(Plate),
                FOREIGN KEY (PickupPlace)
                    REFERENCES staging.RENTAL_OFFICES(OfficeName),
                FOREIGN KEY (DropoffPlace)
                    REFERENCES staging.RENTAL_OFFICES(OfficeName)
            );
        """))
        print("staging.RENTALS table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.DRIVERS(
                LicenseNumber VARCHAR(255) PRIMARY KEY,
                LicenseExpiration DATE,
                DriverName VARCHAR(255),
                Birthdate DATE
            );
        """))
        print("staging.DRIVERS table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.DRIVE(
                LicenseNumber VARCHAR(255),
                Plate VARCHAR(255),
                PickupDate DATE,
                PRIMARY KEY (LicenseNumber, Plate, PickupDate),
                FOREIGN KEY (LicenseNumber)
                    REFERENCES staging.DRIVERS(LicenseNumber),
                FOREIGN KEY (Plate, PickupDate)
                    REFERENCES staging.RENTALS(Plate, PickupDate)
            );
        """))
        print("staging.DRIVE table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.INSURANCES(
                Risk VARCHAR(255),
                Plate VARCHAR(255),
                PickupDate DATE,
                Cost DECIMAL(10, 2),
                PRIMARY KEY (Risk, Plate, PickupDate),
                FOREIGN KEY (Plate, PickupDate)
                    REFERENCES staging.RENTALS(Plate, PickupDate)
            );
        """))
        print("staging.INSURANCES table created successfully!")

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staging.PAYMENTS(
                Plate VARCHAR(255),
                PickupDate DATE,
                Amount DECIMAL(10, 2),
                Discount DECIMAL(10, 2),
                PaymentMode VARCHAR(255),
                PRIMARY KEY (Plate, PickupDate),
                FOREIGN KEY (Plate, PickupDate)
                    REFERENCES staging.RENTALS(Plate, PickupDate)
            );
        """))
        print("staging.PAYMENTS table created successfully!")

        # --- Warehouse schema tables commented out ---
        # Design decision: warehouse schema and tables are now managed by dbt.
        # dbt creates and maintains all dimension and fact tables directly.
        # Keeping this here for reference only.

        # conn.execute(text("""
        #     CREATE TABLE IF NOT EXISTS warehouse.dim_car(
        #         car_id SERIAL PRIMARY KEY,
        #         plate VARCHAR(255) UNIQUE,
        #         category VARCHAR(255),
        #         model VARCHAR(255),
        #         brand VARCHAR(255),
        #         fuel VARCHAR(255),
        #         registration_date DATE,
        #         optional VARCHAR(255)
        #     );
        # """))
        # print("warehouse.dim_car table created successfully!")

        # conn.execute(text("""
        #     CREATE TABLE IF NOT EXISTS warehouse.dim_driver(
        #         driver_id SERIAL PRIMARY KEY,
        #         license_number VARCHAR(255) UNIQUE,
        #         license_expiration DATE,
        #         driver_name VARCHAR(255),
        #         birthdate DATE
        #     );
        # """))
        # print("warehouse.dim_driver table created successfully!")

        # conn.execute(text("""
        #     CREATE TABLE IF NOT EXISTS warehouse.dim_office(
        #         office_id SERIAL PRIMARY KEY,
        #         office_name VARCHAR(255) UNIQUE NOT NULL,
        #         city VARCHAR(255),
        #         area VARCHAR(255),
        #         state VARCHAR(255),
        #         country VARCHAR(255)
        #     );
        # """))
        # print("warehouse.dim_office table created successfully!")

        # conn.execute(text("""
        #     CREATE TABLE IF NOT EXISTS warehouse.dim_date(
        #         date_id SERIAL PRIMARY KEY,
        #         year INT,
        #         month INT,
        #         day INT,
        #         weekday INT,
        #         quarter INT,
        #         week_of_year INT,
        #         is_weekend BOOLEAN
        #     );
        # """))
        # print("warehouse.dim_date table created successfully!")

        # conn.execute(text("""
        #     CREATE TABLE IF NOT EXISTS warehouse.fact_rental(
        #         rental_id SERIAL PRIMARY KEY,
        #         car_id INT REFERENCES warehouse.dim_car(car_id),
        #         driver_id INT REFERENCES warehouse.dim_driver(driver_id),
        #         pickup_office_id INT REFERENCES warehouse.dim_office(office_id),
        #         dropoff_office_id INT REFERENCES warehouse.dim_office(office_id),
        #         pickup_date_id INT REFERENCES warehouse.dim_date(date_id),
        #         dropoff_date_id INT REFERENCES warehouse.dim_date(date_id),
        #         miles INT,
        #         amount DECIMAL(10, 2),
        #         discount DECIMAL(10, 2),
        #         payment_mode VARCHAR(255),
        #         insurance_cost DECIMAL(10, 2)
        #     );
        # """))
        # print("warehouse.fact_rental table created successfully!")

        conn.commit()
    print("Database setup complete")


if __name__ == "__main__":
    setup()
