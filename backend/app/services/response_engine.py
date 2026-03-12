"""
Response Engine Service — Tracks and manages executed response actions.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from app.models.schemas import IncidentStatus, Incident, ResponseAction, ResponsePlan

logger = logging.getLogger(__name__)


class ResponseEngine:
    """Executes and tracks cybersecurity response actions."""

    def __init__(self):
        self._execution_log: list[dict] = []
        self._blocked_ips: set[str] = set()
        self._isolated_hosts: set[str] = set()

    def execute_response(self, plan: ResponsePlan, incident: Incident) -> list[dict]:
        """Execute or simulate response actions from a plan."""
        executed = []

        for action in plan.actions:
            result = self._execute_action(action, incident)
            executed.append(result)
            self._execution_log.append(result)

            # Update incident timeline
            incident.timeline.append({
                "time": datetime.utcnow().isoformat(),
                "event": f"Response action executed: {action.value}",
                "result": result.get("status"),
                "severity": "info",
            })

        if plan.auto_execute:
            incident.status = IncidentStatus.RESPONDING
        else:
            incident.status = IncidentStatus.ANALYZING

        logger.info("Executed %d response actions for incident %s", len(executed), incident.id)
        return executed

    def _execute_action(self, action: ResponseAction, incident: Incident) -> dict:
        """Simulate execution of a single response action."""
        source_ip = incident.threat.source_ip
        affected_asset = incident.threat.affected_asset

        result_map = {
            ResponseAction.BLOCK_IP: lambda: self._block_ip(source_ip),
            ResponseAction.ISOLATE_MACHINE: lambda: self._isolate_machine(affected_asset),
            ResponseAction.FORCE_PASSWORD_RESET: lambda: self._force_reset(incident),
            ResponseAction.NOTIFY_ADMIN: lambda: self._notify_admin(incident),
            ResponseAction.INCREASE_MONITORING: lambda: self._increase_monitoring(incident),
            ResponseAction.QUARANTINE_FILE: lambda: self._quarantine_file(incident),
            ResponseAction.DISABLE_ACCOUNT: lambda: self._disable_account(incident),
            ResponseAction.UPDATE_FIREWALL_RULES: lambda: self._update_firewall(source_ip),
        }

        handler = result_map.get(action)
        if handler:
            return handler()
        return {"action": action.value, "status": "skipped", "timestamp": datetime.utcnow().isoformat()}

    def _block_ip(self, ip: str) -> dict:
        self._blocked_ips.add(ip)
        return {
            "action": "block_ip",
            "target": ip,
            "status": "success",
            "message": f"IP {ip} blocked at perimeter firewall",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _isolate_machine(self, asset: str) -> dict:
        self._isolated_hosts.add(asset or "unknown")
        return {
            "action": "isolate_machine",
            "target": asset or "compromised_host",
            "status": "success",
            "message": f"Host {asset or 'compromised_host'} isolated from network",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _force_reset(self, incident: Incident) -> dict:
        return {
            "action": "force_password_reset",
            "target": "affected_accounts",
            "status": "success",
            "message": "Password reset initiated for affected accounts",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _notify_admin(self, incident: Incident) -> dict:
        return {
            "action": "notify_admin",
            "target": "soc_team",
            "status": "success",
            "message": f"SOC team notified: {incident.threat.threat_type.value} ({incident.threat.severity.value})",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _increase_monitoring(self, incident: Incident) -> dict:
        return {
            "action": "increase_monitoring",
            "target": incident.threat.source_ip,
            "status": "success",
            "message": f"Enhanced monitoring activated for {incident.threat.source_ip}",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _quarantine_file(self, incident: Incident) -> dict:
        return {
            "action": "quarantine_file",
            "target": "suspicious_files",
            "status": "success",
            "message": "Suspicious files quarantined for analysis",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _disable_account(self, incident: Incident) -> dict:
        return {
            "action": "disable_account",
            "target": "compromised_accounts",
            "status": "success",
            "message": "Compromised user accounts disabled pending investigation",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _update_firewall(self, ip: str) -> dict:
        return {
            "action": "update_firewall_rules",
            "target": ip,
            "status": "success",
            "message": f"Firewall rules updated to block traffic patterns from {ip}",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_blocked_ips(self) -> list[str]:
        return sorted(self._blocked_ips)

    def get_execution_log(self, limit: int = 50) -> list[dict]:
        return self._execution_log[-limit:]
