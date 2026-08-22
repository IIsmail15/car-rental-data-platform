import pytest 
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv(".env.test")

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl'))

from connect import get_engine  # Import the get_engine function from connect.py

class TestDataQuality:
    """"test data quality in staging tables."""
def test_no_nulls_in_primary_keys(self, db_engine):
    test = [
        ("staging.cars", 'plate'),
        ("staging.drivers", 'license_number'),
        ("staging.rental_offices", 'OfficeName')
    ]

    with db_engine.connect() as conn:
        for table, pk in tests:
            result = conn.execute(text(f"""  
            SELECT COUNT(*) FROM {table} WHERE {pk} IS NULL; 
            """)
            count = result.scalar()
            assert count == 0, f"Found NULL values in column {pk} of table {table}"
    print("No NULL values found in primary key columns of staging tables.")


def test_foreign_keys_valid(self, db_engine):
     """ensure all foreign keys reference existing records."""
     with db_engine.connect() as conn:
     result = conn.execute(text("""
     SELECT COUNT(*) FROM staging.rentals r
        LEFT JOIN staging.cars c ON r.car_plate = c.plate
        WHERE c.plate IS NULL;
        """))
        count = result.scalar()
        assert count == 0, f"Found {count} rentals with invalid car reference."
    print("all foreign keys are valid")

def test_rental_dates_valid(self,db_engine):
"""ensure rental start dates are before end dates."""

    with db_engine.connect() as conn:
        result = conn.execute(text("""
        SELECT COUNT(*) FROM staging.rentals
        WHERE PickupDate >= DropoffDate;
        """))
        count = result.scalar()
        assert count == 0, f"Found {count} rentals with invalid date ranges."

        print("all rental dates are valid.")

        



    