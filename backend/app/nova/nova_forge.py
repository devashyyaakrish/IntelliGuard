"""
Nova Forge Orchestrator — Coordinates AI agents and manages the analysis pipeline.
Connects Nova Lite (detection) → Nova Act (decision) → execution workflow.
"""

import asyncio
import logging
import uuid
from collections import deque
from datetime import datetime, timedelta

from app.models.schemas import (
    AdversarialAlert, DashboardState, Incident, IncidentStatus,
    ProcessedEvent, ResponsePlan, Severity, SystemMetrics, ThreatDetection,
)
from app.nova.nova_act import NovaActDecisionEngine
from app.nova.nova_lite import NovaLiteAnalyzer
from app.services.adversarial import AdversarialDetectionService
from app.services.data_ingestion import DataIngestionService
from app.services.processing import ProcessingPipeline

logger = logging.getLogger(__name__)


class NovaForgeOrchestrator:
    """
    Nova Forge orchestrates the full MD-ADSS pipeline:
    
    Ingestion → Processing → Nova Lite Detection → Nova Act Response → Dashboard
    
    Acts as the central coordinator for all AI agents.
    """

    def __init__(self):
        # AI Agents
        self.nova_lite = NovaLiteAnalyzer()
        self.nova_act = NovaActDecisionEngine()
        self.adversarial_detector = AdversarialDetectionService()

        # Infrastructure
        self.ingestion = DataIngestionService()
        self.pipeline = ProcessingPipeline()

        # State management
        self._incidents: dict[str, Incident] = {}
        self._threats: deque[ThreatDetection] = deque(maxlen=1000)
        self._adversarial_alerts: deque[AdversarialAlert] = deque(maxlen=100)
        self._processed_events: deque[ProcessedEvent] = deque(maxlen=5000)
        self._risk_trend: deque[dict] = deque(maxlen=60)
        self._attack_freq: deque[dict] = deque(maxlen=60)

        # Metrics
        self._total_events = 0
        self._events_this_minute = 0
        self._minute_boundary = datetime.utcnow()

        # Pipeline state
        self._running = False
        self._notification_callbacks: list = []

        logger.info("Nova Forge Orchestrator initialized — all agents ready")

    # ── Public API ────────────────────────────────────

    def add_notification_callback(self, callback):
        """Register a callback for real-time threat notifications."""
        self._notification_callbacks.append(callback)

    def set_attack_scenario(self, scenario: str | None):
        """Activate a specific attack scenario for demo purposes."""
        self.ingestion.set_attack_scenario(scenario)
        logger.info("Attack scenario set to: %s", scenario)

    def get_dashboard_state(self) -> DashboardState:
        """Return the current full dashboard state."""
        metrics = self._compute_metrics()
        active_incidents = [i for i in self._incidents.values()
                            if i.status not in (IncidentStatus.RESOLVED, IncidentStatus.MITIGATED)]

        return DashboardState(
            metrics=metrics,
            recent_incidents=sorted(active_incidents, key=lambda x: x.timestamp, reverse=True)[:20],
            adversarial_alerts=list(self._adversarial_alerts)[-20:],
            risk_trend=list(self._risk_trend),
            attack_frequency=list(self._attack_freq),
        )

    def get_recent_threats(self, limit: int = 50) -> list[ThreatDetection]:
        return list(reversed(list(self._threats)))[:limit]

    def get_incidents(self) -> list[Incident]:
        return list(self._incidents.values())

    def get_threat_stats(self) -> dict:
        threats = list(self._threats)
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for t in threats:
            by_type[t.threat_type.value] = by_type.get(t.threat_type.value, 0) + 1
            by_severity[t.severity.value] = by_severity.get(t.severity.value, 0) + 1
        return {
            "total": len(threats),
            "by_type": by_type,
            "by_severity": by_severity,
        }

    # ── Orchestration Pipeline ────────────────────────

    async def start(self, log_interval: float = 2.0, detect_interval: float = 5.0):
        """Start the full orchestration pipeline."""
        self._running = True
        logger.info("Nova Forge pipeline starting…")

        # Start parallel workers
        await asyncio.gather(
            self.ingestion.start(log_interval),
            self._detection_worker(detect_interval),
            self._metrics_worker(),
        )

    async def stop(self):
        self._running = False
        self.ingestion.stop()
        logger.info("Nova Forge pipeline stopped")

    async def _detection_worker(self, interval: float):
        """Continuously drain the ingestion queue and run threat analysis."""
        while self._running:
            batch = self._drain_queue(max_items=20)
            if batch:
                await self._process_batch(batch)
            await asyncio.sleep(interval)

    async def _metrics_worker(self):
        """Periodically update metrics snapshots for charting."""
        while self._running:
            await asyncio.sleep(10)
            self._snapshot_metrics()

    async def _process_batch(self, raw_events: list):
        """Full analysis pipeline for a batch of raw events."""
        for raw in raw_events:
            # Stage 1: Processing pipeline
            try:
                processed = self.pipeline.process(raw)
                self._processed_events.append(processed)
                self._total_events += 1
                self._events_this_minute += 1
            except Exception as e:
                logger.error("Processing failed: %s", e)
                continue

            # Stage 2: Adversarial detection (fast path)
            try:
                adv_alert = self.adversarial_detector.analyze(processed)
                if adv_alert:
                    self._adversarial_alerts.append(adv_alert)
                    await self._notify("adversarial_alert", adv_alert.model_dump(mode="json"))
            except Exception as e:
                logger.error("Adversarial detection failed: %s", e)

            # Stage 3: Nova Lite threat detection
            try:
                from app.models.schemas import LogSource
                if processed.source == LogSource.EMAIL:
                    threat = await self.nova_lite.analyze_phishing(processed)
                else:
                    threat = await self.nova_lite.analyze_event(processed)

                if threat:
                    self._threats.append(threat)
                    # Stage 4: Nova Act response generation
                    response = await self.nova_act.generate_response(threat)
                    # Stage 5: Create/update incident
                    incident = self._create_incident(threat, response)
                    await self._notify("threat_detected", {
                        "threat": threat.model_dump(mode="json"),
                        "response": response.model_dump(mode="json"),
                        "incident_id": incident.id,
                    })
            except Exception as e:
                logger.error("Threat detection pipeline failed: %s", e)

    def _drain_queue(self, max_items: int) -> list:
        """Non-blocking drain of the ingestion queue."""
        items = []
        for _ in range(max_items):
            try:
                items.append(self.ingestion.queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return items

    def _create_incident(self, threat: ThreatDetection, response: ResponsePlan) -> Incident:
        """Create a new incident or update an existing one."""
        incident_id = str(uuid.uuid4())

        timeline_entry = {
            "time": datetime.utcnow().isoformat(),
            "event": f"Threat detected: {threat.threat_type.value}",
            "severity": threat.severity.value,
        }

        incident = Incident(
            id=incident_id,
            timestamp=datetime.utcnow(),
            status=IncidentStatus.RESPONDING if response.auto_execute else IncidentStatus.DETECTED,
            threat=threat,
            response=response,
            timeline=[timeline_entry],
        )

        if response.auto_execute:
            incident.timeline.append({
                "time": datetime.utcnow().isoformat(),
                "event": f"Auto-response initiated: {', '.join(a.value for a in response.actions[:2])}",
                "severity": "info",
            })

        self._incidents[incident_id] = incident
        logger.info("Incident created: %s (%s)", incident_id, threat.threat_type.value)
        return incident

    def _compute_metrics(self) -> SystemMetrics:
        threats = list(self._threats)
        active_incidents = sum(
            1 for i in self._incidents.values()
            if i.status not in (IncidentStatus.RESOLVED, IncidentStatus.MITIGATED)
        )

        # Risk score: weighted combination of severity counts
        sev_weights = {Severity.CRITICAL: 1.0, Severity.HIGH: 0.7, Severity.MEDIUM: 0.4, Severity.LOW: 0.1}
        risk = 0.0
        if threats:
            recent = list(reversed(threats))[:20]
            risk = sum(sev_weights.get(t.severity, 0) * t.confidence for t in recent) / len(recent)
            risk = min(risk, 1.0)

        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for t in threats:
            by_type[t.threat_type.value] = by_type.get(t.threat_type.value, 0) + 1
            by_severity[t.severity.value] = by_severity.get(t.severity.value, 0) + 1

        events_per_min = self._compute_epm()

        return SystemMetrics(
            total_events_processed=self._total_events,
            threats_detected=len(threats),
            active_incidents=active_incidents,
            risk_score=round(risk, 3),
            events_per_minute=round(events_per_min, 1),
            threats_by_type=by_type,
            threats_by_severity=by_severity,
            recent_threats=list(reversed(threats))[:10],
        )

    def _snapshot_metrics(self):
        """Write a time-series snapshot for trend charts."""
        now = datetime.utcnow()
        metrics = self._compute_metrics()

        self._risk_trend.append({
            "time": now.isoformat(),
            "risk_score": metrics.risk_score,
        })
        self._attack_freq.append({
            "time": now.isoformat(),
            "count": len([t for t in self._threats if (now - t.timestamp).total_seconds() < 60]),
        })

    def _compute_epm(self) -> float:
        """Calculate events per minute."""
        now = datetime.utcnow()
        if (now - self._minute_boundary).total_seconds() >= 60:
            old = self._events_this_minute
            self._events_this_minute = 0
            self._minute_boundary = now
            return float(old)
        elapsed = (now - self._minute_boundary).total_seconds()
        if elapsed > 0:
            return (self._events_this_minute / elapsed) * 60
        return 0.0

    async def _notify(self, event_type: str, data: dict):
        """Broadcast an event to all registered notification callbacks."""
        for cb in self._notification_callbacks:
            try:
                await cb(event_type, data)
            except Exception as e:
                logger.debug("Notification callback error: %s", e)


# Singleton instance
_forge_instance: NovaForgeOrchestrator | None = None


def get_forge() -> NovaForgeOrchestrator:
    global _forge_instance
    if _forge_instance is None:
        _forge_instance = NovaForgeOrchestrator()
    return _forge_instance
