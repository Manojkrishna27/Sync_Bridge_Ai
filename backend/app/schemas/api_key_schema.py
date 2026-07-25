from marshmallow import Schema, fields, validate

class APIKeySchema(Schema):
    id = fields.String(dump_only=True)
    client_id = fields.String(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=255))
    status = fields.String(dump_only=True)
    expires_at = fields.DateTime(dump_only=True)
    last_used_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class APIKeyCreateRequestSchema(Schema):
    client_id = fields.String(required=True)
    name = fields.String(required=True)
    days_valid = fields.Integer(allow_none=True)

class APIKeyCreateResponseSchema(Schema):
    api_key = fields.Nested(APIKeySchema)
    raw_key = fields.String() # Only returned once
