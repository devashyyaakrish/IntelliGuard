# MD-ADSS System Architecture

## AI Model Workflow

```
                    ┌─────────────────────────┐
                    │    NOVA FORGE            │
                    │    (Orchestrator)        │
                    │                          │
                    │  Coordinates all AI      │
                    │  agents and pipelines    │
                    └────┬──────────┬──────────┘
                         │          │
              ┌──────────▼──┐  ┌───▼───────────┐
              │  NOVA LITE   │  │   NOVA ACT     │
              │  (Analyst)   │  │   (Commander)  │
              │              │  │                │
              │ • Classify   │  │ • Decide       │
              │ • Detect     │  │ • Plan         │
              │ • Summarize  │  │ • Execute      │
              │ • Score      │  │ • Coordinate   │
              └──────────────┘  └────────────────┘
```

## Pipeline Flow

1. **Ingestion** — Simulated logs arrive continuously
2. **Processing** — Logs are parsed, features extracted, normalized
3. **Detection** — Nova Lite classifies threats, scores severity
4. **Adversarial Check** — Monitor for AI-targeted attacks
5. **Decision** — Nova Act generates response strategies
6. **Orchestration** — Nova Forge manages agent coordination
7. **Visualization** — Dashboard receives real-time updates via WebSocket

## Data Flow Diagram

```
[Network Logs] ──┐
[Firewall Logs] ──┼──► [Ingestion] ──► [Processing] ──► [Nova Lite]
[Auth Logs] ──────┤                                         │
[Email Samples] ──┘                                    [Threat Intel]
                                                            │
                                                     [Nova Act] ──► [Response Plan]
                                                            │
                                                     [Nova Forge] ──► [Execute]
                                                            │
                                                     [Dashboard] ◄───[WebSocket]
```

## Nova Model Integration Details

### Nova Lite (amazon.nova-lite-v1:0)
- **Input**: Structured log data with feature vectors
- **Output**: Threat classification, severity, confidence, explanation
- **Use Cases**: Log analysis, phishing detection, anomaly scoring

### Nova Act
- **Input**: Threat intelligence from Nova Lite
- **Output**: Response action plan with prioritized steps
- **Use Cases**: Incident response automation, decision support

### Nova Forge
- **Input**: Pipeline state and agent status
- **Output**: Orchestrated workflow execution
- **Use Cases**: Multi-agent coordination, pipeline management
