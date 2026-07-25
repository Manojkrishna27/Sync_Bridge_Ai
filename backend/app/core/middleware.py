import uuid
from flask import request, g

CORRELATION_HEADER = "X-Correlation-ID"

def register_middleware(app):
    @app.before_request
    def before_request_func():
        # Get Correlation ID from request headers or generate a new UUID
        correlation_id = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        g.correlation_id = correlation_id

    @app.after_request
    def after_request_func(response):
        # Attach Correlation ID to response headers
        if hasattr(g, "correlation_id"):
            response.headers[CORRELATION_HEADER] = g.correlation_id
        return response
