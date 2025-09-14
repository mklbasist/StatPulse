import os
import json
import sqlite3

# Path where your JSON files are stored
DATA_FOLDER = "data/test_matches"
DB_FILE = "test_matches.db"

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

def insert_record(conn, record):
    conn.execute("""
        INSERT INTO deliveries (
            match_id, venue, team, batter, bowler,
            runs_batter, runs_extras, runs_total, dismissal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["match_id"], record["venue"], record["team"],
        record["batter"], record["bowler"],
        record["runs_batter"], record["runs_extras"],
        record["runs_total"], record["dismissal"]
    ))

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

    for fname in os.listdir(DATA_FOLDER):
        if fname.endswith(".json"):
            file_path = os.path.join(DATA_FOLDER, fname)
            records = parse_match(file_path)
            for rec in records:
                insert_record(conn, rec)
            conn.commit()

    conn.close()
    print(f"✅ Done! All JSON data stored in {DB_FILE}")

if __name__ == "__main__":
    main()
