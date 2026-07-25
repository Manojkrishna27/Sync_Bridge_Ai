from marshmallow import Schema, fields, validate
from app.schemas.role_schema import RoleSchema

class UserSchema(Schema):
    id = fields.String(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    role_id = fields.String(required=True)
    role = fields.Nested(RoleSchema, dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    is_locked = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserCreateSchema(UserSchema):
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))

class UserUpdateSchema(Schema):
    email = fields.Email()
    first_name = fields.String(validate=validate.Length(min=1, max=100))
    last_name = fields.String(validate=validate.Length(min=1, max=100))
    role_id = fields.String()
    is_active = fields.Boolean()
