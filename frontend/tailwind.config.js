/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#0a0a0f',
          darker: '#05050a',
          accent: '#00f0ff',
          success: '#00ff88',
          danger: '#ff0000',
          warning: '#ffff00',
        }
      },
      fontFamily: {
        cyber: ['Courier New', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'gradient-shift': 'gradient-shift 3s ease-in-out infinite',
        'matrix-shift': 'matrix-shift 20s linear infinite',
      }
    },
  },
  plugins: [],
}
