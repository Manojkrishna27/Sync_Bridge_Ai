import time
from typing import Dict, Tuple, Optional
from flask import request, g
from app.core.cache import cache_service

# Default Rate Limiting Tiers: (Capacity, Refill Per Sec)
DEFAULT_CONFIGS = {
    "GLOBAL": (10000, 500.0),
    "CLIENT": (1000, 50.0),
    "API_KEY": (500, 20.0),
    "USER": (200, 10.0),
    "IP": (100, 5.0),
    "ENDPOINT": (300, 15.0)
}

class TokenBucketRateLimiter:
    """
    Advanced Multi-Tier Token Bucket Rate Limiter.
    Evaluates thresholds per Global, Client, API Key, User, IP, and Endpoint scope.
    Supports dynamic runtime reconfiguration without application restarts.
    """

    def __init__(self):
        self.configs = dict(DEFAULT_CONFIGS)
        self.in_memory_buckets: Dict[str, Dict[str, float]] = {}

    def update_scope_config(self, scope: str, capacity: int, refill_rate: float):
        self.configs[scope.upper()] = (capacity, float(refill_rate))

    def evaluate_request(
        self,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, dict]:
        
        ip_addr = request.remote_addr if request else "127.0.0.1"
        endpoint_name = endpoint or (request.endpoint if request else "api")

        scopes_to_check = [
            ("GLOBAL", "global_system"),
            ("IP", ip_addr),
            ("ENDPOINT", endpoint_name)
        ]

        if client_id:
            scopes_to_check.append(("CLIENT", client_id))
        if api_key:
            scopes_to_check.append(("API_KEY", api_key))
        if user_id:
            scopes_to_check.append(("USER", user_id))

        now = time.time()

        for scope, scope_id in scopes_to_check:
            capacity, refill_rate = self.configs.get(scope, (500, 20.0))
            bucket_key = f"rate_limit:{scope}:{scope_id}"

            is_allowed, remaining, reset_in = self._check_bucket(bucket_key, capacity, refill_rate, now)
            if not is_allowed:
                return False, {
                    "scope": scope,
                    "scope_id": scope_id,
                    "limit": capacity,
                    "remaining": 0,
                    "reset_in": reset_in
                }

        return True, {
            "scope": "NONE",
            "limit": 1000,
            "remaining": 999,
            "reset_in": 0
        }

    def _check_bucket(self, key: str, capacity: int, refill_rate: float, now: float) -> Tuple[bool, int, int]:
        bucket = self.in_memory_buckets.get(key)
        if not bucket:
            bucket = {"tokens": float(capacity), "last_refill": now}
            self.in_memory_buckets[key] = bucket

        # Calculate refilled tokens
        elapsed = now - bucket["last_refill"]
        tokens_to_add = elapsed * refill_rate
        bucket["tokens"] = min(float(capacity), bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            remaining = int(bucket["tokens"])
            return True, remaining, 0
        else:
            needed = 1.0 - bucket["tokens"]
            reset_in = int(needed / refill_rate) + 1 if refill_rate > 0 else 60
            return False, 0, reset_in

rate_limiter = TokenBucketRateLimiter()
