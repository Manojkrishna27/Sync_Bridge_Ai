from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class RegisterSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))

class RefreshSchema(Schema):
    # refresh token will be extracted from cookie, so payload is empty
    pass

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.String(required=True)
    new_password = fields.String(required=True)
