from app.core.extensions import db
from app.models.base import BaseModel
from sqlalchemy.dialects.mysql import CHAR

class User(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    
    role_id = db.Column(CHAR(36), db.ForeignKey('roles.id'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)

    # Relationships
    role = db.relationship('Role', back_populates='users')
    refresh_tokens = db.relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan', lazy=True)
    login_history = db.relationship('LoginHistory', back_populates='user', cascade='all, delete-orphan', lazy=True)
    audit_logs = db.relationship('AuditLog', foreign_keys='AuditLog.user_id', lazy=True)

    def lock_account(self):
        self.is_locked = True
        
    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.is_locked = False
