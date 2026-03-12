/**
 * App.jsx — Main MD-ADSS Dashboard Application
 */

import '../components/charts/chartSetup'

import TopBar from '../components/layout/TopBar'
import MetricsRow from '../components/dashboard/MetricsRow'
import RiskGauge from '../components/dashboard/RiskGauge'
import ThreatFeed from '../components/dashboard/ThreatFeed'
import IncidentPanel from '../components/dashboard/IncidentPanel'
import AdversarialAlerts from '../components/alerts/AdversarialAlerts'
import RiskTrendChart from '../components/charts/RiskTrendChart'
import ThreatTypeChart from '../components/charts/ThreatTypeChart'
import AttackFrequencyChart from '../components/charts/AttackFrequencyChart'
import AttackMap from '../components/maps/AttackMap'

import { useDashboard } from '../hooks/useDashboard'

export default function App() {
  const {
    wsStatus,
    metrics,
    threats,
    incidents,
    adversarialAlerts,
    riskTrend,
    threatTypeData,
    attackFrequencyData,
    geoThreats,
    setScenario,
    resolveIncident,
  } = useDashboard()

  return (
    <div className="min-h-screen bg-cyber-bg text-white font-mono relative overflow-x-hidden">
      {/* Scanline overlay */}
      <div className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
           style={{
             backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,212,255,0.15) 2px, rgba(0,212,255,0.15) 4px)',
           }} />

      <TopBar
        wsStatus={wsStatus}
        metrics={metrics}
        onScenario={setScenario}
      />

      <main className="max-w-[1920px] mx-auto px-4 pb-8 pt-2 space-y-4">

        {/* Row 1: KPI Metrics */}
        <MetricsRow metrics={metrics} />

        {/* Row 2: Risk Gauge | Threat Feed | Incident Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-2">
            <RiskGauge score={metrics?.risk_score ?? 0} />
          </div>
          <div className="lg:col-span-5">
            <ThreatFeed threats={threats} />
          </div>
          <div className="lg:col-span-5">
            <IncidentPanel incidents={incidents} onResolve={resolveIncident} />
          </div>
        </div>

        {/* Row 3: Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <RiskTrendChart data={riskTrend} />
          <ThreatTypeChart data={threatTypeData} />
          <AttackFrequencyChart data={attackFrequencyData} />
        </div>

        {/* Row 4: Attack Map | Adversarial Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <AttackMap geoThreats={geoThreats} />
          <AdversarialAlerts alerts={adversarialAlerts} />
        </div>

      </main>
    </div>
  )
}
