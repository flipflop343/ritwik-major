"""Loads the trained classifier once and exposes a predict function."""
import json
from functools import lru_cache
from pathlib import Path

import joblib

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "fraud_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)  # {"pipeline": Pipeline, "name": str}


def model_name() -> str | None:
    m = load_model()
    return m["name"] if m else None


def predict_proba(message: str) -> float:
    m = load_model()
    if m is None:
        raise RuntimeError("Model not trained. Run: python -m ml.train")
    return float(m["pipeline"].predict_proba([message])[0, 1])


def metrics() -> dict | None:
    if not METRICS_PATH.exists():
        return None
    return json.loads(METRICS_PATH.read_text())
