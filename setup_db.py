import os
from app import db

DB_FILE = 'test.db'

if os.path.exists(DB_FILE):
    print(f"Deleting old database file: {DB_FILE}")
    os.remove(DB_FILE)

print("Creating new database and tables...")
db.create_all()

print("Database setup completed successfully!")
