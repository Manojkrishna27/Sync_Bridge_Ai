from app.repositories import user_repo, role_repo
from app.core.security import hash_password
from app.core.exceptions import BadRequestException, NotFoundException

class UserService:
    def create_user(self, data):
        if user_repo.get_by_email(data['email']):
            raise BadRequestException("Email already exists")
            
        role = role_repo.get_by_id(data['role_id'])
        if not role:
            raise BadRequestException("Role not found")
            
        data['password_hash'] = hash_password(data.pop('password'))
        return user_repo.create(**data)

    def get_user(self, user_id):
        user = user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def get_all_users(self):
        return user_repo.get_all()

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if 'email' in data and data['email'] != user.email:
            if user_repo.get_by_email(data['email']):
                raise BadRequestException("Email already exists")
                
        if 'role_id' in data:
            if not role_repo.get_by_id(data['role_id']):
                raise BadRequestException("Role not found")
                
        return user_repo.update(user, **data)

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        return user_repo.delete(user)

user_service = UserService()
