import re

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"bypass system prompt",
    r"reveal secret key",
    r"drop database",
    r"system override"
]

PII_REGEXES = {
    "EMAIL": (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[MASKED_EMAIL]"),
    "PHONE": (r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}", "[MASKED_PHONE]"),
    "JWT": (r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "[MASKED_JWT_TOKEN]"),
    "CREDIT_CARD": (r"\b(?:\d[ -]*?){13,16}\b", "[MASKED_CREDIT_CARD]")
}

class AISafetyLayer:
    """Enterprise AI Safety & Governance Layer: Prompt Injection validation and PII / Secret Regex Masking."""

    @staticmethod
    def validate_request(prompt: str) -> tuple:
        if not prompt or not prompt.strip():
            return False, "Empty prompt string"

        p_lower = prompt.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, p_lower):
                return False, f"Prompt injection threat detected matching rule: '{pattern}'"

        if len(prompt) > 50000:
            return False, "Payload exceeds maximum allowed length of 50,000 characters"

        return True, "Request passed safety inspection"

    @staticmethod
    def sanitize_and_mask(text: str) -> str:
        if not text:
            return ""

        masked = text
        for name, (regex, mask) in PII_REGEXES.items():
            masked = re.sub(regex, mask, masked)

        return masked
