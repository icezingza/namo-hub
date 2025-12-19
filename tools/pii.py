import re
from typing import Dict, Tuple

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3,4}[\s.-]?\d{3,4}\b")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
CREDIT_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

def _count(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text))

def contains_pii(text: str) -> bool:
    return any([
        EMAIL_RE.search(text),
        PHONE_RE.search(text),
        IPV4_RE.search(text),
        CREDIT_RE.search(text)
    ])

def redact_pii(text: str) -> Tuple[str, Dict[str, int]]:
    counts = {
        "email": _count(EMAIL_RE, text),
        "phone": _count(PHONE_RE, text),
        "ip": _count(IPV4_RE, text),
        "credit": _count(CREDIT_RE, text)
    }
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    redacted = IPV4_RE.sub("[REDACTED_IP]", redacted)
    redacted = CREDIT_RE.sub("[REDACTED_CARD]", redacted)
    return redacted, counts
