import sqlite3
import pandas as pd
import os

def load_data(db_path="test_matches.db") -> pd.DataFrame:
    """
    Load match data directly from SQLite database instead of JSONs.
    Resolves absolute path to ensure Render can find the DB file.
    """
    # Convert relative path to absolute path based on project root
    base_dir = os.path.dirname(os.path.abspath(__file__))  # bot folder
    db_path = os.path.join(base_dir, "..", db_path)
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM deliveries", conn)
    except pd.io.sql.DatabaseError as e:
        raise RuntimeError(f"Error reading 'deliveries' table: {e}")
    finally:
        conn.close()

    # Ensure dismissals are strictly 0/1 integers
    if not df.empty:
        df["dismissal"] = df["dismissal"].astype(int)

    return df
