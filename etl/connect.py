import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

load_dotenv()


#

database_url = make_url(os.environ["DATABASE_URL"])

engine = create_engine(
    database_url.set(drivername="postgresql+psycopg2")
)
def get_engine():
    return engine

if __name__ == "__main__":
    with get_engine().connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connected successfully!")
        print(result.fetchone()[0]) 
        