import pytest
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv(".env.test")

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'car_rental_dbt'))

from connect import get_engine
from generated_data import generate_offices, generate_cars, generate_drivers, generate_rentals

class TestPipeline:
    """test the complete data generation pipeline""""

    def test_offices_generation(self, db_engine):
        """can we generate offices?"""
        with db_engine.connect() as conn:
            before = conn.execute(text("SELECT COUNT(*) FROM staging.rental_offices")).scalar()

        generate_offices()

        with db_engine.connect() as conn:
            after = conn.execute(text("SELECT COUNT(*) FROM staging.rental_offices")).scalar()

        assert after == before + 5, f"Expected {before + 5} , got {after}"
        print(f"inserted{ after - before} offices (total {after})")

    def test_cars_generation(self, db_engine):
        """can we generate cars?"""

        #making sure offices exist first 
        generate_offices()

        with db_engine.connect() as conn:
            before = conn.execute(
                text("SELECT COUNT(*) FROM staging.cars")
            ).scalar()

            generate_cars(n=10)
        #assert check count after 
        with db_engine.connect() as conn:
            after = conn.execute(
                text("SELECT COUNT(*) FROM staging.cars")
            ).scalar()

            assert after == before + 10, f"Expected {before + 10}, got {after}"

            print(f"inserted {after - before} cars (total {after})")

    def test_cars_have_unique_plates(self, db_engine):
        """ensure all cars have unique plates."""

        #making sure car exist

        generate_offices()
        generate_cars(n=10)

        #query the database
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT LicenceNumber FROM staging.drivers"))
        #extract all plates into a list 

        plates = [row[0] for row in result.fetchall()]

        #create a set to find duplicates
        unique_plates = set(plates)

        assert len(plates) == len(unique_plates), "Duplicate licence plates found in cars table"

    def test_rentals_generation(self, db_engine):
        """can we generate rentals?"""

        #making sure offices, cars and drivers exist first 
        generate_offices()
        generate_cars(n=10)
        generate_drivers(n=5)

        with db_engine.connect() as conn:
            before = conn.execute(
                text("SELECT COUNT(*) FROM staging.rentals")
            ).scalar()

        generate_rentals(n=5)

        #assert check count after 
        with db_engine.connect() as conn:
            after = conn.execute(
                text("SELECT COUNT(*) FROM staging.rentals")
            ).scalar()

            assert after == before + 5, f"Expected {before + 5}, got {after}"

            print(f"inserted {after - before} rentals (total {after})")
