from fastapi import FastAPI
from pydantic import BaseModel
from bot import nlp_parser, stats_engine

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
