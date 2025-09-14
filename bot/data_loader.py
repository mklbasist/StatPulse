import sqlite3
import pandas as pd
import os

def load_data(db_path="test_matches.db") -> pd.DataFrame:
    # Absolute path for safety
    db_path = os.path.join(os.path.dirname(__file__), "..", db_path)
    db_path = os.path.abspath(db_path)

    # Connect and load
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM deliveries", conn)
    conn.close()

    # Defensive: ensure dismissal is integer 0/1
    if not df.empty:
        df["dismissal"] = df["dismissal"].astype(int)

    return df
