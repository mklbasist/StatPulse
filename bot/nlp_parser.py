import re
import spacy
from rapidfuzz import process
from bot import data_loader

# Load spaCy model
import en_core_web_sm
nlp = en_core_web_sm.load()

# Metric keywords
METRICS = {
    "average": ["average", "avg", "batting avg"],
    "strike_rate": ["strike rate", "sr"],
    "dismissals": ["dismissal", "out", "got out"],
    "runs": ["run", "runs", "score", "scored"],
    "wickets": ["wicket", "wickets", "took"]
}

def clean_query(text: str) -> str:
    text = re.sub(r"'s\b", "", text)
    text = text.replace("’", "'")
    return text.strip()

def parse_query(query: str):
    query = clean_query(query)
    q_lower = query.lower()
    doc = nlp(query)

    player, bowler, venue, metric = None, None, None, None

    # detect player vs bowler
    if re.search(r"\b(against|vs|versus)\b", q_lower):
        parts = re.split(r"\b(?:against|vs|versus)\b", query, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) == 2:
            player = parts[0].strip()
            bowler = parts[1].strip()

    # fallback using NER
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not player:
            player = ent.text
        elif ent.label_ == "PERSON" and not bowler:
            bowler = ent.text
        elif ent.label_ in ["GPE", "LOC", "ORG"] and not venue:
            venue = ent.text

    # metric detection
    for key, keywords in METRICS.items():
        if any(word in q_lower for word in keywords):
            metric = key
            break

    return {"player": player, "bowler": bowler, "venue": venue, "metric": metric}
