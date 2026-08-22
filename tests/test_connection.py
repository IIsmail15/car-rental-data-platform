import pytest

from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv(".env.test")

import sys 
import os 

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl'))

class TestConection:
    """Test database connection"""

    def test_can_connect(self, db_engine):
        """can the database be reaached?"""
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1, "Failed to connect to the database"
            print("Database connection successful!") 

    def test_datbase_is_correct(self, db_engine):
        """are we connected to the correct database?"""
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            # check it's the best database(not production)
            assert "test" in db_name or "car_rental" in db_name
        print(f"Connected to the correct database: {db_name}")

            
       