import uuid
from typing import Dict, Any, Optional, Tuple, List
from flask import g, request, has_request_context
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.audit_log import AuditLog
from app.core.logger import get_logger

logger = get_logger()

class AuditLogService:
    def __init__(self):
        self.audit_repo = AuditLogRepository()

    def record_audit(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        client_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        
        correlation_id = None
        ip_address = None

        if has_request_context():
            correlation_id = getattr(g, "correlation_id", None)
            ip_address = request.remote_addr
            if not user_id and hasattr(g, "current_user"):
                user_id = getattr(g.current_user, "id", None)
                user_email = getattr(g.current_user, "email", None)

        audit_entry = AuditLog(
            id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            client_id=client_id,
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            previous_values=previous_values,
            new_values=new_values
        )

        logger.info(
            f"Audit event recorded: {action} on {resource_type} ({resource_id})",
            extra={"resource_id": resource_id, "correlation_id": correlation_id, "user_id": user_id, "client_id": client_id}
        )

        return self.audit_repo.log_event(audit_entry)

    def get_logs(
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
        return self.audit_repo.get_paginated(
            client_id=client_id,
            user_id=user_id,
            resource_type=resource_type,
            action=action,
            search=search,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            order=order
        )

    def get_recent_activity(self, limit: int = 10) -> List[AuditLog]:
        return self.audit_repo.get_recent(limit)
