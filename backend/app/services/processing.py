"""
Data Processing Pipeline — Feature extraction, normalization, and anomaly scoring.
"""

import hashlib
import math
import uuid
from datetime import datetime

from app.models.schemas import LogSource, ProcessedEvent, RawLogEvent


class ProcessingPipeline:
    """Transforms raw log events into feature-enriched processed events."""

    def __init__(self):
        self._ip_history: dict[str, list[datetime]] = {}
        self._user_history: dict[str, list[datetime]] = {}
        self._baseline_bytes: float = 1500.0
        self._baseline_rate: float = 5.0

    def process(self, event: RawLogEvent) -> ProcessedEvent:
        """Full processing pipeline: parse → extract features → normalize → score."""
        features = self._extract_features(event)
        anomaly_score = self._compute_anomaly_score(event, features)

        return ProcessedEvent(
            id=event.id or str(uuid.uuid4()),
            timestamp=event.timestamp,
            source=event.source,
            source_ip=event.source_ip,
            destination_ip=event.destination_ip,
            event_type=event.event_type,
            features=features,
            anomaly_score=anomaly_score,
            raw_text=event.raw_text,
        )

    def _extract_features(self, event: RawLogEvent) -> dict:
        """Extract domain-specific features from raw log."""
        features: dict = {
            "source_type": event.source.value,
            "event_type": event.event_type,
            "hour_of_day": event.timestamp.hour,
            "is_weekend": event.timestamp.weekday() >= 5,
        }

        payload = event.payload

        if event.source == LogSource.NETWORK:
            features.update({
                "bytes_sent": payload.get("bytes_sent", 0),
                "bytes_received": payload.get("bytes_received", 0),
                "bytes_ratio": self._safe_ratio(payload.get("bytes_sent", 0), payload.get("bytes_received", 1)),
                "port": payload.get("port", 0),
                "is_high_port": payload.get("port", 0) > 1024,
                "protocol": payload.get("protocol", ""),
                "duration_ms": payload.get("duration_ms", 0),
                "packets": payload.get("packets", 0),
                "is_c2_domain": "c2" in event.event_type or "beacon" in event.event_type,
            })

        elif event.source == LogSource.FIREWALL:
            features.update({
                "action": payload.get("action", ""),
                "is_denied": payload.get("action") == "DENY",
                "port": payload.get("port", 0),
                "is_sensitive_port": payload.get("port", 0) in {22, 3389, 445, 1433, 3306},
                "zone_src": payload.get("zone_src", ""),
            })

        elif event.source == LogSource.AUTH:
            # Track login history per IP
            self._track_ip(event.source_ip)
            rate = self._get_ip_rate(event.source_ip)
            features.update({
                "login_success": payload.get("success", False),
                "username": payload.get("username", ""),
                "is_privileged_user": payload.get("username", "") in ("admin", "root", "svc_backup"),
                "method": payload.get("method", ""),
                "is_automated_tool": "Hydra" in payload.get("user_agent", ""),
                "attempts_last_hour": payload.get("attempts_last_hour", 0),
                "ip_request_rate": rate,
                "is_off_hours": event.timestamp.hour < 6 or event.timestamp.hour > 22,
            })

        elif event.source == LogSource.EMAIL:
            features.update({
                "has_attachment": payload.get("has_attachment", False),
                "suspicious_urls": len(payload.get("suspicious_urls", [])),
                "urls_count": payload.get("urls_count", 0),
                "spf_pass": payload.get("spf_pass", True),
                "dkim_pass": payload.get("dkim_pass", True),
                "dmarc_pass": payload.get("dmarc_pass", True),
                "auth_failures": sum([
                    not payload.get("spf_pass", True),
                    not payload.get("dkim_pass", True),
                    not payload.get("dmarc_pass", True),
                ]),
                "subject_urgency": any(w in payload.get("subject", "").lower()
                                       for w in ["urgent", "immediately", "verify", "compromised", "action required"]),
                "executable_attachment": payload.get("attachment_name", "").endswith((".exe", ".bat", ".ps1", ".vbs")),
            })

        elif event.source == LogSource.ENDPOINT:
            features.update({
                "operation": payload.get("operation", ""),
                "is_encrypt": payload.get("operation") == "encrypt",
                "is_suspicious_process": payload.get("process", "") in ("cmd.exe", "powershell.exe", "wscript.exe", "svchost_update.exe"),
                "cpu_usage": payload.get("cpu_usage", 0),
                "memory_mb": payload.get("memory_mb", 0),
                "high_resource": payload.get("cpu_usage", 0) > 70,
            })

        return features

    def _compute_anomaly_score(self, event: RawLogEvent, features: dict) -> float:
        """Compute a 0–1 anomaly score based on extracted features."""
        score = 0.0

        # Event type indicators
        suspicious_types = {
            "anomalous_traffic": 0.4, "login_failure": 0.2, "firewall_deny": 0.15,
            "phishing_attempt": 0.6, "file_encrypt": 0.7, "c2_beacon": 0.8,
            "adversarial_probe": 0.9,
        }
        score += suspicious_types.get(event.event_type, 0.0)

        # Auth anomalies
        if features.get("is_automated_tool"):
            score += 0.4
        if features.get("attempts_last_hour", 0) > 50:
            score += 0.3
        if features.get("is_privileged_user") and not features.get("login_success"):
            score += 0.2
        if features.get("is_off_hours") and not features.get("login_success"):
            score += 0.1

        # Network anomalies
        if features.get("bytes_sent", 0) > 100000:
            score += 0.2
        if features.get("is_c2_domain"):
            score += 0.5

        # Email anomalies
        if features.get("auth_failures", 0) >= 2:
            score += 0.3
        if features.get("subject_urgency"):
            score += 0.15
        if features.get("executable_attachment"):
            score += 0.4

        # Endpoint anomalies
        if features.get("is_encrypt"):
            score += 0.5
        if features.get("is_suspicious_process"):
            score += 0.2
        if features.get("high_resource"):
            score += 0.1

        # Malicious IP reputation
        from app.services.data_ingestion import MALICIOUS_IPS
        if event.source_ip in MALICIOUS_IPS:
            score += 0.25

        return min(score, 1.0)

    def _track_ip(self, ip: str):
        now = datetime.utcnow()
        if ip not in self._ip_history:
            self._ip_history[ip] = []
        self._ip_history[ip].append(now)
        # Keep only last 100 entries
        self._ip_history[ip] = self._ip_history[ip][-100:]

    def _get_ip_rate(self, ip: str) -> float:
        entries = self._ip_history.get(ip, [])
        if len(entries) < 2:
            return 0.0
        span = (entries[-1] - entries[0]).total_seconds()
        if span <= 0:
            return float(len(entries))
        return len(entries) / (span / 60.0)

    @staticmethod
    def _safe_ratio(a: float, b: float) -> float:
        if b == 0:
            return 0.0
        return a / b
