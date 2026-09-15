import os
import sys

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv(".env.test")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'car_rental_dbt'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

from connect import get_engine
from generate_data import generate_cars, generate_drivers, generate_offices, generate_rentals


class TestPipeline:
    """Test the complete data generation pipeline."""

    def test_offices_generation(self, db_engine):
        """Can we generate offices?"""
        with db_engine.connect() as conn:
            before = conn.execute(text("SELECT COUNT(*) FROM staging.rental_offices")).scalar()

        generate_offices()

        with db_engine.connect() as conn:
            after = conn.execute(text("SELECT COUNT(*) FROM staging.rental_offices")).scalar()

        assert after == before + 5, f"Expected {before + 5}, got {after}"
        print(f"inserted {after - before} offices (total {after})")

    def test_cars_generation(self, db_engine):
        """Can we generate cars?"""
        generate_offices()

        with db_engine.connect() as conn:
            before = conn.execute(text("SELECT COUNT(*) FROM staging.cars")).scalar()

        generate_cars(n=10)

        with db_engine.connect() as conn:
            after = conn.execute(text("SELECT COUNT(*) FROM staging.cars")).scalar()

        assert after == before + 10, f"Expected {before + 10}, got {after}"
        print(f"inserted {after - before} cars (total {after})")

    def test_cars_have_unique_plates(self, db_engine):
        """Ensure all cars have unique plates."""
        generate_offices()
        generate_cars(n=10)

        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT plate FROM staging.cars"))

        plates = [row[0] for row in result.fetchall()]
        unique_plates = set(plates)

        assert len(plates) == len(unique_plates), "Duplicate licence plates found in cars table"

    def test_rentals_generation(self, db_engine):
        """Can we generate rentals?"""
        generate_offices()
        generate_cars(n=10)
        generate_drivers(n=5)

        with db_engine.connect() as conn:
            before = conn.execute(text("SELECT COUNT(*) FROM staging.rentals")).scalar()

        generate_rentals(n=5)

        with db_engine.connect() as conn:
            after = conn.execute(text("SELECT COUNT(*) FROM staging.rentals")).scalar()

        assert after == before + 5, f"Expected {before + 5}, got {after}"
        print(f"inserted {after - before} rentals (total {after})")
