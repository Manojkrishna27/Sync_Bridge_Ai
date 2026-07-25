import uuid
from datetime import datetime
from typing import List, Optional
from app.models.monitoring_model import SystemAlert
from app.services.audit_log_service import AuditLogService
from app.core.logger import get_logger
from app.core.extensions import db

logger = get_logger()

class AlertService:
    """Configurable Alert Rules Engine with suppression, user acknowledgement, and audit integration."""

    def __init__(self):
        self.audit_service = AuditLogService()

    def evaluate_thresholds(
        self,
        failure_rate: float = 0.0,
        avg_latency: float = 0.0,
        rate_limit_blocked: int = 0
    ) -> List[SystemAlert]:
        
        alerts = []

        if failure_rate > 5.0:
            alerts.append(self.trigger_alert(
                title="High System Failure Rate",
                severity="CRITICAL" if failure_rate > 15.0 else "WARNING",
                category="HIGH_FAILURE_RATE",
                message=f"System execution failure rate reaches {failure_rate:.1f}%"
            ))

        if avg_latency > 1000.0:
            alerts.append(self.trigger_alert(
                title="Slow Response Time SLA Breach",
                severity="WARNING",
                category="SLOW_LATENCY",
                message=f"Average system latency exceeded threshold: {avg_latency:.1f} ms"
            ))

        if rate_limit_blocked > 50:
            alerts.append(self.trigger_alert(
                title="Rate Limit Abuse Warning",
                severity="WARNING",
                category="RATE_LIMIT_ABUSE",
                message=f"High rate limit blocks detected: {rate_limit_blocked} blocked requests"
            ))

        return [a for a in alerts if a is not None]

    def trigger_alert(self, title: str, severity: str, category: str, message: str) -> Optional[SystemAlert]:
        # Check active alerts for suppression
        existing = SystemAlert.query.filter_by(category=category, status='ACTIVE').first()
        if existing:
            return None

        alert = SystemAlert(
            id=str(uuid.uuid4()),
            title=title,
            severity=severity,
            category=category,
            message=message,
            status='ACTIVE'
        )
        db.session.add(alert)
        db.session.commit()

        # Audit Integration
        self.audit_service.record_audit(
            action="ALERT_GENERATED",
            resource_type="SystemAlert",
            resource_id=alert.id,
            new_values={"title": title, "severity": severity, "category": category}
        )

        logger.warning(f"ALERT TRIGGERED [{severity}]: {title} - {message}")
        return alert

    def acknowledge_alert(self, alert_id: str, user_id: str = None) -> SystemAlert:
        alert = SystemAlert.query.filter_by(id=alert_id).first()
        if not alert:
            raise ValueError("Alert not found")

        alert.status = 'ACKNOWLEDGED'
        db.session.commit()

        self.audit_service.record_audit(
            user_id=user_id,
            action="ALERT_ACKNOWLEDGED",
            resource_type="SystemAlert",
            resource_id=alert.id
        )

        return alert

    def get_alerts(self, status: str = None) -> List[SystemAlert]:
        query = SystemAlert.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(SystemAlert.created_at.desc()).all()
