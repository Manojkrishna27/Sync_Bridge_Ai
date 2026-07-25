from sqlalchemy import or_
from typing import List, Optional, Tuple
from app.models.client import Client
from app.models.client_settings import ClientSettings
from app.core.extensions import db
from .base_repository import BaseRepository

class ClientRepository(BaseRepository):
    def __init__(self):
        super().__init__(Client)

    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        tag: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Tuple[List[Client], int]:
        
        query = self.model.query.filter_by(deleted_at=None)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(or_(
                Client.name.ilike(search_filter),
                Client.industry.ilike(search_filter),
                Client.contact_person.ilike(search_filter),
                Client.contact_email.ilike(search_filter)
            ))
            
        if status:
            query = query.filter(Client.status == status)

        if industry:
            query = query.filter(Client.industry == industry)

        total = query.count()

        # Sorting
        sort_column = getattr(Client, sort_by, Client.created_at)
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    def count_total(self) -> int:
        return self.model.query.filter_by(deleted_at=None).count()

    def get_settings(self, client_id: str) -> Optional[ClientSettings]:
        return ClientSettings.query.filter_by(client_id=client_id, deleted_at=None).first()

    def save_settings(self, settings: ClientSettings) -> ClientSettings:
        db.session.add(settings)
        db.session.commit()
        return settings
