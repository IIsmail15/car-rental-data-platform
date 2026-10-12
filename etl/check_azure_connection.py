"""Check the database in the project .env using psycopg2 directly."""

from contextlib import closing
from pathlib import Path
from urllib.parse import unquote, urlsplit

import psycopg2
from dotenv import dotenv_values


def main() -> int:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    database_url = dotenv_values(env_path, interpolate=False).get("DATABASE_URL")
    if not database_url:
        print("Missing DATABASE_URL in the project .env file.")
        return 1

    target = urlsplit(database_url)
    print(f"Connecting to {target.hostname}:{target.port or 5432}...")

    try:
        with closing(psycopg2.connect(database_url, connect_timeout=10)) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_database(), version()")
                database, version = cursor.fetchone()
                print(f"Connected successfully to {database}!")
                print(version)
    except psycopg2.Error as error:
        message = str(error).replace(database_url, "[connection string hidden]")
        if target.password:
            message = message.replace(target.password, "[password hidden]")
            message = message.replace(unquote(target.password), "[password hidden]")
        print(f"Connection failed: {message}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
