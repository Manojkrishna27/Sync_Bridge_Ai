from typing import List, Optional, Tuple
from app.models.audit_log import AuditLog
from app.core.extensions import db
from .base_repository import BaseRepository

class AuditLogRepository(BaseRepository):
    def __init__(self):
        super().__init__(AuditLog)

    def log_event(self, audit_entry: AuditLog) -> AuditLog:
        db.session.add(audit_entry)
        db.session.commit()
        return audit_entry

    def get_paginated(
        self,
        client_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Tuple[List[AuditLog], int]:
        
        query = self.model.query

        if client_id:
            query = query.filter(AuditLog.client_id == client_id)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if action:
            query = query.filter(AuditLog.action == action)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (AuditLog.action.ilike(search_filter)) |
                (AuditLog.resource_type.ilike(search_filter)) |
                (AuditLog.user_email.ilike(search_filter))
            )

        total = query.count()

        # Sorting
        sort_column = getattr(AuditLog, sort_by, AuditLog.created_at)
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    def get_recent(self, limit: int = 10) -> List[AuditLog]:
        return self.model.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
