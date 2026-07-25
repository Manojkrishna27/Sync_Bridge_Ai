import json
import time
from typing import Any, Dict
from .base_connector import BaseConnector

class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class RESTConnector(BaseConnector):
    """Connector implementation for REST HTTP web services with Circuit Breaker support."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_state_change = time.time()

    def validate(self, config: Dict[str, Any]) -> bool:
        return True

    def parse(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except Exception:
                return {"raw_text": payload}
        return {}

    def transform(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        transformed = dict(data)
        mappings = rules.get("mappings", {})
        for src, dest in mappings.items():
            if src in data:
                transformed[dest] = transformed.pop(src)
        return transformed

    def check_circuit_breaker(self):
        now = time.time()
        if self.state == CircuitBreakerState.OPEN:
            if now - self.last_state_change > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.last_state_change = now
            else:
                raise Exception("Circuit Breaker is OPEN. Target endpoint is currently unavailable.")

    def record_success(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.last_state_change = time.time()

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_state_change = time.time()

    def send(self, data: Dict[str, Any], endpoint_config: Dict[str, Any]) -> Dict[str, Any]:
        self.check_circuit_breaker()
        url = endpoint_config.get("url", "https://api.example.com/endpoint")
        method = endpoint_config.get("method", "POST").upper()
        
        try:
            # Simulated HTTP client call
            result = {
                "status": "success",
                "protocol": "REST",
                "url": url,
                "method": method,
                "circuit_breaker_state": self.state,
                "data": data
            }
            self.record_success()
            return result
        except Exception as err:
            self.record_failure()
            raise err

    def receive(self, source_config: Dict[str, Any]) -> Any:
        return {"status": "received", "source": source_config.get("url")}
