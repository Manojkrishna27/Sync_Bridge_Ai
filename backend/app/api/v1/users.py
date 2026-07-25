from flask import request
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

from app.services import user_service
from app.schemas.user_schema import UserSchema, UserCreateSchema, UserUpdateSchema
from app.core.security import require_permission

api = Namespace('Users', description='User management operations')

@api.route('/')
class UserList(Resource):
    @jwt_required()
    @require_permission('READ_USERS')
    def get(self):
        users = user_service.get_all_users()
        return UserSchema(many=True).dump(users), 200

    @jwt_required()
    @require_permission('WRITE_USERS')
    def post(self):
        try:
            data = UserCreateSchema().load(request.json)
            user = user_service.create_user(data)
            return UserSchema().dump(user), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400

@api.route('/<string:id>')
class UserResource(Resource):
    @jwt_required()
    @require_permission('READ_USERS')
    def get(self, id):
        user = user_service.get_user(id)
        return UserSchema().dump(user), 200

    @jwt_required()
    @require_permission('WRITE_USERS')
    def put(self, id):
        try:
            data = UserUpdateSchema().load(request.json)
            user = user_service.update_user(id, data)
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    @require_permission('DELETE_USERS')
    def delete(self, id):
        user_service.delete_user(id)
        return '', 204
