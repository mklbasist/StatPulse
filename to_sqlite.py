# to_sqlite.py
import os
import json
import sqlite3

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data", "test_matches")
DB_FILE = os.path.join(os.path.dirname(__file__), "test_matches.db")
BATCH_SIZE = 100  # insert 100 deliveries at a time

def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            venue TEXT,
            team TEXT,
            batter TEXT,
            bowler TEXT,
            runs_batter INTEGER,
            runs_extras INTEGER,
            runs_total INTEGER,
            dismissal INTEGER
        )
    """)
    conn.commit()

def insert_batch(conn, batch):
    conn.executemany("""
        INSERT INTO deliveries (
            match_id, venue, team, batter, bowler,
            runs_batter, runs_extras, runs_total, dismissal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()

def parse_match(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        match = json.load(f)

    match_id = os.path.basename(file_path).replace(".json", "")
    venue = match["info"].get("venue", "Unknown")

    records = []
    for innings in match.get("innings", []):
        team = innings.get("team")
        for over in innings.get("overs", []):
            for delivery in over.get("deliveries", []):
                batter = delivery.get("batter")
                bowler = delivery.get("bowler")
                runs = delivery.get("runs", {})
                dismissal = 1 if delivery.get("wickets") else 0

                records.append((
                    match_id, venue, team, batter, bowler,
                    runs.get("batter", 0),
                    runs.get("extras", 0),
                    runs.get("total", 0),
                    dismissal
                ))
    return records

def main():
    conn = sqlite3.connect(DB_FILE)
    create_table(conn)

    batch = []
    for fname in os.listdir(DATA_FOLDER):
        if not fname.endswith(".json"):
            continue
        file_path = os.path.join(DATA_FOLDER, fname)
        records = parse_match(file_path)

        for rec in records:
            batch.append(rec)
            if len(batch) >= BATCH_SIZE:
                insert_batch(conn, batch)
                batch = []

    # insert any remaining records
    if batch:
        insert_batch(conn, batch)

    conn.close()
    print(f"✅ Done! All JSON data stored in {DB_FILE}")

if __name__ == "__main__":
    main()
