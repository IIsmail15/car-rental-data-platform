from pathlib import Path
import pandas as pd


def read_raw(table: str) -> pd.DataFrame:
    input_path = Path("data")/ "raw" / f"{table}.parquet"
    return pd.read_parquet(input_path)

#
