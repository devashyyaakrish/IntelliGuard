/**
 * Utility functions for the MD-ADSS dashboard
 */

export function getSeverityColor(severity) {
  const map = {
    critical: '#ff3366',
    high: '#ff8c00',
    medium: '#ffd700',
    low: '#4a90e2',
    info: '#6b7280',
  }
  return map[severity?.toLowerCase()] || '#6b7280'
}

export function getSeverityBg(severity) {
  const map = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/40',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/40',
    info: 'bg-gray-500/20 text-gray-400 border-gray-500/40',
  }
  return map[severity?.toLowerCase()] || map.info
}

export function getThreatIcon(threatType) {
  const map = {
    brute_force: '🔨',
    ransomware: '🔒',
    phishing: '🎣',
    ddos: '🌊',
    malware: '🦠',
    data_exfiltration: '📤',
    suspicious_login: '🔐',
    c2_beacon: '📡',
    adversarial_input: '🤖',
    data_poisoning: '☠️',
    unknown: '❓',
  }
  return map[threatType] || '⚠️'
}

export function formatConfidence(confidence) {
  return `${Math.round((confidence || 0) * 100)}%`
}

export function formatTimestamp(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

export function formatRelativeTime(ts) {
  if (!ts) return '—'
  const diff = Date.now() - new Date(ts).getTime()
  const seconds = Math.floor(diff / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  return `${hours}h ago`
}

export function getRiskLabel(score) {
  if (score >= 0.8) return { label: 'CRITICAL', color: 'text-red-400' }
  if (score >= 0.6) return { label: 'HIGH', color: 'text-orange-400' }
  if (score >= 0.35) return { label: 'MEDIUM', color: 'text-yellow-400' }
  if (score >= 0.1) return { label: 'LOW', color: 'text-blue-400' }
  return { label: 'MINIMAL', color: 'text-green-400' }
}

export function humanizeThreatType(type) {
  const map = {
    brute_force: 'Brute Force',
    ransomware: 'Ransomware',
    phishing: 'Phishing',
    ddos: 'DDoS',
    malware: 'Malware',
    data_exfiltration: 'Data Exfil',
    suspicious_login: 'Susp. Login',
    c2_beacon: 'C2 Beacon',
    adversarial_input: 'Adversarial',
    data_poisoning: 'Data Poison',
    unknown: 'Unknown',
  }
  return map[type] || type
}

export function clamp(value, min = 0, max = 1) {
  return Math.min(Math.max(value, min), max)
}
