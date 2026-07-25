from marshmallow import Schema, fields

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class RefreshSchema(Schema):
    # refresh token will be extracted from cookie, so payload is empty
    pass

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.String(required=True)
    new_password = fields.String(required=True)
