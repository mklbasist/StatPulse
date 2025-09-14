import os
from fastapi import FastAPI
from pydantic import BaseModel
from bot import nlp_parser, stats_engine
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "Server is running!"}

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    parsed = nlp_parser.parse_query(q.question)
    reply = stats_engine.answer_query(parsed)
    return {"reply": reply}

@app.post("/debug_parse")
def debug_parse(q: Question):
    parsed = nlp_parser.parse_query(q.question)
    return {"parsed": parsed}

if __name__ == "__main__":
    # Use Render's PORT environment variable, fallback to 8000 for local testing
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
