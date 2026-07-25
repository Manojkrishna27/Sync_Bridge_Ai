import logging
import json
import time
from flask import g, has_request_context

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Request context additions
        if has_request_context():
            log_data["correlation_id"] = getattr(g, "correlation_id", None)
            log_data["user_id"] = getattr(g, "user_id", None)
            log_data["client_id"] = getattr(g, "client_id", None)
        else:
            log_data["correlation_id"] = getattr(record, "correlation_id", None)
            log_data["user_id"] = getattr(record, "user_id", None)
            log_data["client_id"] = getattr(record, "client_id", None)

        if hasattr(record, "resource_id"):
            log_data["resource_id"] = record.resource_id

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_structured_logging(app=None):
    logger = logging.getLogger("syncbridge")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        
    if app:
        app.logger = logger

def get_logger():
    return logging.getLogger("syncbridge")
