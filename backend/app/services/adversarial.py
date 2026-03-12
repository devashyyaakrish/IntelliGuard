"""
Adversarial Detection Module — Detects attacks targeting the AI models themselves.
Monitors for data poisoning, adversarial inputs, model evasion, and distribution shifts.
"""

import logging
import uuid
from datetime import datetime
from statistics import mean, stdev

from app.models.schemas import AdversarialAlert, ProcessedEvent

logger = logging.getLogger(__name__)


class AdversarialDetectionService:
    """Monitors for adversarial attacks against the AI systems in MD-ADSS."""

    def __init__(self):
        self._anomaly_score_history: list[float] = []
        self._feature_distribution: dict[str, list[float]] = {}
        self._alert_count = 0

    def analyze(self, event: ProcessedEvent) -> AdversarialAlert | None:
        """Check if an event represents an adversarial attack on AI models."""
        self._update_history(event)

        checks = [
            self._detect_distribution_shift(event),
            self._detect_adversarial_probe(event),
            self._detect_data_poisoning(event),
            self._detect_model_evasion(event),
        ]

        # Return the most confident alert found
        alerts = [a for a in checks if a is not None]
        if alerts:
            alerts.sort(key=lambda x: x.confidence, reverse=True)
            self._alert_count += 1
            logger.warning("Adversarial alert: %s (confidence=%.2f)",
                           alerts[0].attack_type, alerts[0].confidence)
            return alerts[0]
        return None

    def _detect_distribution_shift(self, event: ProcessedEvent) -> AdversarialAlert | None:
        """Detect unusual feature distribution that could indicate data poisoning."""
        if len(self._anomaly_score_history) < 20:
            return None

        recent_mean = mean(self._anomaly_score_history[-20:])
        historical_mean = mean(self._anomaly_score_history[:-20]) if len(self._anomaly_score_history) > 20 else recent_mean

        shift = abs(recent_mean - historical_mean)
        if shift > 0.35 and recent_mean > 0.7:
            return AdversarialAlert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                attack_type="distribution_shift",
                description=(
                    f"Significant distribution shift detected in anomaly scores. "
                    f"Recent mean: {recent_mean:.3f} vs historical: {historical_mean:.3f} "
                    f"(shift: {shift:.3f}). Possible data poisoning attack."
                ),
                confidence=min(shift * 1.5, 0.95),
                affected_model="nova_lite_threat_classifier",
                indicators=[
                    f"recent_mean:{recent_mean:.3f}",
                    f"historical_mean:{historical_mean:.3f}",
                    f"shift:{shift:.3f}",
                ],
            )
        return None

    def _detect_adversarial_probe(self, event: ProcessedEvent) -> AdversarialAlert | None:
        """Detect crafted inputs designed to evade the AI classifier."""
        if event.event_type != "adversarial_probe":
            return None

        payload = event.features
        distribution_shift = payload.get("distribution_shift", 0)
        entropy = payload.get("entropy_anomaly", 0)

        confidence = min((distribution_shift + (entropy / 10)) / 2, 0.97)

        return AdversarialAlert(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            attack_type="adversarial_input",
            description=(
                f"Adversarial probe detected from {event.source_ip}. "
                f"Crafted inputs targeting threat classifier with distribution shift {distribution_shift:.2f}."
            ),
            confidence=confidence,
            affected_model="nova_lite_threat_classifier",
            indicators=[
                f"crafted_input:true",
                f"distribution_shift:{distribution_shift:.2f}",
                f"entropy_anomaly:{entropy:.2f}",
                f"src:{event.source_ip}",
            ],
        )

    def _detect_data_poisoning(self, event: ProcessedEvent) -> AdversarialAlert | None:
        """Detect systematic attempts to corrupt the training/inference pipeline."""
        features = event.features

        # Detect unusually repeated identical patterns
        repeated = features.get("repeated_patterns", 0)
        if repeated > 100:
            confidence = min(0.5 + (repeated / 400), 0.92)
            return AdversarialAlert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                attack_type="data_poisoning",
                description=(
                    f"Possible data poisoning attempt: {repeated} repeated pattern injections detected. "
                    "Attacker may be attempting to corrupt model's feature baseline."
                ),
                confidence=confidence,
                affected_model="processing_pipeline",
                indicators=[
                    f"repeated_patterns:{repeated}",
                    f"src:{event.source_ip}",
                    "systematic_injection",
                ],
            )
        return None

    def _detect_model_evasion(self, event: ProcessedEvent) -> AdversarialAlert | None:
        """Detect attempts to craft inputs that appear benign but are malicious."""
        features = event.features

        # High bytes transfer but low anomaly score (evasion signature)
        bytes_sent = features.get("bytes_sent", 0)
        is_malicious_ip = event.source_ip in _get_malicious_ips()

        if bytes_sent > 80000 and event.anomaly_score < 0.3 and is_malicious_ip:
            return AdversarialAlert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                attack_type="model_evasion",
                description=(
                    f"Model evasion attempt: High-volume traffic from known malicious IP {event.source_ip} "
                    f"scoring unexpectedly low anomaly score ({event.anomaly_score:.2f}). "
                    "Crafted to bypass AI detection."
                ),
                confidence=0.72,
                affected_model="nova_lite_threat_classifier",
                indicators=[
                    f"src:{event.source_ip}",
                    f"bytes:{bytes_sent}",
                    f"anomaly_score:{event.anomaly_score:.2f}",
                    "evasion_signature",
                ],
            )
        return None

    def _update_history(self, event: ProcessedEvent):
        """Maintain rolling statistics for anomaly score distribution."""
        self._anomaly_score_history.append(event.anomaly_score)
        if len(self._anomaly_score_history) > 500:
            self._anomaly_score_history = self._anomaly_score_history[-500:]


def _get_malicious_ips() -> list[str]:
    """Return the known malicious IP list."""
    from app.services.data_ingestion import MALICIOUS_IPS
    return MALICIOUS_IPS
