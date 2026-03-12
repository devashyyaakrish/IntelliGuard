"""
Threat Detection Service — High-level orchestration of threat analysis workflows.
"""

import logging
from datetime import datetime, timedelta

from app.models.schemas import ProcessedEvent, Severity, ThreatDetection, ThreatType

logger = logging.getLogger(__name__)


class ThreatDetectionService:
    """Service layer for threat intelligence management and enrichment."""

    SEVERITY_SCORE_MAP = {
        Severity.CRITICAL: 100,
        Severity.HIGH: 75,
        Severity.MEDIUM: 50,
        Severity.LOW: 25,
        Severity.INFO: 5,
    }

    def __init__(self):
        self._threat_store: list[ThreatDetection] = []
        self._false_positive_registry: set[str] = set()

    def record_threat(self, threat: ThreatDetection):
        """Store a confirmed threat detection."""
        self._threat_store.append(threat)
        logger.info("Threat recorded: %s [%s] confidence=%.2f",
                    threat.threat_type.value, threat.severity.value, threat.confidence)

    def get_active_threats(self, window_minutes: int = 60) -> list[ThreatDetection]:
        """Return threats detected within the last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        return [t for t in self._threat_store if t.timestamp > cutoff]

    def compute_risk_score(self, window_minutes: int = 30) -> float:
        """Compute an overall risk score from recent threats (0.0 – 1.0)."""
        active = self.get_active_threats(window_minutes)
        if not active:
            return 0.0

        weighted_sum = sum(
            self.SEVERITY_SCORE_MAP[t.severity] * t.confidence
            for t in active
        )
        max_possible = len(active) * 100
        return min(weighted_sum / max_possible, 1.0)

    def get_threat_heatmap(self) -> list[dict]:
        """Return threat counts per type for the attack frequency chart."""
        counts: dict[str, int] = {}
        for t in self._threat_store[-500:]:
            tp = t.threat_type.value
            counts[tp] = counts.get(tp, 0) + 1
        return [{"label": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]

    def get_severity_distribution(self) -> dict[str, int]:
        recent = self.get_active_threats(120)
        dist: dict[str, int] = {}
        for t in recent:
            dist[t.severity.value] = dist.get(t.severity.value, 0) + 1
        return dist

    def mark_false_positive(self, threat_id: str):
        self._false_positive_registry.add(threat_id)

    def get_top_attackers(self, limit: int = 10) -> list[dict]:
        """Identify top source IPs by threat count."""
        counts: dict[str, int] = {}
        for t in self._threat_store[-1000:]:
            if t.source_ip:
                counts[t.source_ip] = counts.get(t.source_ip, 0) + 1
        return [
            {"ip": ip, "count": cnt}
            for ip, cnt in sorted(counts.items(), key=lambda x: -x[1])[:limit]
        ]
