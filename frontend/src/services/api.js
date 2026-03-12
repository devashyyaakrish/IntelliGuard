/**
 * API Service — Backend communication layer
 */

const BASE_URL = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

export const api = {
  // Dashboard
  getDashboard: () => request('/analytics/dashboard'),
  getRiskTrend: () => request('/analytics/risk-trend'),
  getAttackFrequency: () => request('/analytics/attack-frequency'),
  getSeverityDistribution: () => request('/analytics/severity-distribution'),
  getThreatTypes: () => request('/analytics/threat-types'),
  getGeoThreats: () => request('/analytics/geo-threats'),
  getAdversarialAlerts: () => request('/analytics/adversarial-alerts'),

  // Threats
  getThreats: (limit = 50, severity = null) => {
    const params = new URLSearchParams({ limit })
    if (severity) params.append('severity', severity)
    return request(`/threats?${params}`)
  },
  getTopAttackers: (limit = 10) => request(`/threats/top-attackers?limit=${limit}`),
  setScenario: (scenario) =>
    request(`/threats/scenario/${scenario}`, { method: 'POST' }),

  // Incidents
  getIncidents: (status = null, limit = 20) => {
    const params = new URLSearchParams({ limit })
    if (status) params.append('status', status)
    return request(`/incidents?${params}`)
  },
  getIncident: (id) => request(`/incidents/${id}`),
  resolveIncident: (id) => request(`/incidents/${id}/resolve`, { method: 'POST' }),
  exportReport: () => request('/incidents/export/report'),
}
