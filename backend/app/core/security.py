from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from app.core.extensions import bcrypt
from app.core.exceptions import UnauthorizedException
import datetime

def hash_password(password: str) -> str:
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.check_password_hash(hashed_password, password)

def generate_tokens(user_id: str):
    access_token = create_access_token(identity=user_id)
    # Generate custom refresh token ID to store in DB
    refresh_token = create_refresh_token(identity=user_id)
    
    decoded = decode_token(refresh_token)
    expires_at = datetime.datetime.fromtimestamp(decoded['exp'])
    
    return access_token, refresh_token, expires_at

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.repositories import user_repo
from app.core.exceptions import ForbiddenException, UnauthorizedException

def require_permission(permission_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = user_repo.get_by_id(user_id)
            
            if not user or not user.is_active:
                raise UnauthorizedException("User not found or inactive")
                
            if user.is_locked:
                raise UnauthorizedException("Account is locked")
                
            # Check permissions
            has_permission = False
            for rp in user.role.role_permissions:
                if rp.permission.name == permission_name:
                    has_permission = True
                    break
                    
            if not has_permission:
                raise ForbiddenException(f"Missing required permission: {permission_name}")
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator
