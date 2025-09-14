import os
import sqlite3
import pandas as pd
import subprocess

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "test_matches.db")
JSON_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data/test_matches")

def load_data() -> pd.DataFrame:
    # If DB doesn't exist, generate it from JSON
    if not os.path.exists(DB_FILE):
        print("Database not found. Creating from JSON files...")
        subprocess.run(["python", os.path.join(os.path.dirname(__file__), "..", "to_sqlite.py")], check=True)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM deliveries", conn)
    conn.close()

    if not df.empty:
        df["dismissal"] = df["dismissal"].astype(int)

    return df
