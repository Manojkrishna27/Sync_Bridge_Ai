from app.models.auth import RefreshToken, LoginHistory
from app.models.audit_log import AuditLog
from app.core.extensions import db
from datetime import datetime

class AuthRepository:
    def create_refresh_token(self, token, user_id, expires_at):
        instance = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
        db.session.add(instance)
        db.session.commit()
        return instance

    def get_refresh_token(self, token):
        return RefreshToken.query.filter_by(token=token, is_revoked=False).first()

    def revoke_refresh_token(self, token):
        instance = self.get_refresh_token(token)
        if instance:
            instance.is_revoked = True
            db.session.commit()
            return True
        return False

    def log_login_history(self, user_id, ip_address, user_agent, status):
        log = LoginHistory(user_id=user_id, ip_address=ip_address, user_agent=user_agent, status=status)
        db.session.add(log)
        db.session.commit()

    def create_audit_log(self, user_id, action, resource_type, resource_id=None, details=None, ip_address=None):
        log = AuditLog(
            user_id=user_id, action=action, resource_type=resource_type, 
            resource_id=resource_id, previous_values=details, ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()

auth_repo = AuthRepository()
