"""Train and compare ML classifiers for fraud / scam message detection.

Run from the backend folder:  python -m ml.train

Data
  * UCI SMS Spam Collection (5,574 SMS, ham/spam)          -> data/raw/SMSSpamCollection
  * Hand-written Indian bank / UPI / KYC fraud + genuine
    transactional messages                                  -> data/custom_messages.csv
  Label 1 = fraud/spam, 0 = legitimate.

Models compared (all use the same TF-IDF word + character n-gram features)
  * Multinomial Naive Bayes
  * Logistic Regression
  * Linear SVM (calibrated so it outputs probabilities)

The best model by 5-fold cross-validated F1 on the training set is evaluated on
a held-out 20% test set and saved to models/fraud_model.joblib, with all
metrics in models/metrics.json.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC

from ml.preprocess import normalize_many

BASE = Path(__file__).resolve().parent.parent
RAW_SMS = BASE / "data" / "raw" / "SMSSpamCollection"
CUSTOM = BASE / "data" / "custom_messages.csv"
MODEL_DIR = BASE / "models"
SEED = 42
CUSTOM_WEIGHT = 5.0  # custom Indian-fraud examples are rare, so count them more


def load_data() -> pd.DataFrame:
    if not RAW_SMS.exists():
        raise SystemExit("Dataset missing. Run:  python -m ml.download_data")
    sms = pd.read_csv(RAW_SMS, sep="\t", header=None, names=["label", "message"], quoting=3)
    sms["label"] = (sms["label"] == "spam").astype(int)
    sms["source"] = "uci_sms"

    custom = pd.read_csv(CUSTOM)
    custom["label"] = (custom["label"] == "fraud").astype(int)
    custom["source"] = "custom"

    df = pd.concat([sms, custom], ignore_index=True).dropna(subset=["message"])
    df = df.drop_duplicates(subset=["message"]).reset_index(drop=True)
    return df


def features() -> FeatureUnion:
    return FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3,
                                 sublinear_tf=True, max_features=50000)),
    ])


def build_models() -> dict[str, Pipeline]:
    def pipe(clf):
        return Pipeline([
            ("normalize", FunctionTransformer(normalize_many)),
            ("features", features()),
            ("clf", clf),
        ])

    return {
        "Naive Bayes": pipe(MultinomialNB(alpha=0.1)),
        "Logistic Regression": pipe(LogisticRegression(C=10, class_weight="balanced", max_iter=2000)),
        "Linear SVM": pipe(CalibratedClassifierCV(LinearSVC(C=1.0, class_weight="balanced"), cv=5)),
    }


def evaluate(model, X, y) -> dict:
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "accuracy": round(accuracy_score(y, pred), 4),
        "precision": round(precision_score(y, pred, zero_division=0), 4),
        "recall": round(recall_score(y, pred, zero_division=0), 4),
        "f1": round(f1_score(y, pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y, proba), 4) if len(set(y)) > 1 else None,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def main():
    df = load_data()
    print(f"Loaded {len(df)} messages  (fraud/spam: {df.label.sum()}, legit: {(df.label == 0).sum()})")

    # Stratify on label+source so custom examples appear in both train and test.
    strat = df["label"].astype(str) + "_" + df["source"]
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=SEED, stratify=strat)
    X_train, y_train = train_df["message"].tolist(), train_df["label"].to_numpy()
    X_test, y_test = test_df["message"].tolist(), test_df["label"].to_numpy()
    w_train = np.where(train_df["source"] == "custom", CUSTOM_WEIGHT, 1.0)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    results = {}
    for name, model in build_models().items():
        t0 = time.perf_counter()
        scores = cross_validate(model, X_train, y_train, cv=cv,
                                scoring=["f1", "precision", "recall", "accuracy"],
                                params={"clf__sample_weight": w_train})
        model.fit(X_train, y_train, clf__sample_weight=w_train)
        test = evaluate(model, X_test, y_test)
        custom_mask = (test_df["source"] == "custom").to_numpy()
        results[name] = {
            "model": model,
            "cv_f1_mean": round(scores["test_f1"].mean(), 4),
            "cv_f1_std": round(scores["test_f1"].std(), 4),
            "cv_precision": round(scores["test_precision"].mean(), 4),
            "cv_recall": round(scores["test_recall"].mean(), 4),
            "test": test,
            "test_custom_only": evaluate(model, np.array(X_test)[custom_mask].tolist(), y_test[custom_mask]),
            "train_seconds": round(time.perf_counter() - t0, 2),
        }
        print(f"  {name:20s} CV F1 {results[name]['cv_f1_mean']:.4f} ± {results[name]['cv_f1_std']:.4f} | "
              f"test F1 {test['f1']:.4f}  P {test['precision']:.4f}  R {test['recall']:.4f}  "
              f"AUC {test['roc_auc']:.4f}")

    best_name = max(results, key=lambda n: results[n]["cv_f1_mean"])
    print(f"\nBest model (by CV F1): {best_name}")

    # Refit best model on ALL data for deployment.
    best = build_models()[best_name]
    w_all = np.where(df["source"] == "custom", CUSTOM_WEIGHT, 1.0)
    best.fit(df["message"].tolist(), df["label"].to_numpy(), clf__sample_weight=w_all)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump({"pipeline": best, "name": best_name}, MODEL_DIR / "fraud_model.joblib")

    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "best_model": best_name,
        "selection": "highest 5-fold cross-validated F1 on the 80% training split",
        "dataset": {
            "total": int(len(df)),
            "fraud": int(df.label.sum()),
            "legit": int((df.label == 0).sum()),
            "custom_examples": int((df.source == "custom").sum()),
            "train_size": len(train_df),
            "test_size": len(test_df),
        },
        "models": {n: {k: v for k, v in r.items() if k != "model"} for n, r in results.items()},
    }
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved model -> {MODEL_DIR / 'fraud_model.joblib'}")
    print(f"Saved metrics -> {MODEL_DIR / 'metrics.json'}")


if __name__ == "__main__":
    main()
