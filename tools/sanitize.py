import re

GENERIC_PERSON = "Contributor"
GENERIC_ORG = "Organization"

NAME_PATTERNS = [
    r"\bพี่ไอซ์\b", r"\bNamo\b", r"\bนะโม\b",
    r"\bIce\b", r"\bIced\b", r"\bJules team\b"
]
ORG_PATTERNS = [
    r"\bNaMo[- ]?Hub\b", r"\bNamoVerse\b"
]

def sanitize_text(text: str) -> str:
    t = text
    for p in NAME_PATTERNS:
        t = re.sub(p, GENERIC_PERSON, t, flags=re.IGNORECASE)
    for p in ORG_PATTERNS:
        t = re.sub(p, GENERIC_ORG, t, flags=re.IGNORECASE)
    # trim spaces
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()