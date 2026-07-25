from app.core.extensions import db
from app.models.base import BaseModel
from sqlalchemy.dialects.mysql import CHAR

class Role(BaseModel):
    __tablename__ = 'roles'

    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship('User', back_populates='role', lazy=True)
    role_permissions = db.relationship('RolePermission', back_populates='role', cascade='all, delete-orphan', lazy=True)


class Permission(BaseModel):
    __tablename__ = 'permissions'

    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    role_permissions = db.relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan', lazy=True)


class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    role_id = db.Column(CHAR(36), db.ForeignKey('roles.id'), primary_key=True)
    permission_id = db.Column(CHAR(36), db.ForeignKey('permissions.id'), primary_key=True)
    
    role = db.relationship('Role', back_populates='role_permissions')
    permission = db.relationship('Permission', back_populates='role_permissions')
