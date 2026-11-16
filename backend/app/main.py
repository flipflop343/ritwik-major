"""FraudShield API.

Run from the backend folder:
    uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import model, rules

# How the final 0-100 risk score is built.
ML_WEIGHT = 0.6
RULE_WEIGHT = 0.4
REPORTED_FLOOR = 80  # a reported fraud number is always at least this risky

app = FastAPI(title="FraudShield API", version="0.2.0",
              description="Detects fraud / scam messages with ML classifiers and rule checks.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=5, max_length=2000)
    sender: str | None = Field(None, max_length=20, pattern=r"^[+\d\s()-]*$")


class Flag(BaseModel):
    id: str
    label: str
    weight: int


class MLResult(BaseModel):
    model: str
    fraud_probability: float
    label: str


class AnalyzeResponse(BaseModel):
    id: int
    checkedAt: str
    message: str
    sender: str | None
    score: int
    verdict: str
    flags: list[Flag]
    numbers: list[str]
    links: list[str]
    ml: MLResult
    rule_score: int
    source: str = "backend"


@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": model.load_model() is not None, "model": model.model_name()}


@app.get("/api/model")
def model_info():
    m = model.metrics()
    if m is None:
        raise HTTPException(503, "Model not trained yet. Run: python -m ml.train")
    return m


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if model.load_model() is None:
        raise HTTPException(503, "Model not trained yet. Run: python -m ml.train")

    message = req.message.strip()
    sender = (req.sender or "").strip() or None

    numbers, links = rules.extract(message)
    flags = rules.message_flags(message) + rules.sender_flags(sender) + rules.reported_in_message(numbers)
    rule_score = min(100, sum(f["weight"] for f in flags))

    prob = model.predict_proba(message)
    score = round(ML_WEIGHT * prob * 100 + RULE_WEIGHT * rule_score)
    if any(f["id"].startswith("reported") for f in flags):
        score = max(score, REPORTED_FLOOR)
    score = max(0, min(100, score))
    verdict = "fraud" if score >= 60 else "suspicious" if score >= 30 else "safe"

    return AnalyzeResponse(
        id=time.time_ns() // 1_000_000,
        checkedAt=datetime.now(timezone.utc).isoformat(),
        message=message,
        sender=sender,
        score=score,
        verdict=verdict,
        flags=flags,
        numbers=numbers,
        links=links,
        ml=MLResult(model=model.model_name(), fraud_probability=round(prob, 4),
                    label="fraud" if prob >= 0.5 else "legit"),
        rule_score=rule_score,
    )
