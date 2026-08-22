from dotenv import load_dotenv
from etl.connect import get_engine
import pytest 
import os 
from sqlalchemy import text


load_dotenv(".env.test")  # Load environment variables from .env.test file for testing

import sys 
sys.path.insert(0,os.path.join(os.path.dirname(__file__), "etl"))  # Add the parent directory to sys.path for module imports

from connect import get_engine  # Import the get_engine function from connect.py

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'car_rental_dbt'))

from generate_data import generate_offices

class TestOffices: 
    "test suite for office-related function"

    def test_offices_insertion(self):
        "test that offices are inserted into the database"
        engine = get_engine()

        generate_offices()

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging.OFFICES;"))
            count = result.scalar()  # Get the count of inserted offices
            assert count >= 5, f"Expected at least 5 offices, got {count}"

            print(f"Inserted {count} offices into the database.")