from flask import request
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

from app.services import role_service
from app.schemas.role_schema import RoleSchema
from app.core.security import require_permission

api = Namespace('Roles', description='Role management operations')

@api.route('/')
class RoleList(Resource):
    @jwt_required()
    @require_permission('READ_ROLES')
    def get(self):
        roles = role_service.get_all_roles()
        return RoleSchema(many=True).dump(roles), 200

    @jwt_required()
    @require_permission('WRITE_ROLES')
    def post(self):
        try:
            data = RoleSchema().load(request.json)
            role = role_service.create_role(data)
            return RoleSchema().dump(role), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400

@api.route('/<string:id>')
class RoleResource(Resource):
    @jwt_required()
    @require_permission('READ_ROLES')
    def get(self, id):
        role = role_service.get_role(id)
        return RoleSchema().dump(role), 200

    @jwt_required()
    @require_permission('WRITE_ROLES')
    def put(self, id):
        try:
            data = RoleSchema().load(request.json)
            role = role_service.update_role(id, data)
            return RoleSchema().dump(role), 200
        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    @require_permission('DELETE_ROLES')
    def delete(self, id):
        role_service.delete_role(id)
        return '', 204
