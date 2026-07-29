from marshmallow import Schema, fields, validate

class RoleSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    description = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    permissions = fields.Method('get_permissions')

    def get_permissions(self, role):
        return [
            {'id': rp.permission.id, 'name': rp.permission.name, 'description': rp.permission.description}
            for rp in (role.role_permissions or [])
            if rp.permission
        ]

class PermissionSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)

class RolePermissionSchema(Schema):
    role_id = fields.String()
    permission_id = fields.String()
    permission = fields.Nested(PermissionSchema, dump_only=True)
