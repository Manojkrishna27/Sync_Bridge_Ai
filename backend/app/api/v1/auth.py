from flask import request, jsonify, make_response
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services import auth_service
from app.schemas.auth_schema import LoginSchema, RegisterSchema, ForgotPasswordSchema, ResetPasswordSchema
from app.schemas.user_schema import UserSchema

api = Namespace('Auth', description='Authentication related operations')

@api.route('/login')
class Login(Resource):
    def post(self):
        try:
            data = LoginSchema().load(request.json)
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            access_token, refresh_token = auth_service.login(
                data['email'], data['password'], ip_address, user_agent
            )
            
            resp = make_response(jsonify({
                "message": "Login successful",
                "access_token": access_token
            }), 200)
            
            # Set refresh token in HttpOnly cookie
            resp.set_cookie(
                'refresh_token', refresh_token,
                httponly=True, secure=False, samesite='Lax' # Secure=True for prod
            )
            return resp
            
        except ValidationError as err:
            # Flatten marshmallow errors into a human-readable message
            first_msg = next(iter(err.messages.values()))[0]
            return {"message": first_msg}, 400

@api.route('/register')
class Register(Resource):
    def post(self):
        try:
            data = RegisterSchema().load(request.json or {})
            user = auth_service.register(
                name=data['name'],
                email=data['email'],
                password=data['password'],
            )
            return {"message": "Account created successfully.", "user": UserSchema().dump(user)}, 201
        except ValidationError as err:
            first_msg = next(iter(err.messages.values()))[0]
            return {"message": first_msg}, 400

@api.route('/logout')
class Logout(Resource):
    def post(self):
        refresh_token = request.cookies.get('refresh_token')
        if refresh_token:
            auth_service.logout(refresh_token)
            
        resp = make_response(jsonify({"message": "Logout successful"}), 200)
        resp.delete_cookie('refresh_token')
        return resp

@api.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True, locations=["cookies"])
    def post(self):
        refresh_token = request.cookies.get('refresh_token')
        user_id = get_jwt_identity()
        
        access_token, new_refresh_token = auth_service.refresh(refresh_token, user_id)
        
        resp = make_response(jsonify({
            "access_token": access_token
        }), 200)
        
        resp.set_cookie(
            'refresh_token', new_refresh_token,
            httponly=True, secure=False, samesite='Lax'
        )
        return resp

@api.route('/me')
class CurrentUser(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        from app.services import user_service
        from app.schemas.user_schema import UserSchema
        
        user = user_service.get_user(user_id)
        return UserSchema().dump(user), 200

@api.route('/forgot-password')
class ForgotPassword(Resource):
    def post(self):
        # Implementation for generating token and sending email (mocked)
        return {"message": "Password reset instructions sent if email exists"}, 200

@api.route('/reset-password')
class ResetPassword(Resource):
    def post(self):
        # Implementation for verifying token and updating password
        return {"message": "Password reset successful"}, 200
