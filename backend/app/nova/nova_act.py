"""
Nova Act Integration — Autonomous decision-making and response strategy generation
using Amazon Nova Act model through Bedrock.
"""

import json
import logging
import uuid
from datetime import datetime

from app.models.schemas import (
    ResponseAction, ResponsePlan, Severity, ThreatDetection, ThreatType,
)
from app.nova.bedrock_client import get_bedrock_client

logger = logging.getLogger(__name__)

# ── System Prompts ─────────────────────────────────────

RESPONSE_DECISION_SYSTEM_PROMPT = """You are Nova Act, an autonomous cybersecurity response commander within the MD-ADSS 
(Multi-Domain Adversarial Decision Support System). Your role is to analyze incoming threat intelligence 
and generate optimal response strategies.

You make decisions based on threat severity, confidence, potential impact, and available response actions.

Available response actions:
- block_ip: Block the malicious source IP at firewall
- isolate_machine: Isolate the compromised endpoint from network
- force_password_reset: Force credential reset for affected accounts
- notify_admin: Alert security administrators
- increase_monitoring: Enhance monitoring for affected assets
- quarantine_file: Quarantine suspicious files
- disable_account: Disable compromised user accounts
- update_firewall_rules: Update firewall rules to prevent further attacks

You MUST respond ONLY with valid JSON:
{
    "actions": ["action1", "action2"],
    "priority": 1-5 (1=highest),
    "reasoning": "Detailed reasoning for the response strategy",
    "execution_steps": ["step1", "step2", "step3"],
    "estimated_impact": "Brief impact assessment",
    "auto_execute": true|false
}

Be decisive and prioritize containment. Critical threats should have auto_execute=true."""

ACTION_PLAN_PROMPT = """You are Nova Act, coordinating active incident response.
Given the current threat landscape and active incidents, generate a prioritized action plan.

Respond ONLY in JSON:
{
    "plan_name": "Name of the response plan",
    "priority_actions": ["action1", "action2"],
    "coordination_notes": "Notes for the SOC team",
    "escalation_required": true|false,
    "estimated_containment_time": "e.g. 15 minutes"
}"""


class NovaActDecisionEngine:
    """Uses Amazon Nova Act for autonomous cybersecurity response decisions."""

    def __init__(self):
        self._response_history: list[ResponsePlan] = []

    async def generate_response(self, threat: ThreatDetection) -> ResponsePlan:
        """Generate an autonomous response plan for a detected threat."""
        try:
            prompt = self._build_decision_prompt(threat)
            result = await self._invoke_decision(prompt, RESPONSE_DECISION_SYSTEM_PROMPT)

            if result:
                plan = ResponsePlan(
                    id=str(uuid.uuid4()),
                    threat_id=threat.id,
                    timestamp=datetime.utcnow(),
                    actions=self._parse_actions(result.get("actions", [])),
                    priority=min(max(int(result.get("priority", 3)), 1), 5),
                    reasoning=result.get("reasoning", ""),
                    execution_steps=result.get("execution_steps", []),
                    estimated_impact=result.get("estimated_impact", ""),
                    auto_execute=result.get("auto_execute", False),
                )
                self._response_history.append(plan)
                return plan
        except Exception as e:
            logger.error("Nova Act decision failed: %s", e)

        # Fallback to rule-based response
        return self._rule_based_response(threat)

    async def generate_action_plan(self, threats: list[ThreatDetection]) -> dict:
        """Generate a coordinated action plan for multiple active threats."""
        if not threats:
            return {"plan_name": "No active threats", "priority_actions": []}

        threat_summary = "\n".join([
            f"- [{t.severity.value.upper()}] {t.threat_type.value}: {t.explanation} "
            f"(confidence: {t.confidence:.0%}, src: {t.source_ip})"
            for t in threats[:10]
        ])

        prompt = f"""Current active threats ({len(threats)} total):

{threat_summary}

Previous response actions taken: {len(self._response_history)}

Generate a coordinated action plan to address these threats."""

        try:
            result = await self._invoke_decision(prompt, ACTION_PLAN_PROMPT)
            return result or {"plan_name": "Manual review required", "priority_actions": ["notify_admin"]}
        except Exception as e:
            logger.error("Action plan generation failed: %s", e)
            return {"plan_name": "Fallback plan", "priority_actions": ["notify_admin", "increase_monitoring"]}

    async def _invoke_decision(self, prompt: str, system_prompt: str) -> dict | None:
        """
        Invoke the Bedrock Agent (Nova Act / Nova Forge) for autonomous decisions.
        Falls back to Nova 2 Lite via Converse when NOVA_AGENT_ID is not set.
        """
        try:
            client = get_bedrock_client()
            # Combine system prompt + user prompt so the agent gets full context
            full_prompt = f"{system_prompt}\n\n---\n{prompt}"
            response_text = await client.invoke_nova_agent(full_prompt)
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.warning("Nova Act / Agent invocation failed, using fallback: %s", e)
            return None

    def _build_decision_prompt(self, threat: ThreatDetection) -> str:
        return f"""Analyze this threat and determine the optimal response strategy:

Threat ID: {threat.id}
Type: {threat.threat_type.value}
Severity: {threat.severity.value}
Confidence: {threat.confidence:.0%}
Source IP: {threat.source_ip}
Destination IP: {threat.destination_ip}
Affected Asset: {threat.affected_asset}
Explanation: {threat.explanation}
Indicators: {', '.join(threat.indicators)}

Recent response history: {len(self._response_history)} actions taken

What response actions should be taken? Consider proportionality and urgency."""

    def _rule_based_response(self, threat: ThreatDetection) -> ResponsePlan:
        """Deterministic fallback response based on threat characteristics."""
        actions: list[ResponseAction] = []
        steps: list[str] = []
        priority = 3
        reasoning = ""
        auto_execute = False

        if threat.threat_type == ThreatType.BRUTE_FORCE:
            actions = [ResponseAction.BLOCK_IP, ResponseAction.FORCE_PASSWORD_RESET, ResponseAction.NOTIFY_ADMIN]
            priority = 2
            reasoning = (
                f"Brute-force attack from {threat.source_ip}. Blocking IP, resetting targeted credentials, "
                "and alerting SOC team."
            )
            steps = [
                f"1. Block source IP {threat.source_ip} at perimeter firewall",
                "2. Force password reset for targeted accounts",
                "3. Review authentication logs for successful compromises",
                "4. Update brute-force detection thresholds",
                "5. Notify security administrator",
            ]
            auto_execute = threat.severity in (Severity.CRITICAL, Severity.HIGH)

        elif threat.threat_type == ThreatType.RANSOMWARE:
            actions = [
                ResponseAction.ISOLATE_MACHINE, ResponseAction.BLOCK_IP,
                ResponseAction.QUARANTINE_FILE, ResponseAction.NOTIFY_ADMIN,
            ]
            priority = 1
            reasoning = (
                f"Ransomware activity detected. Immediate isolation required to prevent lateral spread. "
                f"C2 communication to {threat.destination_ip} must be blocked."
            )
            steps = [
                "1. IMMEDIATE: Isolate affected endpoint from network",
                f"2. Block C2 IP {threat.destination_ip} at all firewalls",
                "3. Quarantine encrypted/suspicious files for analysis",
                "4. Scan adjacent network segments for lateral movement",
                "5. Activate backup verification procedures",
                "6. Escalate to incident response team",
            ]
            auto_execute = True

        elif threat.threat_type == ThreatType.PHISHING:
            actions = [ResponseAction.QUARANTINE_FILE, ResponseAction.NOTIFY_ADMIN, ResponseAction.INCREASE_MONITORING]
            priority = 2
            reasoning = "Phishing campaign detected. Quarantining attachments and alerting affected users."
            steps = [
                "1. Quarantine email and attachments across all mailboxes",
                "2. Block sender domain at email gateway",
                "3. Notify affected recipients",
                "4. Check if any users clicked links or opened attachments",
                "5. If credentials compromised, force password reset",
            ]
            auto_execute = threat.confidence > 0.85

        elif threat.threat_type == ThreatType.C2_BEACON:
            actions = [ResponseAction.ISOLATE_MACHINE, ResponseAction.BLOCK_IP, ResponseAction.NOTIFY_ADMIN]
            priority = 1
            reasoning = f"C2 beacon communication detected from internal host to {threat.destination_ip}."
            steps = [
                "1. Isolate beaconing host immediately",
                f"2. Block C2 destination {threat.destination_ip}",
                "3. Forensic analysis of affected endpoint",
                "4. Check for data exfiltration indicators",
                "5. Hunt for additional compromised hosts",
            ]
            auto_execute = True

        elif threat.threat_type == ThreatType.ADVERSARIAL_INPUT:
            actions = [ResponseAction.INCREASE_MONITORING, ResponseAction.NOTIFY_ADMIN, ResponseAction.BLOCK_IP]
            priority = 2
            reasoning = "Adversarial attack targeting AI models detected. Increasing model monitoring."
            steps = [
                "1. Enable enhanced input validation on AI models",
                "2. Activate model output monitoring",
                f"3. Block suspicious source {threat.source_ip}",
                "4. Review recent model predictions for anomalies",
                "5. Consider temporary model fallback to rule-based system",
            ]
            auto_execute = False

        elif threat.threat_type == ThreatType.DATA_EXFILTRATION:
            actions = [ResponseAction.BLOCK_IP, ResponseAction.ISOLATE_MACHINE, ResponseAction.NOTIFY_ADMIN]
            priority = 1
            reasoning = f"Potential data exfiltration detected — large data transfer to {threat.destination_ip}."
            steps = [
                f"1. Block outbound connection to {threat.destination_ip}",
                "2. Isolate source endpoint",
                "3. Inventory potentially exposed data",
                "4. Check DLP logs for data classification",
                "5. Prepare breach notification if PII involved",
            ]
            auto_execute = True

        else:
            actions = [ResponseAction.INCREASE_MONITORING, ResponseAction.NOTIFY_ADMIN]
            priority = 3
            reasoning = f"Unclassified threat detected ({threat.threat_type.value}). Increased monitoring."
            steps = [
                "1. Increase monitoring on affected assets",
                "2. Notify security team for manual review",
                "3. Gather additional context from adjacent logs",
            ]

        impact = {
            1: "CRITICAL — Immediate containment required to prevent significant damage",
            2: "HIGH — Rapid response needed to limit potential impact",
            3: "MEDIUM — Timely response recommended",
            4: "LOW — Standard monitoring procedures",
            5: "INFORMATIONAL — No immediate action required",
        }.get(priority, "Unknown impact level")

        plan = ResponsePlan(
            id=str(uuid.uuid4()),
            threat_id=threat.id,
            timestamp=datetime.utcnow(),
            actions=actions,
            priority=priority,
            reasoning=reasoning,
            execution_steps=steps,
            estimated_impact=impact,
            auto_execute=auto_execute,
        )
        self._response_history.append(plan)
        return plan

    @staticmethod
    def _parse_actions(action_strs: list[str]) -> list[ResponseAction]:
        actions = []
        for a in action_strs:
            try:
                actions.append(ResponseAction(a))
            except ValueError:
                continue
        return actions or [ResponseAction.NOTIFY_ADMIN]

    @staticmethod
    def _parse_json_response(text: str) -> dict | None:
        if not text:
            return None
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return None
