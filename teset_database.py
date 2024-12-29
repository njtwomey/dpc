import os

from dotenv import load_dotenv
from playhouse.postgres_ext import *

load_dotenv()

db = PostgresqlDatabase(
    database=os.getenv("POSTGRES_DATABASE"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=int(os.getenv("POSTGRES_PORT")),
    autorollback=True,
)

try:
    db.connect()
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
