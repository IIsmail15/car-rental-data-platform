from dotenv import load_dotenv
from etl.connect import get_engine
import pytest 
import os 
from sqlalchemy import text


load_dotenv(".env.test")  # Load environment variables from .env.test file for testing

import sys 
sys.path.insert(0,os.path.join(os.path.dirname(__file__), "etl"))  # Add the parent directory to sys.path for module imports


class TestDB_connection:
    "test 1: checking connection to db"

    engine = get_engine()  # Assuming get_engine is defined in the etl module

    with engine.connect() as conn:
        result = conn.execute(text(""" SELECT current_database(), current_user""" ))  # Execute a simple query to test the connection
        db_name, user = result.fetchone()   

        assert "car_rental" in db_name 
        print(f"Connected to database: {db_name}, User: {user}")  # Assert that the result is as expected

