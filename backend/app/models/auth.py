from datetime import datetime
from app.core.extensions import db
from app.models.base import BaseModel
from sqlalchemy.dialects.mysql import CHAR

class RefreshToken(BaseModel):
    __tablename__ = 'refresh_tokens'

    token = db.Column(db.String(512), unique=True, nullable=False, index=True)
    user_id = db.Column(CHAR(36), db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_revoked = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='refresh_tokens')


class LoginHistory(BaseModel):
    __tablename__ = 'login_history'

    user_id = db.Column(CHAR(36), db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False) # SUCCESS, FAILED
    
    user = db.relationship('User', back_populates='login_history')
