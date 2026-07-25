import os
import json
import zlib
import time
from typing import Any, Optional, Dict, List
from app.core.logger import get_logger

logger = get_logger()

class RedisCacheService:
    """
    Centralized, Distributed Redis Cache Service with In-Memory fallback.
    Supports Namespaces, Cache Tags, Pattern-based Deletion, Sliding Expiration, and zlib Compression.
    """

    def __init__(self):
        self.redis_client = None
        self._in_memory_store: Dict[str, Dict[str, Any]] = {}
        self._stats: Dict[str, Dict[str, int]] = {}

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            import redis
            self.redis_client = redis.Redis.from_url(redis_url, socket_connect_timeout=1)
            self.redis_client.ping()
        except Exception:
            self.redis_client = None

    def _get_key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}"

    def _record_stat(self, namespace: str, hit: bool):
        if namespace not in self._stats:
            self._stats[namespace] = {"hits": 0, "misses": 0}
        if hit:
            self._stats[namespace]["hits"] += 1
        else:
            self._stats[namespace]["misses"] += 1

    def get(self, namespace: str, key: str, sliding_ttl: int = None) -> Optional[Any]:
        full_key = self._get_key(namespace, key)

        if self.redis_client:
            try:
                raw = self.redis_client.get(full_key)
                if raw is not None:
                    self._record_stat(namespace, True)
                    if sliding_ttl:
                        self.redis_client.expire(full_key, sliding_ttl)
                    
                    try:
                        decompressed = zlib.decompress(raw).decode('utf-8')
                        return json.loads(decompressed)
                    except Exception:
                        return json.loads(raw.decode('utf-8'))
            except Exception as e:
                logger.warning(f"Redis get failed for {full_key}, falling back to in-memory: {str(e)}")

        # Fallback to in-memory store
        item = self._in_memory_store.get(full_key)
        if item:
            if item["expires_at"] and time.time() > item["expires_at"]:
                del self._in_memory_store[full_key]
                self._record_stat(namespace, False)
                return None
            
            self._record_stat(namespace, True)
            if sliding_ttl:
                item["expires_at"] = time.time() + sliding_ttl
            return item["data"]

        self._record_stat(namespace, False)
        return None

    def set(self, namespace: str, key: str, value: Any, ttl: int = 3600, tags: List[str] = None, compress: bool = False):
        full_key = self._get_key(namespace, key)
        json_str = json.dumps(value)
        data_bytes = json_str.encode('utf-8')

        if compress and len(data_bytes) > 10240: # 10 KB threshold
            data_bytes = zlib.compress(data_bytes)

        if self.redis_client:
            try:
                self.redis_client.setex(full_key, ttl, data_bytes)
                if tags:
                    for tag in tags:
                        tag_key = f"tag:{tag}"
                        self.redis_client.sadd(tag_key, full_key)
                return
            except Exception as e:
                logger.warning(f"Redis set failed for {full_key}: {str(e)}")

        # Fallback to in-memory store
        self._in_memory_store[full_key] = {
            "data": value,
            "expires_at": time.time() + ttl if ttl else None,
            "tags": tags or []
        }

    def invalidate_pattern(self, pattern: str):
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis pattern delete failed for {pattern}: {str(e)}")

        # Fallback in-memory pattern delete
        matching_keys = [k for k in self._in_memory_store.keys() if pattern.replace("*", "") in k]
        for k in matching_keys:
            self._in_memory_store.pop(k, None)

    def invalidate_tag(self, tag: str):
        tag_key = f"tag:{tag}"
        if self.redis_client:
            try:
                keys = self.redis_client.smembers(tag_key)
                if keys:
                    self.redis_client.delete(*keys)
                self.redis_client.delete(tag_key)
            except Exception as e:
                logger.warning(f"Redis tag delete failed for {tag}: {str(e)}")

        matching = [k for k, v in self._in_memory_store.items() if tag in v.get("tags", [])]
        for k in matching:
            self._in_memory_store.pop(k, None)

    def get_namespace_statistics(self) -> Dict[str, dict]:
        res = {}
        for ns, stat in self._stats.items():
            total = stat["hits"] + stat["misses"]
            ratio = round((stat["hits"] / total) * 100, 2) if total > 0 else 0.0
            res[ns] = {
                "hits": stat["hits"],
                "misses": stat["misses"],
                "total_requests": total,
                "hit_ratio": ratio
            }
        return res

cache_service = RedisCacheService()
