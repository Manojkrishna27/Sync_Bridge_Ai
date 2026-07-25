from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.api_key_service import APIKeyService

ns = Namespace('apikeys', description='Client API Key Security & Lifecycle Operations')
api = ns

api_key_input_model = ns.model('APIKeyInput', {
    'client_id': fields.String(required=True, description='Parent Client / Tenant ID'),
    'name': fields.String(required=True, description='Key Name / Description'),
    'days_valid': fields.Integer(description='Validity period in days (default 365)', default=365)
})

api_key_service = APIKeyService()

@ns.route('')
class APIKeyListResource(Resource):
    @ns.doc('list_api_keys', params={
        'client_id': 'Filter keys by Client Tenant ID',
        'status': 'Filter by key status (Active, Revoked, Expired)'
    })
    def get(self):
        """List API keys for a client (raw keys are NEVER included)."""
        client_id = request.args.get('client_id')
        if not client_id:
            return {'message': 'client_id query parameter is required'}, 400

        status = request.args.get('status')
        keys = api_key_service.get_client_keys(client_id, status=status)

        return {
            'client_id': client_id,
            'keys': [
                {
                    'id': k.id,
                    'name': k.name,
                    'status': k.status,
                    'expires_at': k.expires_at.isoformat() if k.expires_at else None,
                    'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None,
                    'created_at': k.created_at.isoformat() if k.created_at else None
                } for k in keys
            ]
        }, 200

    @ns.doc('generate_api_key')
    @ns.expect(api_key_input_model)
    def post(self):
        """Generate a new client API Key. IMPORTANT: The raw API key secret is returned ONLY ONCE."""
        data = request.json or {}
        client_id = data.get('client_id')
        name = data.get('name')
        if not client_id or not name:
            return {'message': 'client_id and name are required'}, 400

        days_valid = data.get('days_valid', 365)
        user_id = request.headers.get('X-User-ID', 'system')

        saved_key, raw_key = api_key_service.generate_key(
            client_id=client_id,
            name=name,
            days_valid=days_valid,
            user_id=user_id
        )

        return {
            'message': 'API Key generated successfully. Copy the raw key now, it will not be shown again.',
            'id': saved_key.id,
            'name': saved_key.name,
            'raw_api_key': raw_key,
            'expires_at': saved_key.expires_at.isoformat() if saved_key.expires_at else None
        }, 201

@ns.route('/<string:id>/rotate')
@ns.param('id', 'The API key identifier')
class APIKeyRotateResource(Resource):
    @ns.doc('rotate_api_key')
    def post(self, id):
        """Rotate an API Key: Revokes old key and issues new token. Raw key is returned ONLY ONCE."""
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            new_key, raw_key = api_key_service.rotate_key(id, user_id=user_id)
            return {
                'message': 'API Key rotated successfully. Copy the new raw key now.',
                'id': new_key.id,
                'name': new_key.name,
                'raw_api_key': raw_key,
                'expires_at': new_key.expires_at.isoformat() if new_key.expires_at else None
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404

@ns.route('/<string:id>/revoke')
@ns.param('id', 'The API key identifier')
class APIKeyRevokeResource(Resource):
    @ns.doc('revoke_api_key')
    def post(self, id):
        """Revoke an active API Key."""
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            revoked = api_key_service.revoke_key(id, user_id=user_id)
            return {
                'message': 'API Key revoked successfully',
                'id': revoked.id,
                'status': revoked.status
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404
