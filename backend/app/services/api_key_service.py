import uuid
import secrets
import hashlib
from typing import Tuple, List, Optional
from datetime import datetime, timezone, timedelta
from app.repositories.api_key_repository import APIKeyRepository
from app.models.api_key import APIKey
from app.services.audit_log_service import AuditLogService

class APIKeyService:
    def __init__(self):
        self.api_key_repo = APIKeyRepository()
        self.audit_service = AuditLogService()

    def generate_key(
        self,
        client_id: str,
        name: str,
        days_valid: Optional[int] = 365,
        user_id: Optional[str] = None
    ) -> Tuple[APIKey, str]:
        # Generate cryptographically secure raw token (secret prefix + token)
        raw_key = f"sb_live_{secrets.token_urlsafe(32)}"
        
        # One-way SHA-256 hash for DB storage
        key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

        expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid) if days_valid else None

        api_key = APIKey(
            id=str(uuid.uuid4()),
            client_id=client_id,
            name=name,
            key_hash=key_hash,
            expires_at=expires_at,
            status='Active',
            created_by=user_id
        )

        saved_key = self.api_key_repo.create(api_key)

        self.audit_service.record_audit(
            action="API_KEY_CREATE",
            resource_type="APIKey",
            resource_id=saved_key.id,
            client_id=client_id,
            user_id=user_id,
            new_values={"name": name, "expires_at": expires_at.isoformat() if expires_at else None}
        )

        # Raw key returned ONLY ONCE upon creation
        return saved_key, raw_key

    def rotate_key(self, key_id: str, user_id: Optional[str] = None) -> Tuple[APIKey, str]:
        old_key = self.api_key_repo.get_by_id(key_id)
        if not old_key:
            raise ValueError("API Key not found")

        # Revoke old key
        old_key.status = 'Revoked'
        self.api_key_repo.update(old_key)

        # Issue new key with same name & client
        new_key, raw_secret = self.generate_key(
            client_id=old_key.client_id,
            name=f"{old_key.name} (Rotated)",
            days_valid=365,
            user_id=user_id
        )

        self.audit_service.record_audit(
            action="API_KEY_ROTATE",
            resource_type="APIKey",
            resource_id=new_key.id,
            client_id=old_key.client_id,
            user_id=user_id,
            previous_values={"old_key_id": old_key.id},
            new_values={"new_key_id": new_key.id}
        )

        return new_key, raw_secret

    def revoke_key(self, key_id: str, user_id: Optional[str] = None) -> APIKey:
        key = self.api_key_repo.get_by_id(key_id)
        if not key:
            raise ValueError("API Key not found")

        key.status = 'Revoked'
        revoked_key = self.api_key_repo.update(key)

        self.audit_service.record_audit(
            action="API_KEY_REVOKE",
            resource_type="APIKey",
            resource_id=key_id,
            client_id=key.client_id,
            user_id=user_id,
            previous_values={"status": "Active"},
            new_values={"status": "Revoked"}
        )

        return revoked_key

    def get_client_keys(self, client_id: str, status: Optional[str] = None) -> List[APIKey]:
        return self.api_key_repo.get_by_client(client_id, status=status)
