from flask_restx import Namespace, Resource
from app.services.dashboard_service import DashboardService

ns = Namespace('dashboard', description='Executive Summary & System Metrics Operations')
api = ns
dashboard_service = DashboardService()

@ns.route('/summary')
class DashboardSummaryResource(Resource):
    @ns.doc('get_dashboard_summary')
    def get(self):
        """Get summary KPI cards and live activity feed for dashboard."""
        summary = dashboard_service.get_summary()
        return summary, 200
