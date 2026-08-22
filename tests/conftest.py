# This file includs fixtures and setup for pytest, such as database connections, test data generation, and environment variable loading. It is used to configure the testing environment.

import pytest
import sys
import os 
from dotenv import load_dotenv


#load test envrioment

load_dotenv(".env.test")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'car_rental_dbt'))

from etl.connect import get_engine  # Import the get_engine function from connect.py

@pytest.fixture(scope="function")

def db_engine():
    """
    provide a datbase engine for tests."""

    return get_engine()

@pytest.fixture(scope="function")
def setup_test_data(db_engine):
    """
    provide a database connection for test"""

    conn = db_engine.connect()
    yield conn
    conn.close()