import pandas as pd
from etl.connect import engine
from pathlib import Path

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

def extract(tables: list[str]) -> dict[str, pd.DataFrame]: 
    output_dir = Path("data")/ "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    dfs = {}
    for table in tables:
        dfs[table] = pd.read_sql(f"SELECT * FROM staging.{table}", engine)
        dfs[table].to_parquet(output_dir / f"{table}.parquet", index=False)
        print(f"Extracted {len(dfs[table])} rows from staging.{table}")
    return dfs

if __name__ == "__main__":
    data = extract(["RENTALS"])
    print(f"Extracted {len(data['RENTALS'])} rows from staging.RENTALS")
    #for name, df in data.items():
        #print(f"{name}: {df.shape}")
