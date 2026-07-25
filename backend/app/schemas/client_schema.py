from marshmallow import Schema, fields, validate

class ClientSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=255))
    industry = fields.String(allow_none=True)
    contact_person = fields.String(allow_none=True)
    contact_email = fields.Email(allow_none=True)
    contact_phone = fields.String(allow_none=True)
    address = fields.String(allow_none=True)
    country = fields.String(allow_none=True)
    timezone = fields.String(allow_none=True)
    status = fields.String(dump_only=True)
    subscription_plan = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ClientListResponseSchema(Schema):
    items = fields.List(fields.Nested(ClientSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
