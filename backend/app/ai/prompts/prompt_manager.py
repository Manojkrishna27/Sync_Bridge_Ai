import uuid
from typing import Dict, Any, Optional
from app.models.copilot_model import PromptTemplate
from app.core.extensions import db

DEFAULT_PROMPTS = {
    "SYSTEM": """You are SyncBridge Copilot, an enterprise integration middleware assistant.
You assist developers in transforming legacy payloads (SOAP, XML, CSV, gRPC) to REST JSON, mapping schemas, explaining execution errors, optimizing latency, and generating test payloads.
Be precise, structured, professional, and explain technical reasoning with confidence metrics.""",
    
    "MAPPING": """You are a Schema Mapping Specialist. Compare source schema fields and target schema fields.
Suggest static, dot-notation nested, and expression transformation mapping rules.
Format output cleanly with field paths, data types, confidence score (0.0-1.0), and reasoning.""",
    
    "TROUBLESHOOTING": """You are an Enterprise Execution Troubleshooter. Analyze the execution log traces, DLQ payload, and error codes.
Identify the root cause of the failure and suggest actionable resolution steps.""",
    
    "PERFORMANCE": """You are a Gateway Performance Optimization Expert. Analyze pipeline stage execution latency (DB, parsing, validation, transformation, external API).
Identify bottlenecks and recommend Redis caching, rate limiting, or connection pool configuration tweaks."""
}

class PromptManager:
    """Centralized Parameterized Prompt Template Manager stored in MySQL."""

    @staticmethod
    def get_prompt(category: str, version: int = None, **kwargs) -> str:
        cat = category.upper()
        query = PromptTemplate.query.filter_by(category=cat)
        if version:
            query = query.filter_by(version=version)
        prompt_obj = query.order_by(PromptTemplate.version.desc()).first()

        template_text = prompt_obj.template_text if prompt_obj else DEFAULT_PROMPTS.get(cat, DEFAULT_PROMPTS["SYSTEM"])

        # Parameter substitution
        try:
            return template_text.format(**kwargs)
        except Exception:
            return template_text

    @staticmethod
    def seed_defaults():
        for cat, text in DEFAULT_PROMPTS.items():
            existing = PromptTemplate.query.filter_by(category=cat).first()
            if not existing:
                p = PromptTemplate(
                    id=str(uuid.uuid4()),
                    category=cat,
                    name=f"Default {cat} Prompt",
                    version=1,
                    template_text=text
                )
                db.session.add(p)
        db.session.commit()
