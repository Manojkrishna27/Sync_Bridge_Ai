from typing import List, Optional, Tuple
from app.models.integration_execution import IntegrationExecution, ExecutionLog, ExecutionError
from .base_repository import BaseRepository

class ExecutionRepository(BaseRepository):
    def __init__(self):
        super().__init__(IntegrationExecution)

    def get_by_integration(
        self,
        integration_id: str,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Tuple[List[IntegrationExecution], int]:
        
        query = self.model.query.filter_by(integration_id=integration_id)
        if status:
            query = query.filter_by(status=status)

        total = query.count()

        sort_column = getattr(IntegrationExecution, sort_by, IntegrationExecution.created_at)
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    def get_execution_detail(self, execution_id: str) -> Optional[IntegrationExecution]:
        return self.model.query.filter_by(id=execution_id).first()
