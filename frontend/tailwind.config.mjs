/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'prism-black': '#1A1A1A',
        'prism-red': '#E50914', 
        'prism-charcoal-gray': '#333333',
        'prism-medium-gray': '#666666',
        'prism-light-gray': '#F8F9FA',
      },
      fontFamily: {
        'sans': ['Segoe UI', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['Consolas', 'Monaco', 'Liberation Mono', 'monospace'],
      },
      letterSpacing: {
        'wider': '0.1em',
        'widest': '0.3em',
      },
    },
  },
}