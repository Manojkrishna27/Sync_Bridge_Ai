from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.client_service import ClientService

ns = Namespace('clients', description='Enterprise Client & Tenant Management Operations')
api = ns

client_settings_model = ns.model('ClientSettings', {
    'timezone': fields.String(description='Client Timezone', default='UTC'),
    'default_environment': fields.String(description='Default Environment', default='Development'),
    'retry_policy': fields.Raw(description='Retry policy JSON'),
    'notification_preferences': fields.Raw(description='Notification preferences JSON'),
    'ai_preferences': fields.Raw(description='AI module preferences JSON'),
    'webhook_configuration': fields.Raw(description='Webhook endpoint settings')
})

client_model = ns.model('Client', {
    'id': fields.String(readOnly=True, description='Client Unique Identifier'),
    'name': fields.String(required=True, description='Company / Organization Name'),
    'industry': fields.String(description='Industry Sector'),
    'contact_person': fields.String(description='Primary Contact Person'),
    'contact_email': fields.String(description='Primary Contact Email'),
    'contact_phone': fields.String(description='Contact Phone Number'),
    'address': fields.String(description='Physical Office Address'),
    'country': fields.String(description='Country Location'),
    'status': fields.String(description='Tenant Status', default='Active'),
    'subscription_plan': fields.String(description='Subscription Tier'),
    'tags': fields.List(fields.String, description='Tags for filtering'),
    'notes': fields.String(description='Administrative Notes'),
    'created_at': fields.String(readOnly=True, description='Creation ISO Timestamp')
})

client_input_model = ns.model('ClientInput', {
    'name': fields.String(required=True, description='Company Name'),
    'industry': fields.String(description='Industry'),
    'contact_person': fields.String(description='Contact Person'),
    'contact_email': fields.String(description='Contact Email'),
    'contact_phone': fields.String(description='Contact Phone'),
    'address': fields.String(description='Address'),
    'country': fields.String(description='Country'),
    'subscription_plan': fields.String(description='Subscription Tier'),
    'tags': fields.List(fields.String, description='Tags list'),
    'notes': fields.String(description='Notes'),
    'settings': fields.Nested(client_settings_model, description='Initial Client Settings')
})

client_service = ClientService()

@ns.route('')
class ClientListResource(Resource):
    @ns.doc('list_clients', params={
        'page': 'Page number (default 1)',
        'per_page': 'Items per page (default 10)',
        'search': 'Search term for name/industry/contact',
        'status': 'Filter by status (Active, Inactive, Suspended)',
        'industry': 'Filter by industry sector',
        'sort_by': 'Field to sort by (created_at, name)',
        'order': 'Sort direction (asc, desc)'
    })
    def get(self):
        """List enterprise clients with server-side pagination and filtering."""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search')
        status = request.args.get('status')
        industry = request.args.get('industry')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        items, total = client_service.get_clients(
            page=page,
            per_page=per_page,
            search=search,
            status=status,
            industry=industry,
            sort_by=sort_by,
            order=order
        )

        return {
            'data': [
                {
                    'id': c.id,
                    'name': c.name,
                    'industry': c.industry,
                    'contact_person': c.contact_person,
                    'contact_email': c.contact_email,
                    'contact_phone': c.contact_phone,
                    'status': c.status,
                    'subscription_plan': c.subscription_plan,
                    'tags': c.tags or [],
                    'created_at': c.created_at.isoformat() if c.created_at else None
                } for c in items
            ],
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if per_page else 1
            }
        }, 200

    @ns.doc('create_client')
    @ns.expect(client_input_model)
    def post(self):
        """Create a new client tenant."""
        data = request.json or {}
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity() or request.headers.get('X-User-ID')
        except Exception:
            user_id = request.headers.get('X-User-ID')
        client = client_service.create_client(data, user_id=user_id)
        return {
            'message': 'Client created successfully',
            'client_id': client.id
        }, 201

@ns.route('/<string:id>')
@ns.param('id', 'The client identifier')
class ClientResource(Resource):
    @ns.doc('get_client')
    def get(self, id):
        """Get details of a specific client."""
        try:
            client = client_service.get_client(id)
            settings = client.settings
            return {
                'id': client.id,
                'name': client.name,
                'industry': client.industry,
                'contact_person': client.contact_person,
                'contact_email': client.contact_email,
                'contact_phone': client.contact_phone,
                'address': client.address,
                'country': client.country,
                'status': client.status,
                'subscription_plan': client.subscription_plan,
                'tags': client.tags or [],
                'notes': client.notes,
                'created_at': client.created_at.isoformat() if client.created_at else None,
                'settings': {
                    'timezone': settings.timezone if settings else 'UTC',
                    'default_environment': settings.default_environment if settings else 'Development',
                    'retry_policy': settings.retry_policy if settings else {},
                    'notification_preferences': settings.notification_preferences if settings else {},
                    'ai_preferences': settings.ai_preferences if settings else {},
                    'webhook_configuration': settings.webhook_configuration if settings else {}
                } if settings else {}
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404

    @ns.doc('update_client')
    @ns.expect(client_input_model)
    def put(self, id):
        """Update client information."""
        data = request.json or {}
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            client = client_service.update_client(id, data, user_id=user_id)
            return {'message': 'Client updated successfully', 'id': client.id}, 200
        except ValueError as e:
            return {'message': str(e)}, 404

    @ns.doc('archive_client')
    def delete(self, id):
        """Soft delete / archive a client."""
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            client = client_service.archive_client(id, user_id=user_id)
            return {'message': 'Client archived successfully', 'id': client.id}, 200
        except ValueError as e:
            return {'message': str(e)}, 404

@ns.route('/<string:id>/settings')
@ns.param('id', 'The client identifier')
class ClientSettingsResource(Resource):
    @ns.doc('update_client_settings')
    @ns.expect(client_settings_model)
    def put(self, id):
        """Update client specific settings (retry policy, timezone, webhooks)."""
        data = request.json or {}
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            settings = client_service.update_client_settings(id, data, user_id=user_id)
            return {'message': 'Client settings updated successfully', 'client_id': id}, 200
        except ValueError as e:
            return {'message': str(e)}, 404
