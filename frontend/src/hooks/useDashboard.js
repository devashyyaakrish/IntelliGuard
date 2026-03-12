/**
 * useDashboard — Custom hook for real-time dashboard data management
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '../services/api'
import { wsService } from '../services/websocket'

const POLL_INTERVAL = 8000 // 8s fallback polling

export function useDashboard() {
  const [metrics, setMetrics] = useState(null)
  const [threats, setThreats] = useState([])
  const [incidents, setIncidents] = useState([])
  const [riskTrend, setRiskTrend] = useState([])
  const [attackFreq, setAttackFreq] = useState([])
  const [threatTypes, setThreatTypes] = useState({})
  const [severityDist, setSeverityDist] = useState({})
  const [geoThreats, setGeoThreats] = useState([])
  const [adversarialAlerts, setAdversarialAlerts] = useState([])
  const [wsStatus, setWsStatus] = useState('connecting')
  const [loading, setLoading] = useState(true)
  const pollRef = useRef(null)

  const fetchAll = useCallback(async () => {
    try {
      const [
        dashboard, threatData, incidentData,
        trendData, freqData, typeData, sevData, geoData, advData
      ] = await Promise.allSettled([
        api.getDashboard(),
        api.getThreats(50),
        api.getIncidents(),
        api.getRiskTrend(),
        api.getAttackFrequency(),
        api.getThreatTypes(),
        api.getSeverityDistribution(),
        api.getGeoThreats(),
        api.getAdversarialAlerts(),
      ])

      if (dashboard.status === 'fulfilled') {
        const d = dashboard.value
        setMetrics(d.metrics)
        setRiskTrend(d.risk_trend || [])
        setAttackFreq(d.attack_frequency || [])
        setAdversarialAlerts(d.adversarial_alerts || [])
      }
      if (threatData.status === 'fulfilled') setThreats(threatData.value.threats || [])
      if (incidentData.status === 'fulfilled') setIncidents(incidentData.value.incidents || [])
      if (trendData.status === 'fulfilled') setRiskTrend(trendData.value.trend || [])
      if (freqData.status === 'fulfilled') setAttackFreq(freqData.value.frequency || [])
      if (typeData.status === 'fulfilled') setThreatTypes(typeData.value.by_type || {})
      if (sevData.status === 'fulfilled') setSeverityDist(sevData.value.distribution || {})
      if (geoData.status === 'fulfilled') setGeoThreats(geoData.value.geo_threats || [])
      if (advData.status === 'fulfilled') setAdversarialAlerts(advData.value.alerts || [])
    } catch (e) {
      console.error('Dashboard fetch error:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  // WebSocket real-time updates
  useEffect(() => {
    wsService.connect()

    const unsubConn = wsService.on('connection', ({ status }) => setWsStatus(status))

    const unsubMetrics = wsService.on('metrics_update', (data) => {
      setMetrics(data)
    })

    const unsubThreat = wsService.on('threat_detected', (data) => {
      if (data?.threat) {
        setThreats((prev) => [data.threat, ...prev].slice(0, 100))
      }
    })

    // Also handle initial state and periodic updates
    const unsubInitial = wsService.on('initial_state', (data) => {
      if (data?.metrics) setMetrics(data.metrics)
      if (data?.recent_incidents) setIncidents(data.recent_incidents)
      if (data?.risk_trend) setRiskTrend(data.risk_trend)
      if (data?.attack_frequency) setAttackFreq(data.attack_frequency)
    })

    return () => {
      unsubConn()
      unsubMetrics()
      unsubThreat()
      unsubInitial()
    }
  }, [])

  // Polling fallback
  useEffect(() => {
    fetchAll()
    pollRef.current = setInterval(fetchAll, POLL_INTERVAL)
    return () => clearInterval(pollRef.current)
  }, [fetchAll])

  const setScenario = useCallback(async (scenario) => {
    await api.setScenario(scenario)
    setTimeout(fetchAll, 1000)
  }, [fetchAll])

  const resolveIncident = useCallback(async (id) => {
    await api.resolveIncident(id)
    setIncidents((prev) => prev.map((i) =>
      i.id === id ? { ...i, status: 'resolved' } : i
    ))
  }, [])

  return {
    metrics,
    threats,
    incidents,
    riskTrend,
    attackFrequencyData: attackFreq,
    threatTypeData: threatTypes,
    severityDist,
    geoThreats,
    adversarialAlerts,
    connected: wsStatus === 'connected',
    wsStatus,
    loading,
    refetch: fetchAll,
    setScenario,
    resolveIncident,
  }
}
