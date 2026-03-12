# MD-ADSS Demo Guide
## Multi-Domain Adversarial Decision Support System
### Amazon Nova AI Hackathon

---

## Quick Start (Local, No Docker)

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add AWS creds if available
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## Quick Start (Docker)

```bash
# From repo root
cp backend/.env.example .env   # optional: add AWS creds
docker-compose up --build
```

- Dashboard → http://localhost:5173
- API Docs → http://localhost:8000/docs

---

## Demo Walkthrough (5-minute script)

### Step 0 — System loads
The platform starts with the **ALL** attack scenario active. You will immediately see:
- Events/min counter climbing in the Top Bar
- Threats populating the live feed
- Risk score rising on the gauge

---

### Step 1 — Brute Force Attack (~60 sec)
Click **BRUTE FORCE** in the top bar.

**What to show:**
- ThreatFeed entries labeled `BRUTE_FORCE` appear
- Severity badges turn **CRITICAL** (red)
- A new Incident appears in IncidentPanel with a **Nova Act** response plan
- Expand the incident → "Block source IP", "Enable MFA enforcement", step-by-step execution

**Talking points:**
> "Amazon Nova Lite classifies the authentication log burst as a credential-stuffing attack
> with 94% confidence. Nova Act autonomously generates a containment plan — blocking the
> attacker IP, disabling the compromised account, and escalating to the SOC analyst."

---

### Step 2 — Ransomware Detection (~60 sec)
Click **RANSOMWARE**.

**What to show:**
- C2 beacon entries appear in ThreatFeed
- Encryption events hit the feed (`.locked` extension activity)
- RiskTrendChart spikes
- Nova Act recommends network isolation + forensic imaging

**Talking points:**
> "Nova Lite detects the C2 communication pattern and correlates it with endpoint file-
> rename events. Nova Act triggers automated quarantine before encryption spreads laterally."

---

### Step 3 — Phishing Campaign (~60 sec)
Click **PHISHING**.

**What to show:**
- Email-source threat events
- Adversarial Alerts panel highlights **adversarial_probe** — the AI model itself is being
  tested by an adversary trying to evade detection
- AdversarialAlerts panel glows amber

**Talking points:**
> "The platform doesn't just detect phishing — it detects adversarial probing of our own
> AI models. When an attacker tries to craft emails that fool the classifier, our adversarial
> detection layer flags the distribution shift in real time."

---

### Step 4 — Attack Map
Point to the AttackMap.

**Talking points:**
> "Every threat is geolocated. We can see attack origin countries, targeting our simulated
> US headquarters. Color coding matches severity — red for critical."

---

### Step 5 — ALL scenarios + metrics
Click **ALL** and let it run for 20 seconds.

**What to show:**
- All chart panels updating simultaneously
- Incidents piling up in IncidentPanel
- Click **Resolve** on an incident to demonstrate workflow

---

## AWS Bedrock Integration

When real AWS credentials are provided, the platform switches from rule-based fallbacks
to live Amazon Nova model calls:

| Feature | Model | Notes |
|---|---|---|
| Threat classification | `amazon.nova-lite-v1:0` | Converse API, JSON output |
| Response decision | `amazon.nova-act-v1:0` | Autonomous action planning |
| Log summarization | `amazon.nova-lite-v1:0` | Plain-language SOC report |

Set credentials in `.env`:
```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

---

## API Reference (Quick)

| Endpoint | Description |
|---|---|
| `GET /api/threats` | Live threat list |
| `GET /api/incidents` | Incident management |
| `POST /api/threats/scenario/{name}` | Activate attack scenario |
| `GET /api/analytics/dashboard` | Full dashboard state |
| `WS /ws/feed` | Real-time event stream |
| `GET /docs` | Swagger UI |

---

## Architecture Summary

```
[Simulated Logs] → DataIngestionService
      ↓
[ProcessingPipeline]  feature extraction, anomaly scoring
      ↓
[NovaForgeOrchestrator]  central coordinator
   ├── NovaLiteAnalyzer     → Amazon Nova Lite (threat detect)
   ├── NovaActDecisionEngine → Amazon Nova Act  (response plan)
   └── AdversarialDetection → AI-attack-on-AI detection
      ↓
[FastAPI + WebSocket] → React Dashboard
```
