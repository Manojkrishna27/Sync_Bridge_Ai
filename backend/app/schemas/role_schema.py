from marshmallow import Schema, fields, validate

class RoleSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    description = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class PermissionSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)

class RolePermissionSchema(Schema):
    role_id = fields.String()
    permission_id = fields.String()
    permission = fields.Nested(PermissionSchema, dump_only=True)
