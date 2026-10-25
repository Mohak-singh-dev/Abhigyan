import os
import sys
import urllib.parse
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import settings

def check_and_create_db():
    url = settings.DATABASE_URL
    if "YOUR_POSTGRES_PASSWORD" in url:
        print("STATUS: PLACEHOLDER_DETECTED")
        print("Notice: backend/.env contains 'YOUR_POSTGRES_PASSWORD'.")
        print("Please replace 'YOUR_POSTGRES_PASSWORD' with your actual postgres password in backend/.env.")
        sys.exit(2)

    parsed = urllib.parse.urlparse(url)
    db_name = parsed.path.lstrip("/")

    # Safe masked URL for printing (never reveal password)
    print(f"Connecting to host: {parsed.hostname}:{parsed.port} as user '{parsed.username}'...")

    try:
        # First connect to default postgres db with autocommit to check and create database if missing
        admin_url = url.replace(f"/{db_name}", "/postgres")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name}
            ).scalar()

            if exists:
                print(f"STATUS: Database '{db_name}' already exists.")
            else:
                print(f"STATUS: Database '{db_name}' not found. Creating database '{db_name}'...")
                conn.execute(text(f'CREATE DATABASE "{db_name}";'))
                print(f"SUCCESS: Database '{db_name}' created successfully.")

        # Now test connection directly to target db
        target_engine = create_engine(url, pool_pre_ping=True)
        with target_engine.connect() as conn:
            ver = conn.execute(text("SELECT version();")).scalar()
            print(f"SUCCESS: Connected directly to '{db_name}'.")
            print(f"PostgreSQL Version: {ver}")
            return True

    except Exception as e:
        err_msg = str(e)
        if "password authentication failed" in err_msg.lower():
            print("ERROR: Password authentication failed for user 'postgres'.")
            print("Please verify the password entered in backend/.env.")
        elif "connection to server" in err_msg.lower():
            print("ERROR: Unable to connect to PostgreSQL service on localhost:5432.")
            print("Please verify the windows service 'postgresql-x64-18' is running.")
        else:
            print(f"ERROR: Database check/creation failed: {err_msg}")
        sys.exit(1)

if __name__ == "__main__":
    check_and_create_db()
