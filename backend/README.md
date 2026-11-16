# FraudShield – Backend (FastAPI + ML)

Scores a message for fraud using a trained ML classifier combined with
explainable rule checks.

## Setup (first time)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m ml.download_data      # UCI SMS Spam Collection -> data/raw/
python -m ml.train              # trains + compares models -> models/
```

## Run

```bash
uvicorn app.main:app --reload
```

- API docs (try requests in the browser): http://127.0.0.1:8000/docs
- Then start the frontend (`cd frontend && npm run dev`); it forwards `/api` calls here.

## Tests

```bash
python -m pytest
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | status + loaded model name |
| GET | `/api/model` | training metrics for all compared models |
| POST | `/api/analyze` | `{ "message": "...", "sender": "+91..." }` -> verdict, score, flags, ML probability |

## How it works

1. **Data**: UCI SMS Spam Collection (5,574 SMS, CC BY 4.0) plus
   `data/custom_messages.csv`, hand-written Indian KYC/UPI/OTP/job scams and
   genuine bank alerts. Custom rows get 5x weight because they are rare.
2. **Preprocessing** (`ml/preprocess.py`): lowercase; URLs, phone numbers,
   money amounts and numbers replaced by tokens.
3. **Features**: TF-IDF word 1–2-grams + character 3–5-grams (catches
   misspellings like "acc0unt").
4. **Models compared**: Multinomial Naive Bayes, Logistic Regression, Linear
   SVM (calibrated). The best by 5-fold cross-validated F1 is saved; all
   metrics are in `models/metrics.json`.
5. **Final score** (`app/main.py`): `0.6 × ML probability + 0.4 × rule score`,
   with a floor of 80 if a reported fraud number appears.
   Verdict: ≥60 fraud, ≥30 suspicious, else safe.

## Results (seed 42, 80/20 split)

| Model | CV F1 | Test F1 | Precision | Recall | ROC-AUC |
|---|---|---|---|---|---|
| Naive Bayes | 0.927 | 0.944 | 0.932 | 0.958 | 0.996 |
| Logistic Regression | 0.950 | 0.972 | 0.972 | 0.972 | 0.998 |
| **Linear SVM** (selected) | 0.950 | 0.975 | 0.979 | 0.972 | 0.998 |

Limitations: the UCI data is UK SMS from ~2012, and the custom Indian set is
small (~110 messages), so performance on new Indian scam styles is less
certain than the table suggests. More labelled Indian data is the biggest
improvement available.
