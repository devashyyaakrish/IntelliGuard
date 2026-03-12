/**
 * IncidentPanel — Active incident response list with Nova Act decisions
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronRight, CheckCircle, AlertOctagon } from 'lucide-react'
import { getSeverityBg, getThreatIcon, humanizeThreatType, formatRelativeTime } from '../../utils/helpers'

function IncidentRow({ incident, onResolve }) {
  const [expanded, setExpanded] = useState(false)
  const threat = incident.threat
  const response = incident.response

  const statusColor = {
    detected: 'text-yellow-400',
    analyzing: 'text-blue-400',
    responding: 'text-orange-400',
    mitigated: 'text-green-400',
    resolved: 'text-gray-400',
  }[incident.status] || 'text-gray-400'

  return (
    <motion.div
      layout
      className="border border-cyber-border/50 rounded-lg overflow-hidden mb-2"
    >
      {/* Summary row */}
      <button
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-cyber-border/10 transition-colors text-left"
        onClick={() => setExpanded((v) => !v)}
      >
        <span className="text-base">{getThreatIcon(threat?.threat_type)}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold font-mono text-white">
              {humanizeThreatType(threat?.threat_type)}
            </span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono border ${getSeverityBg(threat?.severity)}`}>
              {threat?.severity?.toUpperCase()}
            </span>
            <span className={`text-[10px] font-mono uppercase tracking-wide ${statusColor}`}>
              {incident.status}
            </span>
          </div>
          <p className="text-[11px] text-cyber-muted mt-0.5 truncate">{threat?.source_ip}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[10px] font-mono text-cyber-muted">{formatRelativeTime(incident.timestamp)}</span>
          {expanded ? (
            <ChevronDown className="w-3.5 h-3.5 text-cyber-muted" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-cyber-muted" />
          )}
        </div>
      </button>

      {/* Expanded: Nova Act response plan */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden border-t border-cyber-border/40"
          >
            <div className="px-4 py-3 space-y-3">
              {/* Explanation */}
              <div>
                <p className="text-[10px] font-mono text-cyber-neon uppercase tracking-wider mb-1">
                  Nova Lite Analysis
                </p>
                <p className="text-[11px] text-slate-300">{threat?.explanation}</p>
              </div>

              {/* Response plan */}
              {response && (
                <div>
                  <p className="text-[10px] font-mono text-cyber-purple uppercase tracking-wider mb-1">
                    Nova Act Response Plan
                  </p>
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {response.actions?.map((action) => (
                      <span key={action} className="px-2 py-0.5 rounded border border-cyber-purple/30 bg-cyber-purple/10 text-[10px] font-mono text-cyber-purple">
                        {action}
                      </span>
                    ))}
                  </div>
                  <p className="text-[11px] text-slate-400 italic">{response.reasoning}</p>

                  {response.execution_steps?.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {response.execution_steps.slice(0, 4).map((step, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className="text-[10px] font-mono text-cyber-muted">{i + 1}.</span>
                          <span className="text-[11px] text-slate-400">{step.replace(/^\d+\.\s*/, '')}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {response.auto_execute && (
                    <div className="mt-2 flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                      <span className="text-[10px] font-mono text-green-400">AUTO-EXECUTED</span>
                    </div>
                  )}
                </div>
              )}

              {/* Timeline */}
              {incident.timeline?.length > 0 && (
                <div>
                  <p className="text-[10px] font-mono text-cyber-muted uppercase tracking-wider mb-1">Timeline</p>
                  <div className="space-y-1 border-l border-cyber-border/50 pl-3">
                    {incident.timeline.slice(0, 4).map((t, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="text-[9px] font-mono text-cyber-muted shrink-0 mt-0.5">
                          {new Date(t.time).toLocaleTimeString('en-US', { hour12: false })}
                        </span>
                        <span className="text-[11px] text-slate-400">{t.event}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Resolve button */}
              {incident.status !== 'resolved' && incident.status !== 'mitigated' && (
                <button
                  onClick={() => onResolve(incident.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-green-500/30 
                             bg-green-500/10 text-green-400 text-[11px] font-mono hover:bg-green-500/20 transition-colors"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  Mark Resolved
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function IncidentPanel({ incidents, onResolve }) {
  const active = incidents.filter((i) => !['resolved', 'mitigated'].includes(i.status))

  return (
    <div className="glass-card flex flex-col h-full" style={{ maxHeight: 420 }}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-cyber-border shrink-0">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-cyber-orange" />
          <h3 className="text-xs font-mono font-semibold text-white tracking-wider uppercase">Incident Response</h3>
        </div>
        <div className="flex items-center gap-2">
          {active.length > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400 text-[10px] font-mono border border-orange-500/30">
              {active.length} ACTIVE
            </span>
          )}
        </div>
      </div>

      <div className="overflow-y-auto flex-1 min-h-0 p-3">
        {incidents.length === 0 ? (
          <div className="flex items-center justify-center h-20">
            <p className="text-xs font-mono text-cyber-muted">No incidents</p>
          </div>
        ) : (
          <AnimatePresence>
            {incidents.slice(0, 15).map((i) => (
              <IncidentRow key={i.id} incident={i} onResolve={onResolve} />
            ))}
          </AnimatePresence>
        )}
      </div>

      <div className="px-4 py-2 border-t border-cyber-border/50 shrink-0">
        <span className="text-[9px] font-mono text-cyber-muted">Decisions by </span>
        <span className="text-[9px] font-mono text-cyber-purple font-semibold">AMAZON NOVA ACT</span>
        <span className="text-[9px] font-mono text-cyber-muted"> · Orchestrated by </span>
        <span className="text-[9px] font-mono text-cyber-green font-semibold">NOVA FORGE</span>
      </div>
    </div>
  )
}
