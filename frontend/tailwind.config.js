/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        // Prism brand colors for ISRC Analyzer
        'prism-black': '#1A1A1A',
        'prism-red': '#E50914', 
        'prism-charcoal-gray': '#333333',
        'prism-medium-gray': '#666666',
        'prism-light-gray': '#F8F9FA',
        'precise-red': '#E50914', // Primary brand color
        'precise-black': '#1A1A1A', // Primary text
      },
      fontFamily: {
        'sans': ['Segoe UI', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['Consolas', 'Monaco', 'Liberation Mono', 'monospace'],
      },
      letterSpacing: {
        'wider': '0.1em',
        'widest': '0.3em',
      },
      animation: {
        'prism-pulse': 'prism-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        'prism-pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.6 },
        },
        'shimmer': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
}