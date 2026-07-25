from sqlalchemy import or_
from typing import List, Optional, Tuple
from app.models.integration import Integration
from app.models.integration_version import IntegrationVersion
from app.core.extensions import db
from .base_repository import BaseRepository

class IntegrationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Integration)

    def get_paginated(
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
        
        query = self.model.query.filter_by(deleted_at=None)

        if client_id:
            query = query.filter(Integration.client_id == client_id)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(or_(
                Integration.name.ilike(search_filter),
                Integration.source_system.ilike(search_filter),
                Integration.destination_system.ilike(search_filter)
            ))
            
        if protocol:
            query = query.filter(or_(
                Integration.source_protocol.ilike(protocol),
                Integration.destination_protocol.ilike(protocol)
            ))

        if environment:
            query = query.filter(Integration.environment == environment)
            
        if status:
            query = query.filter(Integration.status == status)

        if health_status:
            query = query.filter(Integration.health_status == health_status)

        total = query.count()

        sort_column = getattr(Integration, sort_by, Integration.created_at)
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    def count_by_status(self, status: str = 'Active') -> int:
        return self.model.query.filter_by(status=status, deleted_at=None).count()

    def count_by_environment(self, environment: str) -> int:
        return self.model.query.filter_by(environment=environment, deleted_at=None).count()

    def save_version(self, integration_version: IntegrationVersion) -> IntegrationVersion:
        db.session.add(integration_version)
        db.session.commit()
        return integration_version

    def get_version(self, integration_id: str, version_number: int) -> Optional[IntegrationVersion]:
        return IntegrationVersion.query.filter_by(
            integration_id=integration_id, 
            version_number=version_number,
            deleted_at=None
        ).first()

    def get_all_versions(self, integration_id: str) -> List[IntegrationVersion]:
        return IntegrationVersion.query.filter_by(
            integration_id=integration_id,
            deleted_at=None
        ).order_by(IntegrationVersion.version_number.desc()).all()
