import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
#
engine = create_engine(os.environ["DATABASE_URL"])
def get_engine():
    return engine

if __name__ == "__main__":
    with get_engine().connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connected successfully!")
        print(result.fetchone()[0])