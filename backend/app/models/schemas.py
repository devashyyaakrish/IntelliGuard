from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────

class ThreatType(str, enum.Enum):
    BRUTE_FORCE = "brute_force"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    DDoS = "ddos"
    MALWARE = "malware"
    DATA_EXFILTRATION = "data_exfiltration"
    SUSPICIOUS_LOGIN = "suspicious_login"
    C2_BEACON = "c2_beacon"
    ADVERSARIAL_INPUT = "adversarial_input"
    DATA_POISONING = "data_poisoning"
    UNKNOWN = "unknown"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class LogSource(str, enum.Enum):
    NETWORK = "network"
    FIREWALL = "firewall"
    AUTH = "auth"
    EMAIL = "email"
    ENDPOINT = "endpoint"
    DNS = "dns"


class ResponseAction(str, enum.Enum):
    BLOCK_IP = "block_ip"
    ISOLATE_MACHINE = "isolate_machine"
    FORCE_PASSWORD_RESET = "force_password_reset"
    NOTIFY_ADMIN = "notify_admin"
    INCREASE_MONITORING = "increase_monitoring"
    QUARANTINE_FILE = "quarantine_file"
    DISABLE_ACCOUNT = "disable_account"
    UPDATE_FIREWALL_RULES = "update_firewall_rules"


class IncidentStatus(str, enum.Enum):
    DETECTED = "detected"
    ANALYZING = "analyzing"
    RESPONDING = "responding"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


# ── Data Models ────────────────────────────────────────

class RawLogEvent(BaseModel):
    id: str = Field(default_factory=lambda: "")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: LogSource
    source_ip: str = ""
    destination_ip: str = ""
    event_type: str = ""
    payload: dict = Field(default_factory=dict)
    raw_text: str = ""


class ProcessedEvent(BaseModel):
    id: str
    timestamp: datetime
    source: LogSource
    source_ip: str
    destination_ip: str
    event_type: str
    features: dict = Field(default_factory=dict)
    anomaly_score: float = 0.0
    raw_text: str = ""


class ThreatDetection(BaseModel):
    id: str = ""
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    threat_type: ThreatType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = ""
    source_ip: str = ""
    destination_ip: str = ""
    affected_asset: str = ""
    indicators: list[str] = Field(default_factory=list)


class ResponsePlan(BaseModel):
    id: str = ""
    threat_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actions: list[ResponseAction] = Field(default_factory=list)
    priority: int = Field(ge=1, le=5, default=3)
    reasoning: str = ""
    execution_steps: list[str] = Field(default_factory=list)
    estimated_impact: str = ""
    auto_execute: bool = False


class Incident(BaseModel):
    id: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: IncidentStatus = IncidentStatus.DETECTED
    threat: ThreatDetection
    response: Optional[ResponsePlan] = None
    timeline: list[dict] = Field(default_factory=list)


class AdversarialAlert(BaseModel):
    id: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attack_type: str = ""
    description: str = ""
    confidence: float = 0.0
    affected_model: str = ""
    indicators: list[str] = Field(default_factory=list)


class SystemMetrics(BaseModel):
    total_events_processed: int = 0
    threats_detected: int = 0
    active_incidents: int = 0
    risk_score: float = 0.0
    events_per_minute: float = 0.0
    threats_by_type: dict[str, int] = Field(default_factory=dict)
    threats_by_severity: dict[str, int] = Field(default_factory=dict)
    recent_threats: list[ThreatDetection] = Field(default_factory=list)


class DashboardState(BaseModel):
    metrics: SystemMetrics = Field(default_factory=SystemMetrics)
    recent_incidents: list[Incident] = Field(default_factory=list)
    adversarial_alerts: list[AdversarialAlert] = Field(default_factory=list)
    risk_trend: list[dict] = Field(default_factory=list)
    attack_frequency: list[dict] = Field(default_factory=list)
