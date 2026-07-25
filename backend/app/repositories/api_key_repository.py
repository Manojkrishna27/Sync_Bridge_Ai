from typing import List, Optional
from app.models.api_key import APIKey
from .base_repository import BaseRepository

class APIKeyRepository(BaseRepository):
    def __init__(self):
        super().__init__(APIKey)

    def get_by_client(self, client_id: str, status: Optional[str] = None) -> List[APIKey]:
        query = self.model.query.filter_by(client_id=client_id, deleted_at=None)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(APIKey.created_at.desc()).all()

    def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        return self.model.query.filter_by(key_hash=key_hash, status='Active', deleted_at=None).first()

    def count_active_keys(self) -> int:
        return self.model.query.filter_by(status='Active', deleted_at=None).count()
