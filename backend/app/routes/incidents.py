"""
Incident Routes — REST API endpoints for incident management.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.nova.nova_forge import get_forge
from app.services.response_engine import ResponseEngine

router = APIRouter(prefix="/api/incidents", tags=["incidents"])
_response_engine = ResponseEngine()


@router.get("")
async def get_incidents(
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return current incidents."""
    forge = get_forge()
    incidents = forge.get_incidents()

    if status:
        incidents = [i for i in incidents if i.status.value == status]

    incidents = sorted(incidents, key=lambda x: x.timestamp, reverse=True)[:limit]
    return {
        "incidents": [i.model_dump(mode="json") for i in incidents],
        "total": len(incidents),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    """Get a specific incident by ID."""
    forge = get_forge()
    incidents = {i.id: i for i in forge.get_incidents()}
    incident = incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.model_dump(mode="json")


@router.post("/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    """Manually resolve an incident."""
    from app.models.schemas import IncidentStatus
    forge = get_forge()
    incidents = {i.id: i for i in forge.get_incidents()}
    incident = incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = IncidentStatus.RESOLVED
    incident.timeline.append({
        "time": datetime.utcnow().isoformat(),
        "event": "Incident manually resolved",
        "severity": "info",
    })
    return {"status": "resolved", "incident_id": incident_id}


@router.get("/export/report")
async def export_incident_report():
    """Export a summary incident report for the current session."""
    forge = get_forge()
    incidents = forge.get_incidents()
    threats = forge.get_recent_threats(limit=100)

    report = {
        "report_generated": datetime.utcnow().isoformat(),
        "system": "MD-ADSS — Multi-Domain Adversarial Decision Support System",
        "summary": {
            "total_incidents": len(incidents),
            "total_threats": len(threats),
            "critical": sum(1 for t in threats if t.severity.value == "critical"),
            "high": sum(1 for t in threats if t.severity.value == "high"),
        },
        "incidents": [i.model_dump(mode="json") for i in incidents[:50]],
        "top_threats": [t.model_dump(mode="json") for t in threats[:20]],
    }
    return report
