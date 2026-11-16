"""Rule-based red-flag detection (explainable signals shown to the user)."""
import re

RULES = [
    ("otp", "Asks for OTP / PIN / CVV", 30,
     r"\b(otp|one[\s-]?time[\s-]?password|pin|cvv|cvc|mpin|upi\s?pin)\b"),
    ("kyc", "KYC / account update threat", 25,
     r"\b(kyc|update (your )?(pan|aadhaar|account|details)|re-?verify|verification pending)\b"),
    ("blocked", "Account blocked / suspended threat", 25,
     r"\b(blocked|suspended|deactivated|frozen|will be (closed|terminated)|disabled)\b"),
    ("urgency", "Creates urgency", 15,
     r"\b(urgent|urgently|immediately|within \d+ ?(hours?|hrs?|minutes?|mins?)|today only|last chance|act now|expire[sd]?)\b"),
    ("prize", "Lottery / prize / reward bait", 25,
     r"\b(congratulations|you (have )?won|lottery|lucky draw|prize|reward|cashback of|jackpot|gift card)\b"),
    ("card", "Mentions credit/debit card", 10,
     r"\b(credit card|debit card|card (number|details)|atm card)\b"),
    ("money", "Requests payment or transfer", 15,
     r"\b(pay|transfer|send money|processing fee|registration fee|deposit)\b"),
    ("link", "Contains a link", 10, r"(https?://|www\.)\S+"),
    ("shortlink", "Shortened / disguised link", 20,
     r"\b(bit\.ly|tinyurl|goo\.gl|t\.co|cutt\.ly|rb\.gy|is\.gd|shorturl)\b"),
    ("apk", "Asks to install an app / APK", 25,
     r"(\.apk\b|\banydesk\b|\bteamviewer\b|\bquicksupport\b|\bdownload (the |our )?app\b|\binstall (this|the) app\b)"),
    ("job", "Work-from-home / easy money offer", 20,
     r"\b(work from home|part[\s-]?time job|earn \S+ (per|a) day|daily income|like (youtube )?videos)\b"),
    ("click", "Asks you to click / call back", 10,
     r"\b(click (here|the link|below)|call (us|now|immediately)|contact (immediately|now))\b"),
]
_COMPILED = [(i, label, w, re.compile(p, re.I)) for i, label, w, p in RULES]

PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}\d")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.I)

# Placeholder list until the number-reputation database is built.
REPORTED_NUMBERS = {"9876543210", "8001234567", "7012345678"}


def _last10(number: str) -> str:
    return re.sub(r"\D", "", number)[-10:]


def message_flags(message: str) -> list[dict]:
    return [{"id": i, "label": label, "weight": w}
            for i, label, w, rx in _COMPILED if rx.search(message)]


def sender_flags(sender: str | None) -> list[dict]:
    if not sender:
        return []
    flags = []
    s = sender.strip()
    digits = re.sub(r"\D", "", s)
    if digits and _last10(s) in REPORTED_NUMBERS:
        flags.append({"id": "reported", "label": "Sender number reported as fraud", "weight": 50})
    if s.startswith("+") and not s.replace(" ", "").startswith("+91"):
        flags.append({"id": "intl", "label": "International sender number", "weight": 15})
    elif len(digits) == 10 and digits[0] not in "6789":
        flags.append({"id": "odd", "label": "Unusual mobile number format", "weight": 10})
    return flags


def extract(message: str) -> tuple[list[str], list[str]]:
    numbers = list(dict.fromkeys(m.strip() for m in PHONE_RE.findall(message)))
    links = list(dict.fromkeys(URL_RE.findall(message)))
    return numbers, links


def reported_in_message(numbers: list[str]) -> list[dict]:
    return [{"id": "reported-in-msg", "label": f"Number {n} reported as fraud", "weight": 40}
            for n in numbers if _last10(n) in REPORTED_NUMBERS]
