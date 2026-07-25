from app.models.role import Role, Permission
from app.repositories.base_repository import BaseRepository

class RoleRepository(BaseRepository):
    def __init__(self):
        super().__init__(Role)

    def get_by_name(self, name):
        return self.model.query.filter_by(name=name, deleted_at=None).first()

class PermissionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Permission)
        
    def get_by_name(self, name):
        return self.model.query.filter_by(name=name, deleted_at=None).first()

role_repo = RoleRepository()
permission_repo = PermissionRepository()
