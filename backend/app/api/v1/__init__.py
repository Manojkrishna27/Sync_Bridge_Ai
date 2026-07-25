from flask import Blueprint, jsonify
from flask_restx import Api
from app.core.exceptions import APIException
from app.services.monitoring_service import MonitoringService

blueprint = Blueprint('api_v1', __name__)
api = Api(
    blueprint,
    title='AI Integration Gateway API',
    version='1.0',
    description='Swagger API Documentation for AI Integration Gateway v1',
    doc='/docs'
)

@blueprint.errorhandler(APIException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@blueprint.route('/health', methods=['GET'])
def health_check():
    monitoring_svc = MonitoringService()
    return jsonify(monitoring_svc.get_system_health()), 200

# Import namespaces
from .auth import api as auth_ns
from .users import api as users_ns
from .roles import api as roles_ns
from .clients import api as clients_ns
from .integrations import api as integrations_ns
from .apikeys import api as apikeys_ns
from .audit_logs import api as audit_logs_ns
from .dashboard import api as dashboard_ns
from .execution_api import api as execution_ns
from .schema_api import api as schema_ns
from .monitoring_api import api as monitoring_ns
from .copilot_api import api as copilot_ns

api.add_namespace(auth_ns, path='/auth')
api.add_namespace(users_ns, path='/users')
api.add_namespace(roles_ns, path='/roles')
api.add_namespace(clients_ns, path='/clients')
api.add_namespace(integrations_ns, path='/integrations')
api.add_namespace(apikeys_ns, path='/apikeys')
api.add_namespace(audit_logs_ns, path='/audit-logs')
api.add_namespace(dashboard_ns, path='/dashboard')
api.add_namespace(execution_ns, path='/executions')
api.add_namespace(schema_ns, path='/schema')
api.add_namespace(monitoring_ns, path='/monitoring')
api.add_namespace(copilot_ns, path='/copilot')
