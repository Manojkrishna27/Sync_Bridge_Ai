from marshmallow import Schema, fields, validate

class IntegrationVersionSchema(Schema):
    id = fields.String(dump_only=True)
    version_number = fields.Integer(dump_only=True)
    snapshot = fields.Dict(dump_only=True)
    change_notes = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class IntegrationSchema(Schema):
    id = fields.String(dump_only=True)
    client_id = fields.String(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=255))
    description = fields.String(allow_none=True)
    source_system = fields.String(required=True)
    destination_system = fields.String(required=True)
    source_protocol = fields.String(required=True)
    destination_protocol = fields.String(required=True)
    integration_type = fields.String(allow_none=True)
    environment = fields.String(required=True)
    status = fields.String(dump_only=True)
    version = fields.Integer(dump_only=True)
    health_score = fields.Integer(dump_only=True)
    config = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    versions = fields.List(fields.Nested(IntegrationVersionSchema), dump_only=True)

class IntegrationListResponseSchema(Schema):
    items = fields.List(fields.Nested(IntegrationSchema(exclude=('versions',))))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
