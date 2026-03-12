# MD-ADSS — Multi-Domain Adversarial Decision Support System

> AI-Powered Cybersecurity Operations Center built with Amazon Nova Models

## 🏗 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   React Dashboard (UI)                   │
│  Threat Feed │ Attack Map │ Charts │ Incident Timeline   │
└──────────────────────┬───────────────────────────────────┘
                       │  WebSocket + REST
┌──────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                          │
│  /api/threats  /api/incidents  /api/analytics  /ws/feed  │
└──────┬──────────────┬──────────────┬─────────────────────┘
       │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────────────────────┐
│ Data Ingest │ │ Processing │ │  Nova Forge Orchestrator   │
│   Layer     │ │  Pipeline  │ │                            │
│ (Simulator) │ │ (Feature   │ │  ┌───────────┐ ┌────────┐ │
│             │ │  Extraction│ │  │ Nova Lite  │ │Nova Act│ │
│ Network     │ │  Normalize)│ │  │ (Detect)   │ │(Decide)│ │
│ Firewall    │ │            │ │  └───────────┘ └────────┘ │
│ Auth Logs   │ │            │ │                            │
│ Phishing    │ │            │ │  Adversarial Detection     │
└─────────────┘ └────────────┘ └────────────────────────────┘
```

## 🔧 Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Frontend      | React 18, TailwindCSS, Framer Motion, Chart.js |
| Backend       | Python 3.11+, FastAPI, WebSockets   |
| AI Models     | Amazon Nova Lite, Nova Act, Nova Forge (via Bedrock) |
| Infra         | AWS Lambda, S3, API Gateway         |

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # configure your AWS credentials
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 for the dashboard.

## 📂 Project Structure

```
NOVA/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py           # Settings & env vars
│   │   │   └── security.py         # CORS & auth helpers
│   │   ├── nova/
│   │   │   ├── bedrock_client.py   # Bedrock SDK wrapper
│   │   │   ├── nova_lite.py        # Nova Lite threat analysis
│   │   │   ├── nova_act.py         # Nova Act decision engine
│   │   │   └── nova_forge.py       # Nova Forge orchestrator
│   │   ├── services/
│   │   │   ├── data_ingestion.py   # Log simulator & ingestion
│   │   │   ├── processing.py       # Feature extraction pipeline
│   │   │   ├── threat_detection.py # Threat classification
│   │   │   ├── adversarial.py      # Adversarial attack detection
│   │   │   └── response_engine.py  # Autonomous response
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── routes/
│   │   │   ├── threats.py          # Threat endpoints
│   │   │   ├── incidents.py        # Incident endpoints
│   │   │   ├── analytics.py        # Analytics endpoints
│   │   │   └── websocket.py        # Real-time feed
│   │   └── data/
│   │       └── sample_logs.json    # Demo dataset
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── dashboard/
│   │   │   ├── charts/
│   │   │   ├── alerts/
│   │   │   └── maps/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── docs/
    └── ARCHITECTURE.md
```

## 🎯 Demo Scenario

The platform simulates three concurrent attack scenarios:

1. **Brute Force Login Attack** — Thousands of failed login attempts from rotating IPs
2. **Ransomware Activity** — Encrypted file operations and C2 beacon traffic
3. **Phishing Campaign** — Spear-phishing emails with malicious payloads

Nova Lite detects and classifies each threat → Nova Act generates response plans → Nova Forge orchestrates the full pipeline → Dashboard visualizes everything in real-time.

## 📜 License

MIT — Built for Amazon Nova AI Hackathon
