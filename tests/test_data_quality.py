import pytest

def test_data_count(): 
    count = get_row_count("staging.RENTALS")
    assert count == 200, f"Expected 200 rows in staging.RENTALS, but found {count}"


def test_no_null(): 
    null_count = get_null_count("rentals","cars_plate")
    assert null_count == 0, f"Expected 0 null values in rentals.cars_plate, but found {null_count}"

