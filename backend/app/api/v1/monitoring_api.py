from flask import request
from flask_restx import Namespace, Resource
from app.services.monitoring_service import MonitoringService
from app.services.alert_service import AlertService
from app.core.cache import cache_service
from app.core.rate_limiter import rate_limiter

ns = Namespace('monitoring', description='Real-Time Platform Monitoring, Latency Analytics, Rate Limiting & Health APIs')
api = ns

monitoring_service = MonitoringService()
alert_service = AlertService()

@ns.route('/dashboard')
class MonitoringDashboardResource(Resource):
    @ns.doc('get_monitoring_dashboard', params={'time_range': 'Time window: 1h, 24h, 7d'})
    def get(self):
        """Get real-time system monitoring dashboard telemetry (RPM, latency, success rates, cache ratios)."""
        time_range = request.args.get('time_range', '24h')
        return monitoring_service.get_dashboard_summary(time_range), 200

@ns.route('/health')
class MonitoringHealthResource(Resource):
    @ns.doc('get_monitoring_health')
    def get(self):
        """Get system & connector health status breakdown (Healthy, Degraded, Critical, Offline)."""
        return monitoring_service.get_system_health(), 200

@ns.route('/connectors')
class MonitoringConnectorsResource(Resource):
    @ns.doc('get_monitoring_connectors')
    def get(self):
        """Get connector performance rankings (requests, latency, availability %)."""
        return {'connectors': monitoring_service.get_connector_health_metrics()}, 200

@ns.route('/alerts')
class MonitoringAlertsResource(Resource):
    @ns.doc('get_monitoring_alerts', params={'status': 'ACTIVE, ACKNOWLEDGED, RESOLVED'})
    def get(self):
        """Get active system alerts and threshold violations."""
        status = request.args.get('status')
        alerts = alert_service.get_alerts(status)
        return {
            'alerts': [
                {
                    'id': a.id,
                    'title': a.title,
                    'severity': a.severity,
                    'category': a.category,
                    'message': a.message,
                    'status': a.status,
                    'created_at': a.created_at.isoformat() if a.created_at else None
                } for a in alerts
            ]
        }, 200

@ns.route('/alerts/<string:id>/acknowledge')
@ns.param('id', 'System Alert ID')
class AlertAcknowledgeResource(Resource):
    @ns.doc('acknowledge_alert')
    def post(self, id):
        """Acknowledge an active system alert."""
        try:
            alert = alert_service.acknowledge_alert(id)
            return {'id': alert.id, 'status': alert.status, 'message': 'Alert acknowledged'}, 200
        except ValueError as e:
            return {'message': str(e)}, 404

@ns.route('/traces')
class MonitoringTracesResource(Resource):
    @ns.doc('get_monitoring_traces')
    def get(self):
        """Get OpenTelemetry-ready trace records and Correlation IDs."""
        from app.models.monitoring_model import ExecutionMetrics
        traces = ExecutionMetrics.query.order_by(ExecutionMetrics.created_at.desc()).limit(50).all()
        return {
            'traces': [
                {
                    'correlation_id': t.correlation_id,
                    'trace_id': t.trace_id,
                    'client_id': t.client_id,
                    'integration_id': t.integration_id,
                    'profiling_ms': {
                        'db_time': t.db_time_ms,
                        'parsing_time': t.parsing_time_ms,
                        'validation_time': t.validation_time_ms,
                        'transformation_time': t.transformation_time_ms,
                        'external_api_time': t.external_api_time_ms,
                        'total_time': t.total_time_ms
                    },
                    'timestamp': t.created_at.isoformat() if t.created_at else None
                } for t in traces
            ]
        }, 200

# Endpoint /api/v1/rate-limit/status
@ns.route('/rate-limit/status')
class RateLimitStatusResource(Resource):
    @ns.doc('get_rate_limit_status')
    def get(self):
        """Get current rate limiting configurations across scopes."""
        return {'configs': rate_limiter.configs}, 200

# Endpoint /api/v1/cache/statistics & invalidation
@ns.route('/cache/statistics')
class CacheStatisticsResource(Resource):
    @ns.doc('get_cache_statistics')
    def get(self):
        """Get Redis cache telemetry and hit ratios per namespace."""
        return {'namespaces': cache_service.get_namespace_statistics()}, 200

@ns.route('/cache/invalidate')
class CacheInvalidateResource(Resource):
    @ns.doc('invalidate_cache')
    def post(self):
        """Bulk invalidate Redis cache by pattern or namespace tag."""
        data = request.json or {}
        pattern = data.get('pattern')
        tag = data.get('tag')
        if pattern:
            cache_service.invalidate_pattern(pattern)
            return {'message': f"Cache matching pattern '{pattern}' flushed successfully"}, 200
        elif tag:
            cache_service.invalidate_tag(tag)
            return {'message': f"Cache matching tag '{tag}' flushed successfully"}, 200
        
        return {'message': 'Specify pattern or tag parameter'}, 400

@ns.route('/prometheus')
class MonitoringPrometheusResource(Resource):
    @ns.doc('get_prometheus_metrics')
    def get(self):
        """Get system telemetry formatted for Prometheus scraping."""
        summary = monitoring_service.get_dashboard_summary('24h')
        metrics = summary.get('metrics', {})
        
        prom_text = f"""# HELP syncbridge_rpm Requests Per Minute
# TYPE syncbridge_rpm gauge
syncbridge_rpm {metrics.get('rpm', 0.0)}

# HELP syncbridge_avg_latency_ms Average system latency in milliseconds
# TYPE syncbridge_avg_latency_ms gauge
syncbridge_avg_latency_ms {metrics.get('avg_latency_ms', 0.0)}

# HELP syncbridge_success_rate Success execution rate percentage
# TYPE syncbridge_success_rate gauge
syncbridge_success_rate {metrics.get('success_rate', 100.0)}

# HELP syncbridge_cache_hit_ratio Redis cache hit ratio percentage
# TYPE syncbridge_cache_hit_ratio gauge
syncbridge_cache_hit_ratio {metrics.get('cache_hit_ratio', 0.0)}
"""
        from flask import Response
        return Response(prom_text, mimetype='text/plain')
