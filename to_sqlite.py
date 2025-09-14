import os
import json
import sqlite3

# Paths
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data", "test_matches")
DB_FILE = os.path.join(os.path.dirname(__file__), "test_matches.db")

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

def insert_records(conn, records):
    if not records:
        return
    conn.executemany("""
        INSERT INTO deliveries (
            match_id, venue, team, batter, bowler,
            runs_batter, runs_extras, runs_total, dismissal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            r["match_id"], r["venue"], r["team"], r["batter"], r["bowler"],
            r["runs_batter"], r["runs_extras"], r["runs_total"], r["dismissal"]
        )
        for r in records
    ])
    conn.commit()

def parse_match(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        match = json.load(f)

    match_id = os.path.basename(file_path).replace(".json", "")
    venue = match.get("info", {}).get("venue", "Unknown")

    records = []
    for innings in match.get("innings", []):
        team = innings.get("team")
        for over in innings.get("overs", []):
            for delivery in over.get("deliveries", []):
                batter = delivery.get("batter")
                bowler = delivery.get("bowler")
                runs = delivery.get("runs", {})

                # Only count dismissal if this batter got out
                dismissal = 0
                for w in delivery.get("wickets", []):
                    if w.get("player_out") == batter:
                        dismissal = 1
                        break

                records.append({
                    "match_id": match_id,
                    "venue": venue,
                    "team": team,
                    "batter": batter,
                    "bowler": bowler,
                    "runs_batter": runs.get("batter", 0),
                    "runs_extras": runs.get("extras", 0),
                    "runs_total": runs.get("total", 0),
                    "dismissal": dismissal
                })
    return records

def main():
    conn = sqlite3.connect(DB_FILE)
    create_table(conn)

    json_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    total_files = len(json_files)
    print(f"Found {total_files} JSON files. Processing in batches...")

    for i, fname in enumerate(json_files, 1):
        file_path = os.path.join(DATA_FOLDER, fname)
        records = parse_match(file_path)
        insert_records(conn, records)
        if i % 50 == 0 or i == total_files:
            print(f"Processed {i}/{total_files} files")

    conn.close()
    print(f"✅ Done! All JSON data stored in {DB_FILE}")

if __name__ == "__main__":
    main()
