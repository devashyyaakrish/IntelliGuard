/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#050a14',
          card: '#0a1628',
          border: '#1a2d4a',
          neon: '#00d4ff',
          green: '#00ff88',
          red: '#ff3366',
          orange: '#ff8c00',
          purple: '#9b59ff',
          yellow: '#ffd700',
          muted: '#4a6282',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        pulse_red: 'pulse_red 2s cubic-bezier(0.4,0,0.6,1) infinite',
        scan: 'scan 3s linear infinite',
        glow: 'glow 2s ease-in-out infinite alternate',
        fadeIn: 'fadeIn 0.5s ease-in-out',
        slideUp: 'slideUp 0.4s ease-out',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      keyframes: {
        pulse_red: {
          '0%,100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        glow: {
          from: { boxShadow: '0 0 10px #00d4ff44, 0 0 20px #00d4ff22' },
          to: { boxShadow: '0 0 20px #00d4ff88, 0 0 40px #00d4ff44' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { transform: 'translateY(20px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
