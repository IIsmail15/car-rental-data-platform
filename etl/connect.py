from sqlalchemy import create_engine, text 
import os 
from dotenv import load_dotenv 

load_dotenv()

def get_engine():
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print("Connected successfully!")
    print(result.fetchone()[0]) 