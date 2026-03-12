/**
 * Topbar — Navigation header with system status
 */

import { motion } from 'framer-motion'
import { Shield, Wifi, WifiOff, Activity, Bell } from 'lucide-react'

export default function TopBar({ wsStatus, metrics, onScenario }) {
  const connected = wsStatus === 'connected'

  return (
    <header className="sticky top-0 z-50 h-14 flex items-center justify-between px-6 
                        bg-cyber-bg/90 backdrop-blur-md border-b border-cyber-border">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <Shield className="w-7 h-7 text-cyber-neon" />
          <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-cyber-green animate-ping-slow" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-wider text-white">
            MD-ADSS
          </h1>
          <p className="text-[10px] text-cyber-muted font-mono tracking-wider -mt-0.5">
            MULTI-DOMAIN ADVERSARIAL DECISION SUPPORT SYSTEM
          </p>
        </div>
      </div>

      {/* Center — Quick scenario controls */}
      <div className="hidden md:flex items-center gap-2">
        <span className="text-[10px] text-cyber-muted font-mono mr-1">SIMULATE:</span>
        {[
          { id: 'brute_force', label: 'BRUTE FORCE', color: 'border-cyber-orange/40 text-cyber-orange hover:bg-cyber-orange/10' },
          { id: 'ransomware', label: 'RANSOMWARE', color: 'border-cyber-red/40 text-cyber-red hover:bg-cyber-red/10' },
          { id: 'phishing', label: 'PHISHING', color: 'border-cyber-yellow/40 text-cyber-yellow hover:bg-cyber-yellow/10' },
          { id: 'all', label: 'ALL ATTACKS', color: 'border-cyber-purple/40 text-cyber-purple hover:bg-cyber-purple/10' },
          { id: 'none', label: 'NORMAL', color: 'border-cyber-border text-cyber-muted hover:bg-cyber-border/20' },
        ].map((s) => (
          <button
            key={s.id}
            onClick={() => onScenario(s.id)}
            className={`px-2 py-1 text-[9px] font-mono font-semibold tracking-widest rounded border transition-all duration-200 ${s.color}`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Right — Status indicators */}
      <div className="flex items-center gap-4">
        {/* Events/min */}
        <div className="hidden sm:flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-cyber-neon" />
          <span className="text-xs font-mono text-cyber-neon">
            {metrics?.events_per_minute?.toFixed(0) ?? '—'} <span className="text-cyber-muted">ev/min</span>
          </span>
        </div>

        {/* Active incidents */}
        {metrics?.active_incidents > 0 && (
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="flex items-center gap-1.5"
          >
            <Bell className="w-3.5 h-3.5 text-cyber-red animate-pulse" />
            <span className="text-xs font-mono text-cyber-red">
              {metrics.active_incidents} ACTIVE
            </span>
          </motion.div>
        )}

        {/* WS connection status */}
        <div className="flex items-center gap-1.5">
          {connected ? (
            <Wifi className="w-3.5 h-3.5 text-cyber-green" />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-cyber-red" />
          )}
          <span className={`text-[10px] font-mono ${connected ? 'text-cyber-green' : 'text-cyber-red'}`}>
            {connected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>

        {/* Nova badge */}
        <div className="hidden sm:flex items-center gap-1 px-2 py-1 rounded border border-cyber-neon/30 bg-cyber-neon/5">
          <span className="text-[9px] font-mono text-cyber-neon tracking-widest">AMAZON NOVA</span>
        </div>
      </div>
    </header>
  )
}
