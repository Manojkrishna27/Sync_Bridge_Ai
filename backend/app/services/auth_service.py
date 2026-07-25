from app.repositories import user_repo, auth_repo
from app.core.security import check_password, generate_tokens, hash_password
from app.core.exceptions import UnauthorizedException, BadRequestException
from flask import request

class AuthService:
    def login(self, email, password, ip_address, user_agent):
        user = user_repo.get_by_email(email)
        
        if not user:
            # Avoid timing attacks by faking a hash check
            hash_password("dummy")
            auth_repo.log_login_history(None, ip_address, user_agent, "FAILED")
            raise UnauthorizedException("Invalid credentials")

        if user.is_locked:
            raise UnauthorizedException("Account is locked. Please contact support.")

        if not check_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.lock_account()
            user_repo.update(user)
            auth_repo.log_login_history(user.id, ip_address, user_agent, "FAILED")
            raise UnauthorizedException("Invalid credentials")

        # Success
        user.reset_failed_attempts()
        user_repo.update(user)
        
        access_token, refresh_token, expires_at = generate_tokens(user.id)
        
        auth_repo.create_refresh_token(refresh_token, user.id, expires_at)
        auth_repo.log_login_history(user.id, ip_address, user_agent, "SUCCESS")
        
        return access_token, refresh_token

    def logout(self, refresh_token):
        if refresh_token:
            auth_repo.revoke_refresh_token(refresh_token)
            
    def refresh(self, refresh_token, user_id):
        token_record = auth_repo.get_refresh_token(refresh_token)
        if not token_record or token_record.is_revoked:
            raise UnauthorizedException("Invalid or revoked refresh token")
            
        # Rotate refresh token
        auth_repo.revoke_refresh_token(refresh_token)
        access_token, new_refresh_token, expires_at = generate_tokens(user_id)
        auth_repo.create_refresh_token(new_refresh_token, user_id, expires_at)
        
        return access_token, new_refresh_token

auth_service = AuthService()
