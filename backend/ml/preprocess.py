"""Text normalisation shared by training and the API.

Replacing URLs, phone numbers and amounts with tokens helps the model learn
"this message contains a link / a number / money" instead of memorising the
exact values, which are different in every scam.
"""
import re

URL_RE = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+\.(?:com|in|co|org|net|xyz|top|apk|ly|gy)\b\S*)", re.I)
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}\d")
MONEY_RE = re.compile(r"(?:rs\.?|inr|₹|£|\$)\s?[\d,]+(?:\.\d+)?", re.I)
NUMBER_RE = re.compile(r"\b\d+\b")


def normalize(text: str) -> str:
    text = text.lower()
    text = URL_RE.sub(" urltoken ", text)
    text = MONEY_RE.sub(" moneytoken ", text)
    text = PHONE_RE.sub(" phonetoken ", text)
    text = NUMBER_RE.sub(" numtoken ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_many(texts):
    return [normalize(t) for t in texts]
