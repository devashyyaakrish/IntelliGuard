/**
 * AdversarialAlerts — Panel for AI-targeted attack detections
 */

import { motion, AnimatePresence } from 'framer-motion'
import { Brain, AlertTriangle } from 'lucide-react'
import { formatRelativeTime, formatConfidence } from '../../utils/helpers'

const ATTACK_ICONS = {
  distribution_shift: '📊',
  adversarial_input: '🤖',
  data_poisoning: '☠️',
  model_evasion: '👻',
}

const ATTACK_COLORS = {
  distribution_shift: 'text-purple-400 border-purple-400/30 bg-purple-400/10',
  adversarial_input: 'text-red-400 border-red-400/30 bg-red-400/10',
  data_poisoning: 'text-orange-400 border-orange-400/30 bg-orange-400/10',
  model_evasion: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10',
}

export default function AdversarialAlerts({ alerts }) {
  return (
    <div className="glass-card flex flex-col" style={{ maxHeight: 300 }}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-cyber-border shrink-0">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-cyber-purple" />
          <h3 className="text-xs font-mono font-semibold text-white tracking-wider uppercase">
            Adversarial AI Attacks
          </h3>
        </div>
        <span className="text-[10px] font-mono text-cyber-muted">{alerts.length} detected</span>
      </div>

      <div className="overflow-y-auto flex-1 min-h-0 divide-y divide-cyber-border/20">
        {alerts.length === 0 ? (
          <div className="flex items-center justify-center p-6">
            <p className="text-xs font-mono text-cyber-muted">No adversarial attacks detected</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {alerts.slice(0, 10).map((alert, i) => {
              const cls = ATTACK_COLORS[alert.attack_type] || 'text-gray-400 border-gray-400/30 bg-gray-400/10'
              return (
                <motion.div
                  key={alert.id || i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="px-4 py-3 hover:bg-cyber-border/10 transition-colors"
                >
                  <div className="flex items-start gap-2">
                    <span className="text-sm mt-0.5">
                      {ATTACK_ICONS[alert.attack_type] || '⚠️'}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`px-1.5 py-0.5 rounded border text-[10px] font-mono font-bold ${cls}`}>
                          {alert.attack_type?.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className="text-[10px] font-mono text-cyber-purple">
                          {formatConfidence(alert.confidence)}
                        </span>
                        <span className="text-[10px] font-mono text-cyber-muted ml-auto">
                          {formatRelativeTime(alert.timestamp)}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{alert.description}</p>
                      <p className="text-[10px] font-mono text-cyber-muted mt-1">
                        Target: <span className="text-cyber-neon">{alert.affected_model}</span>
                      </p>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        )}
      </div>
    </div>
  )
}
