import pandas as pd
from etl.connect import engine

STAGING_TABLES = [
    "RENTAL_OFFICES",
    "CARS",
    "HAVE_OPTIONAL",
    "DRIVERS",
    "RENTALS",
    "DRIVE",
    "INSURANCES",
    "PAYMENTS",
]

def extract() -> dict[str, pd.DataFrame]:
    dfs = {}
    for table in STAGING_TABLES:
        dfs[table] = pd.read_sql(f"SELECT * FROM staging.{table}", engine)
        print(f"Extracted {len(dfs[table])} rows from staging.{table}")
    return dfs

if __name__ == "__main__":
    data = extract()
    for name, df in data.items():
        print(f"{name}: {df.shape}")
