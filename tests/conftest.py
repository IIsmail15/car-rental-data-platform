# This file includs fixtures and setup for pytest, such as database connections,
# test data generation, and environment variable loading.

import os
import sys

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv(".env.test")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'car_rental_dbt'))

from etl.connect import get_engine
from etl.setup_db import setup


@pytest.fixture(scope="function")
def db_engine():
    """Provide a clean database engine for tests."""
    setup()
    engine = get_engine()

    with engine.begin() as conn:
        for table in [
            "staging.payments",
            "staging.insurances",
            "staging.drive",
            "staging.have_optional",
            "staging.rentals",
            "staging.cars",
            "staging.drivers",
            "staging.rental_offices",
        ]:
            conn.execute(text(f"DELETE FROM {table}"))

    return engine


@pytest.fixture(scope="function")
def setup_test_data(db_engine):
    """Provide a database connection for tests."""
    conn = db_engine.connect()
    yield conn
    conn.close()