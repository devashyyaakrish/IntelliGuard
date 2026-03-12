/**
 * Chart.js global registration — import this once
 */

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Global defaults for dark cyber theme
ChartJS.defaults.color = '#4a6282'
ChartJS.defaults.borderColor = '#1a2d4a'
ChartJS.defaults.font.family = "'JetBrains Mono', monospace"
ChartJS.defaults.font.size = 10
