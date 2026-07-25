from flask import request
from flask_restx import Namespace, Resource
from app.services.audit_log_service import AuditLogService

ns = Namespace('audit-logs', description='Enterprise Audit Trails & Request Tracing Operations')
api = ns
audit_service = AuditLogService()

@ns.route('')
class AuditLogListResource(Resource):
    @ns.doc('list_audit_logs', params={
        'client_id': 'Filter by Client Tenant ID',
        'user_id': 'Filter by User ID',
        'resource_type': 'Filter by resource (Client, Integration, APIKey, ClientSettings)',
        'action': 'Filter by action (e.g. CLIENT_CREATE, INTEGRATION_ROLLBACK)',
        'search': 'Search keyword in action/resource/user email',
        'page': 'Page number (default 1)',
        'per_page': 'Items per page (default 10)',
        'sort_by': 'Sort field (created_at)',
        'order': 'Sort order (asc, desc)'
    })
    def get(self):
        """Query enterprise audit logs with correlation IDs and diff history."""
        client_id = request.args.get('client_id')
        user_id = request.args.get('user_id')
        resource_type = request.args.get('resource_type')
        action = request.args.get('action')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        items, total = audit_service.get_logs(
            client_id=client_id,
            user_id=user_id,
            resource_type=resource_type,
            action=action,
            search=search,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            order=order
        )

        return {
            'data': [
                {
                    'id': log.id,
                    'correlation_id': log.correlation_id,
                    'client_id': log.client_id,
                    'user_id': log.user_id,
                    'user_email': log.user_email or 'System',
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'ip_address': log.ip_address,
                    'previous_values': log.previous_values,
                    'new_values': log.new_values,
                    'created_at': log.created_at.isoformat() if log.created_at else None
                } for log in items
            ],
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if per_page else 1
            }
        }, 200
