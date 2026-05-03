import subprocess
from etl.setup_db import setup
from data.generate_data import main as generate

def run_dbt():
    result = subprocess.run(
        ["dbt", "run"],
        cwd="car_rental_dbt",
        capture_output=False
    )
    if result.returncode != 0:
        raise Exception("dbt run failed")

def main():
    print("=== Step 1: Setting up staging schema ===")
    setup()

    print("\n=== Step 2: Generating data ===")
    generate()

    print("\n=== Step 3: Running dbt transformations ===")
    run_dbt()

    print("\n=== Pipeline complete ===")

if __name__ == "__main__":
    main()