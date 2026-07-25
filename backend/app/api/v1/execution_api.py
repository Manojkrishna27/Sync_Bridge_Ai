from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.execution_service import ExecutionService

ns = Namespace('executions', description='Integration Execution Engine, Transformation & Tracing Operations')
api = ns

execution_service = ExecutionService()

execute_input_model = ns.model('ExecuteInput', {
    'payload': fields.Raw(required=True, description='Input payload (SOAP XML, XML, JSON, CSV string or object)')
})

@ns.route('/integrations/<string:id>/execute')
@ns.param('id', 'The integration pipeline identifier')
class IntegrationExecuteResource(Resource):
    @ns.doc('execute_integration')
    @ns.expect(execute_input_model)
    def post(self, id):
        """Execute integration pipeline: auto-detects protocol, parses payload, validates schema, applies transformations, dispatches request, and logs trace history."""
        payload = request.json.get('payload') if request.is_json else request.get_data(as_text=True)
        headers = dict(request.headers)
        return execution_service.execute(id, payload, headers)

@ns.route('/integrations/<string:id>/preview')
@ns.param('id', 'The integration pipeline identifier')
class IntegrationPreviewResource(Resource):
    @ns.doc('preview_integration')
    @ns.expect(execute_input_model)
    def post(self, id):
        """Preview transformation: parses payload, validates schema, and returns mapped output without sending or saving execution history."""
        payload = request.json.get('payload') if request.is_json else request.get_data(as_text=True)
        headers = dict(request.headers)
        return execution_service.preview(id, payload, headers)

@ns.route('/integrations/<string:id>/validate')
@ns.param('id', 'The integration pipeline identifier')
class IntegrationValidateResource(Resource):
    @ns.doc('validate_integration')
    @ns.expect(execute_input_model)
    def post(self, id):
        """Validate input payload against integration schema without executing transformation."""
        payload = request.json.get('payload') if request.is_json else request.get_data(as_text=True)
        headers = dict(request.headers)
        try:
            result = execution_service.validate_payload(id, payload, headers)
            return result, 200
        except ValueError as e:
            return {'valid': False, 'error': str(e)}, 400

@ns.route('/integrations/<string:id>/history')
@ns.param('id', 'The integration pipeline identifier')
class IntegrationHistoryResource(Resource):
    @ns.doc('get_integration_history', params={
        'page': 'Page number (default 1)',
        'per_page': 'Items per page (default 10)',
        'status': 'Filter by status (SUCCESS, FAILED, VALIDATION_ERROR)'
    })
    def get(self, id):
        """Get execution history runs for an integration with Correlation IDs and duration metrics."""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status')

        items, total = execution_service.get_history(id, page=page, per_page=per_page, status=status)

        return {
            'data': [
                {
                    'id': ex.id,
                    'correlation_id': ex.correlation_id,
                    'status': ex.status,
                    'protocol': ex.protocol,
                    'execution_mode': ex.execution_mode,
                    'payload_size': ex.payload_size,
                    'metrics': {
                        'parsing_time_ms': ex.parsing_time_ms,
                        'validation_time_ms': ex.validation_time_ms,
                        'transformation_time_ms': ex.transformation_time_ms,
                        'request_time_ms': ex.request_time_ms,
                        'total_time_ms': ex.total_time_ms
                    },
                    'dlq_eligible': ex.dlq_eligible,
                    'created_at': ex.created_at.isoformat() if ex.created_at else None
                } for ex in items
            ],
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if per_page else 1
            }
        }, 200

@ns.route('/<string:id>')
@ns.param('id', 'The execution run identifier')
class ExecutionDetailResource(Resource):
    @ns.doc('get_execution_detail')
    def get(self, id):
        """Get full execution trace, stage timelines, logs, and error details for a run."""
        try:
            ex = execution_service.get_execution(id)
            return {
                'id': ex.id,
                'correlation_id': ex.correlation_id,
                'client_id': ex.client_id,
                'integration_id': ex.integration_id,
                'status': ex.status,
                'protocol': ex.protocol,
                'execution_mode': ex.execution_mode,
                'payload_size': ex.payload_size,
                'metrics': {
                    'parsing_time_ms': ex.parsing_time_ms,
                    'validation_time_ms': ex.validation_time_ms,
                    'transformation_time_ms': ex.transformation_time_ms,
                    'request_time_ms': ex.request_time_ms,
                    'total_time_ms': ex.total_time_ms
                },
                'timeline': {
                    'received_at': ex.received_at.isoformat() if ex.received_at else None,
                    'parsed_at': ex.parsed_at.isoformat() if ex.parsed_at else None,
                    'validated_at': ex.validated_at.isoformat() if ex.validated_at else None,
                    'transformed_at': ex.transformed_at.isoformat() if ex.transformed_at else None,
                    'sent_at': ex.sent_at.isoformat() if ex.sent_at else None,
                    'response_received_at': ex.response_received_at.isoformat() if ex.response_received_at else None,
                    'completed_at': ex.completed_at.isoformat() if ex.completed_at else None
                },
                'dlq_eligible': ex.dlq_eligible,
                'request_payload': ex.request_payload,
                'response_payload': ex.response_payload,
                'logs': [
                    {
                        'step_name': l.step_name,
                        'log_level': l.log_level,
                        'message': l.message,
                        'details': l.details,
                        'timestamp': l.created_at.isoformat() if l.created_at else None
                    } for l in ex.logs
                ],
                'errors': [
                    {
                        'error_code': err.error_code,
                        'category': err.category,
                        'message': err.message,
                        'technical_details': err.technical_details,
                        'suggested_resolution': err.suggested_resolution
                    } for err in ex.errors
                ]
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404
