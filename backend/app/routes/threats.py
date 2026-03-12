"""
Threat Routes — REST API endpoints for threat intelligence.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query

from app.nova.nova_forge import get_forge

router = APIRouter(prefix="/api/threats", tags=["threats"])


@router.get("")
async def get_threats(
    limit: int = Query(default=50, ge=1, le=500),
    severity: str | None = Query(default=None),
):
    """Return recent threat detections."""
    forge = get_forge()
    threats = forge.get_recent_threats(limit=limit)

    if severity:
        threats = [t for t in threats if t.severity.value == severity]

    return {
        "threats": [t.model_dump(mode="json") for t in threats],
        "total": len(threats),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/stats")
async def get_threat_stats():
    """Return threat statistics and heatmap data."""
    forge = get_forge()
    dashboard = forge.get_dashboard_state()
    return {
        "metrics": dashboard.metrics.model_dump(mode="json"),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/top-attackers")
async def get_top_attackers(limit: int = Query(default=10, ge=1, le=50)):
    """Return top attacking IP addresses."""
    from app.services.threat_detection import ThreatDetectionService
    # Build from recent threats
    forge = get_forge()
    threats = forge.get_recent_threats(limit=500)

    counts: dict[str, int] = {}
    for t in threats:
        if t.source_ip:
            counts[t.source_ip] = counts.get(t.source_ip, 0) + 1

    top = sorted(counts.items(), key=lambda x: -x[1])[:limit]
    return {"top_attackers": [{"ip": ip, "count": cnt} for ip, cnt in top]}


@router.post("/scenario/{scenario}")
async def set_scenario(scenario: str):
    """Activate a specific attack scenario (brute_force, ransomware, phishing, all, none)."""
    valid = {"brute_force", "ransomware", "phishing", "all", "none"}
    if scenario not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid scenario. Choose from: {valid}")

    forge = get_forge()
    forge.set_attack_scenario(None if scenario == "none" else scenario)
    return {"status": "ok", "scenario": scenario, "message": f"Scenario '{scenario}' activated"}
