"""
Data Ingestion Layer — Simulates cybersecurity log streams from multiple domains.
Generates realistic network, firewall, auth, email, and endpoint events.
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta

from app.models.schemas import LogSource, RawLogEvent


# ── Realistic data pools ──────────────────────────────

INTERNAL_IPS = [
    "10.0.1.15", "10.0.1.22", "10.0.1.45", "10.0.2.10", "10.0.2.33",
    "10.0.3.8", "10.0.3.50", "192.168.1.100", "192.168.1.101", "192.168.1.200",
]

EXTERNAL_IPS = [
    "203.0.113.50", "198.51.100.23", "185.220.101.1", "45.33.32.156",
    "91.219.237.229", "104.248.50.87", "159.89.174.89", "138.197.148.152",
]

MALICIOUS_IPS = [
    "185.220.101.1", "91.219.237.229", "45.154.98.12", "194.26.29.111",
    "77.247.181.163", "162.247.74.7", "23.129.64.100", "51.15.43.205",
]

USERS = [
    "admin", "jdoe", "asmith", "mchen", "kpatel", "root", "svc_backup",
    "finance_bot", "hr_system", "devops_user", "guest", "test_user",
]

HOSTNAMES = [
    "WS-FINANCE-01", "WS-HR-02", "SRV-DB-01", "SRV-WEB-02", "SRV-MAIL-01",
    "WS-DEV-03", "SRV-DC-01", "WS-EXEC-01", "SRV-APP-01", "SRV-FILE-01",
]

PHISHING_SUBJECTS = [
    "Urgent: Your account has been compromised",
    "Action Required: Verify your credentials immediately",
    "Invoice #INV-2026-4851 attached",
    "Password Reset Request - Confirm Now",
    "Congratulations! You've won a $500 gift card",
    "Your package delivery failed — reschedule now",
    "IT Department: System update required",
    "Shared document: Q1 Financial Report.xlsx",
]

LEGITIMATE_SUBJECTS = [
    "Team meeting agenda for Monday",
    "Project status update",
    "Monthly report attached",
    "Lunch plans?",
    "RE: Code review feedback",
]

SUSPICIOUS_DOMAINS = [
    "amaz0n-security.com", "micros0ft-verify.net", "g00gle-auth.org",
    "paypa1-secure.com", "app1e-id-verify.com",
]

C2_DOMAINS = [
    "update.evil-cdn.xyz", "api.shadow-net.cc", "beacon.darkops.io",
]

RANSOMWARE_EXTENSIONS = [".encrypted", ".locked", ".cry", ".wnry", ".wcry"]

FILE_OPERATIONS = ["read", "write", "delete", "rename", "encrypt"]

PROTOCOLS = ["TCP", "UDP", "HTTP", "HTTPS", "DNS", "SSH", "RDP", "SMTP"]


class DataIngestionService:
    """Generates simulated cybersecurity log events from multiple domains."""

    def __init__(self):
        self._running = False
        self._event_queue: asyncio.Queue[RawLogEvent] = asyncio.Queue(maxsize=10000)
        self._attack_mode: str | None = None  # active attack scenario

    @property
    def queue(self) -> asyncio.Queue[RawLogEvent]:
        return self._event_queue

    def set_attack_scenario(self, scenario: str | None):
        """Activate a specific attack scenario: brute_force, ransomware, phishing, or None."""
        self._attack_mode = scenario

    async def start(self, interval: float = 2.0):
        """Start generating log events."""
        self._running = True
        while self._running:
            events = self._generate_batch()
            for event in events:
                try:
                    self._event_queue.put_nowait(event)
                except asyncio.QueueFull:
                    # Drop oldest events
                    try:
                        self._event_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    self._event_queue.put_nowait(event)
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False

    def _generate_batch(self) -> list[RawLogEvent]:
        """Generate a batch of mixed log events."""
        events: list[RawLogEvent] = []

        # Normal background traffic (2-5 events)
        for _ in range(random.randint(2, 5)):
            generator = random.choice([
                self._gen_network_event,
                self._gen_firewall_event,
                self._gen_auth_event,
                self._gen_endpoint_event,
            ])
            events.append(generator(malicious=False))

        # Inject attack-specific events
        if self._attack_mode == "brute_force":
            events.extend(self._gen_brute_force_burst())
        elif self._attack_mode == "ransomware":
            events.extend(self._gen_ransomware_activity())
        elif self._attack_mode == "phishing":
            events.extend(self._gen_phishing_campaign())
        elif self._attack_mode == "all":
            # Mixed attack scenario for demo
            r = random.random()
            if r < 0.35:
                events.extend(self._gen_brute_force_burst())
            elif r < 0.65:
                events.extend(self._gen_ransomware_activity())
            elif r < 0.85:
                events.extend(self._gen_phishing_campaign())
            else:
                # Occasional adversarial-style anomaly
                events.append(self._gen_adversarial_event())
        else:
            # Random chance of suspicious events even in normal mode
            if random.random() < 0.15:
                events.append(random.choice([
                    self._gen_network_event(malicious=True),
                    self._gen_auth_event(malicious=True),
                    self._gen_firewall_event(malicious=True),
                ]))

        return events

    # ── Network Events ────────────────────────────────

    def _gen_network_event(self, malicious: bool = False) -> RawLogEvent:
        src = random.choice(MALICIOUS_IPS if malicious else EXTERNAL_IPS)
        dst = random.choice(INTERNAL_IPS)
        proto = random.choice(PROTOCOLS)
        bytes_sent = random.randint(64, 5000) if not malicious else random.randint(50000, 500000)
        port = random.choice([80, 443, 8080, 22, 3389, 53, 25, 445])

        return RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.NETWORK,
            source_ip=src,
            destination_ip=dst,
            event_type="connection" if not malicious else "anomalous_traffic",
            payload={
                "protocol": proto,
                "port": port,
                "bytes_sent": bytes_sent,
                "bytes_received": random.randint(64, 2000),
                "duration_ms": random.randint(10, 30000),
                "packets": random.randint(1, 500),
                "flags": random.choice(["SYN", "ACK", "SYN-ACK", "FIN", "RST"]) if proto == "TCP" else "",
            },
            raw_text=f"{proto} {src}:{random.randint(1024, 65535)} -> {dst}:{port} bytes={bytes_sent}",
        )

    # ── Firewall Events ───────────────────────────────

    def _gen_firewall_event(self, malicious: bool = False) -> RawLogEvent:
        src = random.choice(MALICIOUS_IPS if malicious else EXTERNAL_IPS)
        dst = random.choice(INTERNAL_IPS)
        action = "DENY" if malicious or random.random() < 0.3 else "ALLOW"
        port = random.choice([22, 3389, 445, 80, 443, 8080, 1433, 3306])

        return RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.FIREWALL,
            source_ip=src,
            destination_ip=dst,
            event_type=f"firewall_{action.lower()}",
            payload={
                "action": action,
                "port": port,
                "protocol": random.choice(["TCP", "UDP"]),
                "rule_id": f"FW-{random.randint(100, 999)}",
                "zone_src": "EXTERNAL" if malicious else random.choice(["EXTERNAL", "DMZ"]),
                "zone_dst": "INTERNAL",
            },
            raw_text=f"FIREWALL {action} {src} -> {dst}:{port}",
        )

    # ── Auth Events ───────────────────────────────────

    def _gen_auth_event(self, malicious: bool = False) -> RawLogEvent:
        user = random.choice(["admin", "root", "svc_backup"] if malicious else USERS)
        src = random.choice(MALICIOUS_IPS if malicious else INTERNAL_IPS)
        success = not malicious or random.random() < 0.05  # attackers rarely succeed
        host = random.choice(HOSTNAMES)

        return RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.AUTH,
            source_ip=src,
            destination_ip="",
            event_type="login_failure" if not success else "login_success",
            payload={
                "username": user,
                "hostname": host,
                "success": success,
                "method": random.choice(["password", "ssh_key", "mfa"]),
                "user_agent": "Mozilla/5.0" if not malicious else "Hydra/9.3",
                "attempts_last_hour": random.randint(50, 500) if malicious else random.randint(0, 3),
            },
            raw_text=f"AUTH {'SUCCESS' if success else 'FAILURE'} user={user} src={src} host={host}",
        )

    # ── Email Events ──────────────────────────────────

    def _gen_email_event(self, phishing: bool = False) -> RawLogEvent:
        sender_domain = random.choice(SUSPICIOUS_DOMAINS if phishing else ["company.com", "partner.org"])
        sender = f"{random.choice(['noreply', 'admin', 'support', 'security'])}@{sender_domain}"
        recipient = f"{random.choice(USERS)}@company.com"
        subject = random.choice(PHISHING_SUBJECTS if phishing else LEGITIMATE_SUBJECTS)

        return RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.EMAIL,
            source_ip=random.choice(MALICIOUS_IPS if phishing else EXTERNAL_IPS),
            destination_ip="",
            event_type="phishing_attempt" if phishing else "email_received",
            payload={
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "has_attachment": phishing or random.random() < 0.3,
                "attachment_name": "Invoice_2026.xlsx.exe" if phishing else "Report.pdf",
                "urls_count": random.randint(2, 8) if phishing else random.randint(0, 2),
                "suspicious_urls": [f"http://{random.choice(SUSPICIOUS_DOMAINS)}/verify"] if phishing else [],
                "spf_pass": not phishing,
                "dkim_pass": not phishing,
                "dmarc_pass": not phishing,
            },
            raw_text=f"EMAIL from={sender} to={recipient} subject='{subject}'",
        )

    # ── Endpoint Events ───────────────────────────────

    def _gen_endpoint_event(self, malicious: bool = False) -> RawLogEvent:
        host = random.choice(HOSTNAMES)
        operation = random.choice(FILE_OPERATIONS)

        return RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.ENDPOINT,
            source_ip=random.choice(INTERNAL_IPS),
            destination_ip="",
            event_type=f"file_{operation}",
            payload={
                "hostname": host,
                "operation": operation,
                "file_path": ("C:\\Users\\document.docx" if not malicious else "C:\\Windows\\System32\\payload.exe"),
                "process": "explorer.exe" if not malicious else random.choice(["cmd.exe", "powershell.exe", "wscript.exe"]),
                "pid": random.randint(1000, 65535),
                "cpu_usage": random.uniform(1, 15) if not malicious else random.uniform(60, 99),
                "memory_mb": random.randint(50, 500) if not malicious else random.randint(500, 4000),
            },
            raw_text=f"ENDPOINT {host} {operation} process={('explorer.exe' if not malicious else 'powershell.exe')}",
        )

    # ── Attack Scenario Generators ────────────────────

    def _gen_brute_force_burst(self) -> list[RawLogEvent]:
        """Simulate a burst of brute-force login attempts."""
        attacker_ip = random.choice(MALICIOUS_IPS)
        target_user = random.choice(["admin", "root", "svc_backup"])
        target_host = random.choice(HOSTNAMES)
        events = []
        for i in range(random.randint(8, 20)):
            events.append(RawLogEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() + timedelta(seconds=i * 0.5),
                source=LogSource.AUTH,
                source_ip=attacker_ip,
                destination_ip="",
                event_type="login_failure",
                payload={
                    "username": target_user,
                    "hostname": target_host,
                    "success": False,
                    "method": "password",
                    "user_agent": "Hydra/9.3",
                    "attempts_last_hour": 150 + i * 10,
                },
                raw_text=f"AUTH FAILURE user={target_user} src={attacker_ip} host={target_host} tool=Hydra",
            ))
        return events

    def _gen_ransomware_activity(self) -> list[RawLogEvent]:
        """Simulate ransomware file encryption activity."""
        infected_host = random.choice(HOSTNAMES)
        infected_ip = random.choice(INTERNAL_IPS)
        events = []
        # File encryption burst
        for i in range(random.randint(5, 12)):
            ext = random.choice(RANSOMWARE_EXTENSIONS)
            events.append(RawLogEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() + timedelta(seconds=i),
                source=LogSource.ENDPOINT,
                source_ip=infected_ip,
                destination_ip="",
                event_type="file_encrypt",
                payload={
                    "hostname": infected_host,
                    "operation": "encrypt",
                    "file_path": f"C:\\Users\\Documents\\file_{i}{ext}",
                    "process": "svchost_update.exe",
                    "pid": random.randint(5000, 9000),
                    "cpu_usage": random.uniform(80, 99),
                    "memory_mb": random.randint(1000, 4000),
                    "files_encrypted_total": 50 + i * 20,
                },
                raw_text=f"ENDPOINT {infected_host} ENCRYPT file_{i}{ext} proc=svchost_update.exe CPU=95%",
            ))
        # C2 beacon traffic
        events.append(RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.NETWORK,
            source_ip=infected_ip,
            destination_ip=random.choice(MALICIOUS_IPS),
            event_type="c2_beacon",
            payload={
                "protocol": "HTTPS",
                "port": 443,
                "domain": random.choice(C2_DOMAINS),
                "bytes_sent": random.randint(100, 500),
                "bytes_received": random.randint(500, 5000),
                "interval_seconds": 60,
                "beacon_count": random.randint(10, 100),
            },
            raw_text=f"NETWORK {infected_ip} -> C2 beacon to {C2_DOMAINS[0]} interval=60s",
        ))
        return events

    def _gen_phishing_campaign(self) -> list[RawLogEvent]:
        """Simulate a phishing email campaign."""
        events = []
        sender_domain = random.choice(SUSPICIOUS_DOMAINS)
        for i in range(random.randint(3, 7)):
            events.append(self._gen_email_event(phishing=True))
        return events

    def _gen_adversarial_event(self) -> RawLogEvent:
        """Simulate an adversarial attack against the AI system itself."""
        return RawLogEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source=LogSource.NETWORK,
            source_ip=random.choice(MALICIOUS_IPS),
            destination_ip=random.choice(INTERNAL_IPS),
            event_type="adversarial_probe",
            payload={
                "type": random.choice(["data_poisoning", "model_evasion", "adversarial_input"]),
                "target_model": "nova_lite_threat_classifier",
                "crafted_input": True,
                "distribution_shift": random.uniform(0.3, 0.9),
                "entropy_anomaly": random.uniform(3.5, 8.0),
                "repeated_patterns": random.randint(50, 200),
            },
            raw_text="ADVERSARIAL PROBE detected — crafted input targeting threat classifier",
        )
