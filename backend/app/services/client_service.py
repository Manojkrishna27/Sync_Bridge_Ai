import uuid
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from app.repositories.client_repository import ClientRepository
from app.models.client import Client
from app.models.client_settings import ClientSettings
from app.services.audit_log_service import AuditLogService

class ClientService:
    def __init__(self):
        self.client_repo = ClientRepository()
        self.audit_service = AuditLogService()

    def get_clients(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        tag: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Tuple[list, int]:
        return self.client_repo.get_paginated(
            page=page,
            per_page=per_page,
            search=search,
            status=status,
            industry=industry,
            tag=tag,
            sort_by=sort_by,
            order=order
        )

    def get_client(self, client_id: str) -> Client:
        client = self.client_repo.get_by_id(client_id)
        if not client:
            raise ValueError("Client not found")
        return client

    def create_client(self, data: Dict[str, Any], user_id: str) -> Client:
        client_id = str(uuid.uuid4())
        from app.models.user import User
        valid_user = User.query.get(user_id) if user_id else None
        created_by_id = valid_user.id if valid_user else None

        client = Client(
            id=client_id,
            name=data.get('name'),
            industry=data.get('industry'),
            contact_person=data.get('contact_person'),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone'),
            address=data.get('address'),
            country=data.get('country'),
            subscription_plan=data.get('subscription_plan'),
            tags=data.get('tags', []),
            notes=data.get('notes'),
            created_by=created_by_id
        )

        saved_client = self.client_repo.create(client)

        # Create default ClientSettings
        settings_data = data.get('settings', {})
        settings = ClientSettings(
            id=str(uuid.uuid4()),
            client_id=client_id,
            timezone=settings_data.get('timezone', 'UTC'),
            default_environment=settings_data.get('default_environment', 'Development'),
            retry_policy=settings_data.get('retry_policy', {"max_retries": 3, "backoff_factor": 2}),
            notification_preferences=settings_data.get('notification_preferences', {"email": True}),
            ai_preferences=settings_data.get('ai_preferences', {"auto_mapping": True}),
            webhook_configuration=settings_data.get('webhook_configuration', {})
        )
        self.client_repo.save_settings(settings)

        self.audit_service.record_audit(
            action="CLIENT_CREATE",
            resource_type="Client",
            resource_id=saved_client.id,
            client_id=saved_client.id,
            user_id=user_id,
            new_values={"name": saved_client.name, "industry": saved_client.industry}
        )

        return saved_client

    def update_client(self, client_id: str, data: Dict[str, Any], user_id: Optional[str] = None) -> Client:
        client = self.get_client(client_id)
        previous = {"name": client.name, "status": client.status, "tags": client.tags}

        for key, value in data.items():
            if hasattr(client, key) and key not in ['id', 'created_at', 'deleted_at']:
                setattr(client, key, value)

        updated_client = self.client_repo.update(client)

        self.audit_service.record_audit(
            action="CLIENT_UPDATE",
            resource_type="Client",
            resource_id=updated_client.id,
            client_id=updated_client.id,
            user_id=user_id,
            previous_values=previous,
            new_values={"name": updated_client.name, "status": updated_client.status, "tags": updated_client.tags}
        )

        return updated_client

    def update_client_settings(self, client_id: str, data: Dict[str, Any], user_id: Optional[str] = None) -> ClientSettings:
        settings = self.client_repo.get_settings(client_id)
        if not settings:
            settings = ClientSettings(id=str(uuid.uuid4()), client_id=client_id)

        previous = {
            "timezone": settings.timezone,
            "default_environment": settings.default_environment,
            "retry_policy": settings.retry_policy
        }

        for key, value in data.items():
            if hasattr(settings, key) and key not in ['id', 'client_id']:
                setattr(settings, key, value)

        saved_settings = self.client_repo.save_settings(settings)

        self.audit_service.record_audit(
            action="CLIENT_SETTINGS_UPDATE",
            resource_type="ClientSettings",
            resource_id=saved_settings.id,
            client_id=client_id,
            user_id=user_id,
            previous_values=previous,
            new_values=data
        )

        return saved_settings

    def archive_client(self, client_id: str, user_id: Optional[str] = None) -> Client:
        client = self.get_client(client_id)
        client.status = 'Inactive'
        client.deleted_at = datetime.now(timezone.utc)
        archived_client = self.client_repo.update(client)

        self.audit_service.record_audit(
            action="CLIENT_ARCHIVE",
            resource_type="Client",
            resource_id=client_id,
            client_id=client_id,
            user_id=user_id,
            previous_values={"status": "Active"},
            new_values={"status": "Inactive", "deleted_at": archived_client.deleted_at.isoformat()}
        )

        return archived_client
