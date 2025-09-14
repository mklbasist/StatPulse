# bot/nlp_parser.py
import re
import spacy
from rapidfuzz import process
from bot import data_loader

# Load all match data once
df = data_loader.load_data()  # no argument needed

# Dynamic player + venue lists
PLAYERS = df["batter"].unique().tolist() + df["bowler"].unique().tolist()
VENUES = df["venue"].unique().tolist()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Metric keywords
METRICS = {
    "average": ["average", "avg", "batting avg"],
    "strike_rate": ["strike rate", "sr"],
    "dismissals": ["dismissal", "out", "got out"],
    "runs": ["run", "runs", "score", "scored"],
    "wickets": ["wicket", "wickets", "took"]
}


def clean_query(text: str) -> str:
    """Normalize apostrophes and remove possessives"""
    text = re.sub(r"'s\b", "", text)
    text = text.replace("’", "'")
    return text.strip()


def fuzzy_match(query, choices, threshold=80):
    """Return closest match from choices using fuzzy matching"""
    if not query or not choices:
        return None
    match = process.extractOne(query, choices)
    if match and match[1] >= threshold:
        return match[0]
    return None


def parse_query(query: str):
    query = clean_query(query)
    q_lower = query.lower()
    doc = nlp(query)

    player, bowler, venue, metric = None, None, None, None

    # --- Handle "player vs bowler" or "player against bowler" ---
    if re.search(r"\b(against|vs|versus)\b", q_lower):
        parts = re.split(r"\b(?:against|vs|versus)\b", query, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()

            # Extract venue if "at <venue>" is present
            if re.search(r"\bat\b", right, flags=re.IGNORECASE):
                right_before_at, at_part = re.split(r"\bat\b", right, flags=re.IGNORECASE, maxsplit=1)
                bowler = fuzzy_match(right_before_at.strip(), PLAYERS)
                venue = fuzzy_match(at_part.strip(), VENUES)
            else:
                bowler = fuzzy_match(right, PLAYERS)

            player = fuzzy_match(left, PLAYERS)

    # --- Fallback: use spaCy NER ---
    if not player or not bowler:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                m = fuzzy_match(ent.text, PLAYERS)
                if m:
                    if not player:
                        player = m
                    elif not bowler:
                        bowler = m
            elif ent.label_ in ["GPE", "LOC", "ORG"]:
                m = fuzzy_match(ent.text, VENUES)
                if m:
                    venue = m

    # --- Metric detection ---
    for key, keywords in METRICS.items():
        if any(word in q_lower for word in keywords):
            metric = key
            break

    return {"player": player, "bowler": bowler, "venue": venue, "metric": metric}
