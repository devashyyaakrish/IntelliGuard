"""
Analytics Routes — Visualization data endpoints for dashboards and charts.
"""

from datetime import datetime
from fastapi import APIRouter, Query

from app.nova.nova_forge import get_forge

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard():
    """Full dashboard state snapshot."""
    forge = get_forge()
    state = forge.get_dashboard_state()
    return state.model_dump(mode="json")


@router.get("/risk-trend")
async def get_risk_trend():
    """Time-series risk score trend data."""
    forge = get_forge()
    state = forge.get_dashboard_state()
    return {"trend": state.risk_trend}


@router.get("/attack-frequency")
async def get_attack_frequency():
    """Attack frequency over time."""
    forge = get_forge()
    state = forge.get_dashboard_state()
    return {"frequency": state.attack_frequency}


@router.get("/severity-distribution")
async def get_severity_distribution():
    """Threat severity distribution."""
    forge = get_forge()
    threats = forge.get_recent_threats(limit=500)
    dist: dict[str, int] = {}
    for t in threats:
        dist[t.severity.value] = dist.get(t.severity.value, 0) + 1
    return {"distribution": dist}


@router.get("/threat-types")
async def get_threat_types():
    """Threat type breakdown for pie chart."""
    forge = get_forge()
    stats = forge.get_threat_stats()
    return {"by_type": stats.get("by_type", {}), "total": stats.get("total", 0)}


@router.get("/geo-threats")
async def get_geo_threats():
    """
    Return threats with simulated geographic coordinates for the attack map.
    Coordinates are derived deterministically from IP addresses for demo purposes.
    """
    forge = get_forge()
    threats = forge.get_recent_threats(limit=30)

    # Simulated geo data for known malicious IPs
    ip_geo = {
        "203.0.113.50": {"lat": 39.9042, "lng": 116.4074, "country": "China"},
        "198.51.100.23": {"lat": 55.7558, "lng": 37.6173, "country": "Russia"},
        "185.220.101.1": {"lat": 51.5074, "lng": -0.1278, "country": "UK (Tor)"},
        "45.33.32.156": {"lat": 37.5485, "lng": -121.9886, "country": "USA"},
        "91.219.237.229": {"lat": 48.8566, "lng": 2.3522, "country": "France"},
        "104.248.50.87": {"lat": 40.7128, "lng": -74.0060, "country": "USA"},
        "159.89.174.89": {"lat": -23.5505, "lng": -46.6333, "country": "Brazil"},
        "138.197.148.152": {"lat": 52.3676, "lng": 4.9041, "country": "Netherlands"},
    }

    geo_events = []
    for t in threats:
        geo = ip_geo.get(t.source_ip)
        if geo:
            geo_events.append({
                "ip": t.source_ip,
                "lat": geo["lat"],
                "lng": geo["lng"],
                "country": geo["country"],
                "threat_type": t.threat_type.value,
                "severity": t.severity.value,
                "timestamp": t.timestamp.isoformat(),
            })

    return {"geo_threats": geo_events}


@router.get("/adversarial-alerts")
async def get_adversarial_alerts(limit: int = Query(default=20, ge=1, le=100)):
    """Return recent adversarial AI attack alerts."""
    forge = get_forge()
    state = forge.get_dashboard_state()
    return {"alerts": state.adversarial_alerts[-limit:]}
