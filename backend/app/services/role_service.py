from app.repositories import role_repo
from app.core.exceptions import BadRequestException, NotFoundException

class RoleService:
    def create_role(self, data):
        if role_repo.get_by_name(data['name']):
            raise BadRequestException("Role already exists")
        return role_repo.create(**data)

    def get_role(self, role_id):
        role = role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role not found")
        return role

    def get_all_roles(self):
        return role_repo.get_all()

    def update_role(self, role_id, data):
        role = self.get_role(role_id)
        if 'name' in data and data['name'] != role.name:
            if role_repo.get_by_name(data['name']):
                raise BadRequestException("Role already exists")
        return role_repo.update(role, **data)

    def delete_role(self, role_id):
        role = self.get_role(role_id)
        return role_repo.delete(role)

role_service = RoleService()
