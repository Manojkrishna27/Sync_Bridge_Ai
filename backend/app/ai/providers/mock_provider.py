import re
from typing import Dict, Any, List, Optional
from .base_provider import BaseAIProvider

SYNONYMS = {
    "name": ["fullname", "first_name", "last_name", "customer_name", "user_name"],
    "email": ["email_address", "mail", "contact_email"],
    "phone": ["phone_number", "mobile", "contact_phone", "telephone"],
    "created_at": ["created_date", "creation_time", "createdat", "timestamp"],
    "address": ["street_address", "location", "addr"],
    "zip": ["postal_code", "zipcode", "postalcode", "postcode"]
}

class MockAIProvider(BaseAIProvider):
    """
    Heuristic Semantic Matcher Provider.
    Executes rule-based fuzzy field matching and synonym dictionary evaluation without external LLM API calls.
    """

    def generate_mapping_suggestions(
        self,
        source_fields: List[Dict[str, Any]],
        target_fields: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        suggestions = []

        for src in source_fields:
            src_path = src.get("path", "")
            src_leaf = src_path.split(".")[-1].lower()
            src_clean = re.sub(r"[_\-]", "", src_leaf)

            best_match = None
            highest_score = 0.0
            reason = ""
            transform = None

            for tgt in target_fields:
                tgt_path = tgt.get("path", "")
                tgt_leaf = tgt_path.split(".")[-1].lower()
                tgt_clean = re.sub(r"[_\-]", "", tgt_leaf)

                # 1. Exact Name Match
                if src_leaf == tgt_leaf or src_clean == tgt_clean:
                    best_match = tgt_path
                    highest_score = 0.98
                    reason = f"Exact field name match ('{src_leaf}' == '{tgt_leaf}')"
                    break

                # 2. Synonym Dictionary Match
                for root_key, synonym_list in SYNONYMS.items():
                    if (src_leaf in synonym_list or src_clean in synonym_list or src_leaf == root_key) and \
                       (tgt_leaf in synonym_list or tgt_clean in synonym_list or tgt_leaf == root_key):
                        best_match = tgt_path
                        highest_score = 0.90
                        reason = f"Semantic synonym match for '{root_key}'"
                        if "date" in src_leaf or "time" in src_leaf:
                            transform = "date_iso"
                        break

                # 3. Substring Containment Match
                if not best_match and (src_clean in tgt_clean or tgt_clean in src_clean):
                    best_match = tgt_path
                    highest_score = 0.75
                    reason = f"Partial token match between '{src_leaf}' and '{tgt_leaf}'"

            if best_match and highest_score >= 0.70:
                suggestions.append({
                    "source_field": src_path,
                    "target_field": best_match,
                    "confidence_score": highest_score,
                    "reason": reason,
                    "suggested_transformation": transform,
                    "suggested_validation": {"required": src.get("required", False)}
                })

        return suggestions

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        return (
            f"[MockProvider — No LLM API key configured]\n\n"
            f"Query received: '{user_message}'\n\n"
            f"Please set OPENAI_API_KEY or GEMINI_API_KEY in your .env file to get real AI responses."
        )

        suggestions = []

        for src in source_fields:
            src_path = src.get("path", "")
            src_leaf = src_path.split(".")[-1].lower()
            src_clean = re.sub(r"[_\-]", "", src_leaf)

            best_match = None
            highest_score = 0.0
            reason = ""
            transform = None

            for tgt in target_fields:
                tgt_path = tgt.get("path", "")
                tgt_leaf = tgt_path.split(".")[-1].lower()
                tgt_clean = re.sub(r"[_\-]", "", tgt_leaf)

                # 1. Exact Name Match
                if src_leaf == tgt_leaf or src_clean == tgt_clean:
                    best_match = tgt_path
                    highest_score = 0.98
                    reason = f"Exact field name match ('{src_leaf}' == '{tgt_leaf}')"
                    break

                # 2. Synonym Dictionary Match
                for root_key, synonym_list in SYNONYMS.items():
                    if (src_leaf in synonym_list or src_clean in synonym_list or src_leaf == root_key) and \
                       (tgt_leaf in synonym_list or tgt_clean in synonym_list or tgt_leaf == root_key):
                        best_match = tgt_path
                        highest_score = 0.90
                        reason = f"Semantic synonym match for '{root_key}'"
                        if "date" in src_leaf or "time" in src_leaf:
                            transform = "date_iso"
                        break

                # 3. Substring Containment Match
                if not best_match and (src_clean in tgt_clean or tgt_clean in src_clean):
                    best_match = tgt_path
                    highest_score = 0.75
                    reason = f"Partial token match between '{src_leaf}' and '{tgt_leaf}'"

            if best_match and highest_score >= 0.70:
                suggestions.append({
                    "source_field": src_path,
                    "target_field": best_match,
                    "confidence_score": highest_score,
                    "reason": reason,
                    "suggested_transformation": transform,
                    "suggested_validation": {"required": src.get("required", False)}
                })

        return suggestions
