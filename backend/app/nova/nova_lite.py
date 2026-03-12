"""
Nova Lite Integration — Threat analysis, classification, and anomaly detection
using Amazon Nova Lite model through Bedrock.
"""

import json
import logging
import uuid
from datetime import datetime

from app.models.schemas import (
    ProcessedEvent, Severity, ThreatDetection, ThreatType,
)
from app.nova.bedrock_client import get_bedrock_client

logger = logging.getLogger(__name__)

# ── System Prompts ─────────────────────────────────────

THREAT_ANALYSIS_SYSTEM_PROMPT = """You are Nova Lite, an advanced AI cybersecurity analyst operating within the MD-ADSS 
(Multi-Domain Adversarial Decision Support System). Your role is to analyze cybersecurity events 
and classify threats with high accuracy.

You MUST respond ONLY with valid JSON in the following format:
{
    "threat_type": "brute_force|ransomware|phishing|ddos|malware|data_exfiltration|suspicious_login|c2_beacon|adversarial_input|data_poisoning|unknown",
    "severity": "critical|high|medium|low|info",
    "confidence": 0.0 to 1.0,
    "explanation": "Brief technical explanation of the detection",
    "indicators": ["indicator1", "indicator2"],
    "affected_asset": "hostname or IP"
}

Be precise and technical. Base your analysis on the event data provided."""

PHISHING_ANALYSIS_PROMPT = """You are Nova Lite, specialized in email security analysis.
Analyze the email event and determine if it's a phishing attempt.

Respond ONLY with valid JSON:
{
    "is_phishing": true|false,
    "threat_type": "phishing|unknown",
    "severity": "critical|high|medium|low|info",
    "confidence": 0.0 to 1.0,
    "explanation": "Technical analysis of phishing indicators",
    "indicators": ["indicator1", "indicator2"]
}"""

LOG_SUMMARY_PROMPT = """You are Nova Lite, a cybersecurity log analysis AI.
Summarize the provided batch of security logs, highlighting:
- Key patterns and anomalies
- Potential threats
- Recommended areas of focus

Respond in JSON:
{
    "summary": "Brief summary",
    "patterns": ["pattern1", "pattern2"],
    "anomalies": ["anomaly1"],
    "risk_level": "critical|high|medium|low",
    "recommendations": ["rec1", "rec2"]
}"""


class NovaLiteAnalyzer:
    """Uses Amazon Nova Lite for cybersecurity threat detection and analysis."""

    def __init__(self):
        self._use_bedrock = True

    async def analyze_event(self, event: ProcessedEvent) -> ThreatDetection | None:
        """Analyze a processed event and return threat detection if suspicious."""
        # Quick filter — only analyze events above anomaly threshold
        if event.anomaly_score < 0.25:
            return None

        try:
            prompt = self._build_analysis_prompt(event)
            result = await self._invoke_analysis(prompt, THREAT_ANALYSIS_SYSTEM_PROMPT)

            if result:
                return ThreatDetection(
                    id=str(uuid.uuid4()),
                    event_id=event.id,
                    timestamp=datetime.utcnow(),
                    threat_type=self._parse_threat_type(result.get("threat_type", "unknown")),
                    severity=self._parse_severity(result.get("severity", "medium")),
                    confidence=min(max(float(result.get("confidence", 0.5)), 0.0), 1.0),
                    explanation=result.get("explanation", ""),
                    source_ip=event.source_ip,
                    destination_ip=event.destination_ip,
                    affected_asset=result.get("affected_asset", ""),
                    indicators=result.get("indicators", []),
                )
        except Exception as e:
            logger.error("Nova Lite analysis failed: %s", e)

        # Fallback to rule-based detection
        return self._rule_based_detection(event)

    async def analyze_phishing(self, event: ProcessedEvent) -> ThreatDetection | None:
        """Specialized phishing email analysis."""
        try:
            prompt = self._build_phishing_prompt(event)
            result = await self._invoke_analysis(prompt, PHISHING_ANALYSIS_PROMPT)

            if result and result.get("is_phishing"):
                return ThreatDetection(
                    id=str(uuid.uuid4()),
                    event_id=event.id,
                    timestamp=datetime.utcnow(),
                    threat_type=ThreatType.PHISHING,
                    severity=self._parse_severity(result.get("severity", "high")),
                    confidence=float(result.get("confidence", 0.8)),
                    explanation=result.get("explanation", "Phishing attempt detected"),
                    source_ip=event.source_ip,
                    indicators=result.get("indicators", []),
                )
        except Exception as e:
            logger.error("Phishing analysis failed: %s", e)

        return self._rule_based_phishing(event)

    async def summarize_logs(self, events: list[ProcessedEvent]) -> dict:
        """Summarize a batch of log events using Nova Lite."""
        if not events:
            return {"summary": "No events to analyze", "risk_level": "low"}

        log_text = "\n".join([
            f"[{e.timestamp.isoformat()}] {e.source.value} | {e.event_type} | "
            f"src={e.source_ip} | anomaly={e.anomaly_score:.2f} | {e.raw_text}"
            for e in events[:50]  # Limit to 50 for context window
        ])

        prompt = f"Analyze and summarize these {len(events)} security log events:\n\n{log_text}"

        try:
            result = await self._invoke_analysis(prompt, LOG_SUMMARY_PROMPT)
            return result or {"summary": "Analysis unavailable", "risk_level": "medium"}
        except Exception as e:
            logger.error("Log summarization failed: %s", e)
            return {"summary": f"Processed {len(events)} events", "risk_level": "medium"}

    async def _invoke_analysis(self, prompt: str, system_prompt: str) -> dict | None:
        """Invoke Nova Lite and parse JSON response."""
        try:
            client = get_bedrock_client()
            response_text = await client.invoke_nova_lite(prompt, system_prompt)
            # Parse JSON from response
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.warning("Bedrock invocation failed, using fallback: %s", e)
            return None

    def _build_analysis_prompt(self, event: ProcessedEvent) -> str:
        return f"""Analyze this cybersecurity event for threats:

Event ID: {event.id}
Timestamp: {event.timestamp.isoformat()}
Source: {event.source.value}
Event Type: {event.event_type}
Source IP: {event.source_ip}
Destination IP: {event.destination_ip}
Anomaly Score: {event.anomaly_score:.3f}

Features:
{json.dumps(event.features, indent=2, default=str)}

Raw Log: {event.raw_text}

Classify this event. Is it a threat? If so, what type and severity?"""

    def _build_phishing_prompt(self, event: ProcessedEvent) -> str:
        return f"""Analyze this email event for phishing indicators:

Event ID: {event.id}
Source IP: {event.source_ip}
Event Type: {event.event_type}

Email Details:
{json.dumps(event.features, indent=2, default=str)}

Raw Log: {event.raw_text}

Determine if this is a phishing attempt. Analyze email authentication, URL patterns, and content indicators."""

    def _rule_based_detection(self, event: ProcessedEvent) -> ThreatDetection | None:
        """Fallback rule-based detection when Nova Lite is unavailable."""
        features = event.features
        threat_type = ThreatType.UNKNOWN
        severity = Severity.LOW
        confidence = 0.5
        explanation = ""
        indicators: list[str] = []

        if event.event_type == "login_failure" and features.get("is_automated_tool"):
            threat_type = ThreatType.BRUTE_FORCE
            severity = Severity.HIGH
            confidence = 0.9
            explanation = f"Automated brute-force attack detected from {event.source_ip} using Hydra"
            indicators = ["automated_tool:Hydra", f"src_ip:{event.source_ip}", f"target_user:{features.get('username')}"]

        elif event.event_type == "file_encrypt":
            threat_type = ThreatType.RANSOMWARE
            severity = Severity.CRITICAL
            confidence = 0.95
            explanation = f"Ransomware file encryption detected on {features.get('hostname', 'unknown host')}"
            indicators = ["file_encryption", f"process:{features.get('process', '')}", "high_cpu_usage"]

        elif event.event_type == "c2_beacon":
            threat_type = ThreatType.C2_BEACON
            severity = Severity.CRITICAL
            confidence = 0.85
            explanation = f"Command & Control beacon traffic detected from {event.source_ip}"
            indicators = ["c2_communication", f"dst:{event.destination_ip}", "periodic_beacon"]

        elif event.event_type == "adversarial_probe":
            threat_type = ThreatType.ADVERSARIAL_INPUT
            severity = Severity.HIGH
            confidence = 0.75
            explanation = "Adversarial probe targeting AI threat classifier detected"
            indicators = ["adversarial_input", "distribution_shift", "crafted_payload"]

        elif event.event_type == "anomalous_traffic":
            threat_type = ThreatType.DATA_EXFILTRATION
            severity = Severity.MEDIUM
            confidence = 0.6
            explanation = f"Anomalous traffic pattern from {event.source_ip} — large data transfer"
            indicators = [f"bytes:{features.get('bytes_sent', 0)}", f"src_ip:{event.source_ip}"]

        elif event.event_type == "login_failure" and features.get("attempts_last_hour", 0) > 30:
            threat_type = ThreatType.SUSPICIOUS_LOGIN
            severity = Severity.MEDIUM
            confidence = 0.7
            explanation = f"Suspicious login activity — {features.get('attempts_last_hour')} failures in last hour"
            indicators = [f"user:{features.get('username')}", f"attempts:{features.get('attempts_last_hour')}"]

        else:
            if event.anomaly_score < 0.4:
                return None
            explanation = f"Anomalous event detected (score: {event.anomaly_score:.2f})"
            indicators = [f"anomaly_score:{event.anomaly_score:.2f}"]

        return ThreatDetection(
            id=str(uuid.uuid4()),
            event_id=event.id,
            timestamp=datetime.utcnow(),
            threat_type=threat_type,
            severity=severity,
            confidence=confidence,
            explanation=explanation,
            source_ip=event.source_ip,
            destination_ip=event.destination_ip,
            indicators=indicators,
        )

    def _rule_based_phishing(self, event: ProcessedEvent) -> ThreatDetection | None:
        """Fallback phishing detection."""
        features = event.features
        if features.get("auth_failures", 0) >= 2 or features.get("executable_attachment") or features.get("subject_urgency"):
            return ThreatDetection(
                id=str(uuid.uuid4()),
                event_id=event.id,
                timestamp=datetime.utcnow(),
                threat_type=ThreatType.PHISHING,
                severity=Severity.HIGH,
                confidence=0.8,
                explanation="Phishing indicators: failed email authentication, suspicious content",
                source_ip=event.source_ip,
                indicators=[
                    f"auth_failures:{features.get('auth_failures', 0)}",
                    f"suspicious_urls:{features.get('suspicious_urls', 0)}",
                    f"executable_attachment:{features.get('executable_attachment', False)}",
                ],
            )
        return None

    @staticmethod
    def _parse_json_response(text: str) -> dict | None:
        """Extract JSON from model response text."""
        if not text:
            return None
        text = text.strip()
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try to find JSON block
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return None

    @staticmethod
    def _parse_threat_type(value: str) -> ThreatType:
        try:
            return ThreatType(value)
        except ValueError:
            return ThreatType.UNKNOWN

    @staticmethod
    def _parse_severity(value: str) -> Severity:
        try:
            return Severity(value)
        except ValueError:
            return Severity.MEDIUM
