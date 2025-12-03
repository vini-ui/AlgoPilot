"""
Migration script to add mpin column to app_secrets table.
Run this script once to update the existing database schema.
"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), "algopilot.db")

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    print("The database will be created automatically when you start the backend.")
    exit(0)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if mpin column already exists
    cursor.execute("PRAGMA table_info(app_secrets)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'mpin' in columns:
        print("[OK] mpin column already exists in app_secrets table")
    else:
        # Add mpin column
        print("Adding mpin column to app_secrets table...")
        cursor.execute("ALTER TABLE app_secrets ADD COLUMN mpin TEXT")
        conn.commit()
        print("[OK] Successfully added mpin column to app_secrets table")
    
    # Check if base_url column exists
    if 'base_url' in columns:
        print("[OK] base_url column already exists in app_secrets table")
    else:
        # Add base_url column
        print("Adding base_url column to app_secrets table...")
        cursor.execute("ALTER TABLE app_secrets ADD COLUMN base_url TEXT DEFAULT 'https://apiconnect.angelbroking.com'")
        conn.commit()
        print("[OK] Successfully added base_url column to app_secrets table")
    
    print("\nMigration completed successfully!")
    
except sqlite3.Error as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()

