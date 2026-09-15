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
        """Are we connected to the expected database?"""
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            db_name_lower = db_name.lower()
            assert "test" in db_name_lower or "car_rental" in db_name_lower or "neondb" in db_name_lower
        print(f"Connected to the correct database: {db_name}")

            
       