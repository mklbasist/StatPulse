import sqlite3
import pandas as pd
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "test_matches.db")

def fetch_player_data(player=None, bowler=None, venue=None):
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT * FROM deliveries WHERE 1=1"
    params = []

    if player:
        query += " AND LOWER(batter)=?"
        params.append(player.lower())
    if bowler:
        query += " AND LOWER(bowler)=?"
        params.append(bowler.lower())
    if venue:
        query += " AND venue LIKE ?"
        params.append(f"%{venue}%")

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if not df.empty and "dismissal" in df.columns:
        df["dismissal"] = df["dismissal"].fillna(0).astype(int)

    return df
