import uuid
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timezone
from app.repositories.integration_repository import IntegrationRepository
from app.models.integration import Integration
from app.models.integration_version import IntegrationVersion
from app.services.audit_log_service import AuditLogService
from app.connectors import get_connector
from app.core.logger import get_logger

logger = get_logger()

class IntegrationService:
    def __init__(self):
        self.integration_repo = IntegrationRepository()
        self.audit_service = AuditLogService()

    def get_integrations(
        self,
        client_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        protocol: Optional[str] = None,
        environment: Optional[str] = None,
        status: Optional[str] = None,
        health_status: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Tuple[List[Integration], int]:
        return self.integration_repo.get_paginated(
            client_id=client_id,
            page=page,
            per_page=per_page,
            search=search,
            protocol=protocol,
            environment=environment,
            status=status,
            health_status=health_status,
            sort_by=sort_by,
            order=order
        )

    def get_integration(self, integration_id: str) -> Integration:
        integration = self.integration_repo.get_by_id(integration_id)
        if not integration:
            raise ValueError("Integration not found")
        return integration

    def create_integration(self, client_id: str, data: Dict[str, Any], user_id: str) -> Integration:
        # Validate protocol configs via Pluggable Connectors
        source_connector = get_connector(data.get('source_protocol', data.get('source_connector', 'REST')))
        source_connector.validate(data.get('config', {}).get('source', {}))

        from app.models.user import User
        valid_user = User.query.get(user_id) if user_id else None
        created_by_id = valid_user.id if valid_user else None

        source_sys = data.get('source_system') or data.get('source_connector') or data.get('source_protocol') or 'REST'
        dest_sys = data.get('destination_system') or data.get('target_connector') or data.get('destination_protocol') or 'REST'

        integration = Integration(
            id=str(uuid.uuid4()),
            client_id=client_id,
            name=data.get('name'),
            description=data.get('description'),
            source_system=source_sys,
            destination_system=dest_sys,
            source_protocol=data.get('source_protocol', data.get('source_connector', 'REST')),
            destination_protocol=data.get('destination_protocol', data.get('target_connector', 'REST')),
            integration_type=data.get('integration_type', 'Sync'),
            environment=data.get('environment', 'Development'),
            health_status='Healthy',
            health_score=100,
            tags=data.get('tags', []),
            config=data.get('config', {}),
            created_by=created_by_id
        )

        saved = self.integration_repo.create(integration)
        self._create_version(saved.id, 1, saved.config, "Initial Creation", user_id)

        self.audit_service.record_audit(
            action="INTEGRATION_CREATE",
            resource_type="Integration",
            resource_id=saved.id,
            client_id=client_id,
            user_id=user_id,
            new_values={"name": saved.name, "environment": saved.environment}
        )

        return saved

    def update_integration(self, integration_id: str, data: Dict[str, Any], user_id: str) -> Integration:
        integration = self.get_integration(integration_id)
        previous = {"name": integration.name, "version": integration.version, "config": integration.config}

        config_changed = False
        if 'config' in data and data['config'] != integration.config:
            config_changed = True

        for key, value in data.items():
            if hasattr(integration, key) and key not in ['id', 'client_id', 'version', 'created_at', 'deleted_at']:
                setattr(integration, key, value)

        if config_changed:
            integration.version += 1
            self._create_version(
                integration.id,
                integration.version,
                integration.config,
                data.get('change_notes', 'Configuration updated'),
                user_id
            )

        updated = self.integration_repo.update(integration)

        self.audit_service.record_audit(
            action="INTEGRATION_UPDATE",
            resource_type="Integration",
            resource_id=updated.id,
            client_id=updated.client_id,
            user_id=user_id,
            previous_values=previous,
            new_values={"version": updated.version, "status": updated.status}
        )

        return updated

    def rollback_integration(self, integration_id: str, version_number: int, user_id: str) -> Integration:
        integration = self.get_integration(integration_id)
        historical_version = self.integration_repo.get_version(integration_id, version_number)

        if not historical_version:
            raise ValueError(f"Integration version {version_number} not found")

        previous_version = integration.version
        integration.config = historical_version.snapshot
        integration.version += 1

        self._create_version(
            integration.id,
            integration.version,
            integration.config,
            f"Rolled back from version {previous_version} to version {version_number}",
            user_id
        )

        updated = self.integration_repo.update(integration)

        self.audit_service.record_audit(
            action="INTEGRATION_ROLLBACK",
            resource_type="Integration",
            resource_id=integration.id,
            client_id=integration.client_id,
            user_id=user_id,
            previous_values={"version": previous_version},
            new_values={"version": updated.version, "restored_from_version": version_number}
        )

        return updated

    def clone_integration(self, integration_id: str, new_environment: str, user_id: str) -> Integration:
        source = self.get_integration(integration_id)
        cloned = Integration(
            id=str(uuid.uuid4()),
            client_id=source.client_id,
            name=f"{source.name} ({new_environment})",
            description=source.description,
            source_system=source.source_system,
            destination_system=source.destination_system,
            source_protocol=source.source_protocol,
            destination_protocol=source.destination_protocol,
            integration_type=source.integration_type,
            environment=new_environment,
            status='Inactive',
            health_status='Healthy',
            tags=source.tags,
            config=source.config,
            created_by=user_id
        )

        saved = self.integration_repo.create(cloned)
        self._create_version(saved.id, 1, saved.config, f"Cloned from integration {source.id}", user_id)

        self.audit_service.record_audit(
            action="INTEGRATION_CLONE",
            resource_type="Integration",
            resource_id=saved.id,
            client_id=saved.client_id,
            user_id=user_id,
            new_values={"cloned_from": source.id, "environment": new_environment}
        )

        return saved

    def get_version_history(self, integration_id: str) -> List[IntegrationVersion]:
        return self.integration_repo.get_all_versions(integration_id)

    def record_execution_stat(self, integration_id: str, success: bool, duration_ms: float):
        integration = self.get_integration(integration_id)
        integration.total_executions += 1
        if success:
            integration.successful_executions += 1
        else:
            integration.failed_executions += 1

        # Moving average for execution time
        if integration.total_executions > 1:
            integration.average_execution_time = (
                (integration.average_execution_time * (integration.total_executions - 1) + duration_ms)
                / integration.total_executions
            )
        else:
            integration.average_execution_time = float(duration_ms)

        integration.last_execution_time = datetime.now(timezone.utc)
        self.integration_repo.update(integration)

    def _create_version(self, integration_id: str, version_num: int, config: dict, notes: str, user_id: str):
        from app.models.user import User
        valid_user = User.query.get(user_id) if user_id else None
        created_by_id = valid_user.id if valid_user else None

        version = IntegrationVersion(
            id=str(uuid.uuid4()),
            integration_id=integration_id,
            version_number=version_num,
            snapshot=config,
            change_notes=notes,
            created_by=created_by_id
        )
        self.integration_repo.save_version(version)
