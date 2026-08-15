#shared fixtures for tests 

from data.generate_data import generate_rentals, generate_drives, generate_insurances, generate_payments
from sqlalchemy import create_engine
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Generate data for all tables before running tests
    generate_rentals()
    generate_drives()
    generate_insurances()
    generate_payments() 

