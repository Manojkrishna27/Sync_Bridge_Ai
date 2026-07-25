from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.integration_service import IntegrationService

ns = Namespace('integrations', description='Integration Pipelines & Versioning Operations')
api = ns

integration_input_model = ns.model('IntegrationInput', {
    'client_id': fields.String(required=True, description='Parent Client / Tenant ID'),
    'name': fields.String(required=True, description='Integration Pipeline Name'),
    'description': fields.String(description='Detailed Description'),
    'source_system': fields.String(required=True, description='Source System Name (e.g. SAP, Salesforce)'),
    'destination_system': fields.String(required=True, description='Destination System Name'),
    'source_protocol': fields.String(required=True, description='Source Protocol (REST, SOAP, XML, CSV, GraphQL, SFTP)', default='REST'),
    'destination_protocol': fields.String(required=True, description='Destination Protocol', default='REST'),
    'integration_type': fields.String(description='Type of integration', default='Sync'),
    'environment': fields.String(description='Environment (Development, Staging, Production)', default='Development'),
    'tags': fields.List(fields.String, description='Category tags'),
    'config': fields.Raw(description='JSON Configuration state'),
    'change_notes': fields.String(description='Notes for configuration updates')
})

rollback_input_model = ns.model('RollbackInput', {
    'version_number': fields.Integer(required=True, description='Historical version number to restore')
})

clone_input_model = ns.model('CloneInput', {
    'target_environment': fields.String(required=True, description='Environment to clone integration into (Staging, Production)')
})

integration_service = IntegrationService()

@ns.route('')
class IntegrationListResource(Resource):
    @ns.doc('list_integrations', params={
        'client_id': 'Filter by Client Tenant ID',
        'page': 'Page number (default 1)',
        'per_page': 'Items per page (default 10)',
        'search': 'Search term for name/systems',
        'protocol': 'Filter by protocol (REST, SOAP, XML, CSV, GraphQL, SFTP)',
        'environment': 'Filter by environment (Development, Staging, Production)',
        'status': 'Filter by status (Active, Inactive)',
        'health_status': 'Filter by health status (Healthy, Warning, Critical, Offline)',
        'sort_by': 'Sort field (created_at, name)',
        'order': 'Sort order (asc, desc)'
    })
    def get(self):
        """List integrations with multi-tenant filtering, pagination, and health indicators."""
        client_id = request.args.get('client_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search')
        protocol = request.args.get('protocol')
        environment = request.args.get('environment')
        status = request.args.get('status')
        health_status = request.args.get('health_status')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        items, total = integration_service.get_integrations(
            client_id=client_id,
            page=page,
            per_page=per_page,
            search=search,
            protocol=protocol,
            environment=environment,
            status=status,
            health_status=health_status,
            sort_by=sort_by,
            order=order
        )

        return {
            'data': [
                {
                    'id': i.id,
                    'client_id': i.client_id,
                    'client_name': i.client.name if i.client else None,
                    'name': i.name,
                    'description': i.description,
                    'source_system': i.source_system,
                    'destination_system': i.destination_system,
                    'source_protocol': i.source_protocol,
                    'destination_protocol': i.destination_protocol,
                    'environment': i.environment,
                    'status': i.status,
                    'health_score': i.health_score,
                    'health_status': i.health_status,
                    'version': i.version,
                    'tags': i.tags or [],
                    'total_executions': i.total_executions,
                    'successful_executions': i.successful_executions,
                    'failed_executions': i.failed_executions,
                    'average_execution_time': i.average_execution_time,
                    'created_at': i.created_at.isoformat() if i.created_at else None
                } for i in items
            ],
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if per_page else 1
            }
        }, 200

    @ns.doc('create_integration')
    @ns.expect(integration_input_model)
    def post(self):
        """Create a new integration pipeline."""
        data = request.json or {}
        client_id = data.get('client_id')
        if not client_id:
            return {'message': 'client_id is required'}, 400

        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity() or request.headers.get('X-User-ID')
        except Exception:
            user_id = request.headers.get('X-User-ID')

        try:
            integration = integration_service.create_integration(client_id, data, user_id=user_id)
            return {
                'message': 'Integration created successfully',
                'id': integration.id,
                'version': integration.version
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400

@ns.route('/<string:id>')
@ns.param('id', 'The integration identifier')
class IntegrationResource(Resource):
    @ns.doc('get_integration')
    def get(self, id):
        """Get complete details and configuration of an integration."""
        try:
            i = integration_service.get_integration(id)
            return {
                'id': i.id,
                'client_id': i.client_id,
                'client_name': i.client.name if i.client else None,
                'name': i.name,
                'description': i.description,
                'source_system': i.source_system,
                'destination_system': i.destination_system,
                'source_protocol': i.source_protocol,
                'destination_protocol': i.destination_protocol,
                'integration_type': i.integration_type,
                'environment': i.environment,
                'status': i.status,
                'health_score': i.health_score,
                'health_status': i.health_status,
                'version': i.version,
                'tags': i.tags or [],
                'config': i.config or {},
                'execution_stats': {
                    'total_executions': i.total_executions,
                    'successful_executions': i.successful_executions,
                    'failed_executions': i.failed_executions,
                    'average_execution_time': i.average_execution_time,
                    'last_execution_time': i.last_execution_time.isoformat() if i.last_execution_time else None
                },
                'created_at': i.created_at.isoformat() if i.created_at else None
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404

    @ns.doc('update_integration')
    @ns.expect(integration_input_model)
    def put(self, id):
        """Update integration configuration and automatically increment version."""
        data = request.json or {}
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            updated = integration_service.update_integration(id, data, user_id=user_id)
            return {
                'message': 'Integration updated successfully',
                'id': updated.id,
                'version': updated.version
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 400

@ns.route('/<string:id>/versions')
@ns.param('id', 'The integration identifier')
class IntegrationVersionResource(Resource):
    @ns.doc('get_integration_versions')
    def get(self, id):
        """Get version history timeline of an integration."""
        try:
            versions = integration_service.get_version_history(id)
            return {
                'integration_id': id,
                'versions': [
                    {
                        'id': v.id,
                        'version_number': v.version_number,
                        'change_notes': v.change_notes,
                        'created_by': v.created_by,
                        'created_at': v.created_at.isoformat() if v.created_at else None,
                        'snapshot': v.snapshot
                    } for v in versions
                ]
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404

@ns.route('/<string:id>/rollback')
@ns.param('id', 'The integration identifier')
class IntegrationRollbackResource(Resource):
    @ns.doc('rollback_integration')
    @ns.expect(rollback_input_model)
    def post(self, id):
        """Rollback an integration configuration to a previous version snapshot."""
        data = request.json or {}
        version_number = data.get('version_number')
        if not version_number:
            return {'message': 'version_number is required'}, 400

        user_id = request.headers.get('X-User-ID', 'system')
        try:
            restored = integration_service.rollback_integration(id, version_number, user_id=user_id)
            return {
                'message': f'Integration successfully rolled back to version {version_number}',
                'new_version': restored.version
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 400

@ns.route('/<string:id>/clone')
@ns.param('id', 'The integration identifier')
class IntegrationCloneResource(Resource):
    @ns.doc('clone_integration')
    @ns.expect(clone_input_model)
    def post(self, id):
        """Clone an integration definition to a new environment."""
        data = request.json or {}
        target_env = data.get('target_environment', 'Staging')
        user_id = request.headers.get('X-User-ID', 'system')
        try:
            cloned = integration_service.clone_integration(id, target_env, user_id=user_id)
            return {
                'message': f'Integration cloned successfully to {target_env}',
                'id': cloned.id,
                'name': cloned.name
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400
