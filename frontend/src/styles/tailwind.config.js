/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Keep Prism brand colors but apply to ISRC Analyzer
        'prism-black': '#1A1A1A',
        'prism-red': '#E50914', 
        'prism-charcoal-gray': '#333333',
        'prism-medium-gray': '#666666',
        'prism-light-gray': '#F8F9FA',
        'precise-red': '#E50914', // Primary brand color
        'precise-black': '#1A1A1A', // Primary text
      },
      fontFamily: {
        'sans': ['Segoe UI', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['Consolas', 'Monaco', 'monospace'],
      },
      letterSpacing: {
        'wider': '0.1em',
        'widest': '0.2em',
      }
    },
  },
  plugins: [],
}