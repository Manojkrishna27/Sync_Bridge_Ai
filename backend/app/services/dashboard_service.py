from typing import Dict, Any
from app.repositories.client_repository import ClientRepository
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.api_key_repository import APIKeyRepository
from app.services.audit_log_service import AuditLogService

class DashboardService:
    def __init__(self):
        self.client_repo = ClientRepository()
        self.integration_repo = IntegrationRepository()
        self.api_key_repo = APIKeyRepository()
        self.audit_service = AuditLogService()

    def get_summary(self) -> Dict[str, Any]:
        total_clients = self.client_repo.count_total()
        active_integrations = self.integration_repo.count_by_status('Active')
        prod_integrations = self.integration_repo.count_by_environment('Production')
        dev_integrations = self.integration_repo.count_by_environment('Development')
        active_api_keys = self.api_key_repo.count_active_keys()
        
        recent_logs = self.audit_service.get_recent_activity(limit=10)
        recent_activities = [
            {
                "id": log.id,
                "correlation_id": log.correlation_id,
                "user_email": log.user_email or "System",
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "timestamp": log.created_at.isoformat() if log.created_at else None
            }
            for log in recent_logs
        ]

        return {
            "total_clients": total_clients,
            "active_integrations": active_integrations,
            "production_integrations": prod_integrations,
            "development_integrations": dev_integrations,
            "active_api_keys": active_api_keys,
            "recent_activities": recent_activities
        }
