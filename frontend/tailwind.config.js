/** @type {import('tailwindcss').Config} */
module.exports = {
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
        'prism-white': '#FFFFFF',
      },
      fontFamily: {
        'sans': ['Segoe UI', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['Consolas', 'Monaco', 'Liberation Mono', 'monospace'],
      },
      letterSpacing: {
        'tight': '-0.025em',
        'normal': '0em',
        'wide': '0.025em',
        'wider': '0.05em',
        'widest': '0.3em', // For PRISM wordmark
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      },
      spacing: {
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '5': '1.25rem',
        '6': '1.5rem',
        '8': '2rem',
        '10': '2.5rem',
        '12': '3rem',
        '16': '4rem',
        '20': '5rem',
        '24': '6rem',
      },
      borderRadius: {
        'sm': '0.125rem',
        'md': '0.375rem',
        'lg': '0.5rem',
        'xl': '0.75rem',
        '2xl': '1rem',
        'full': '9999px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(26, 26, 26, 0.05)',
        'md': '0 4px 6px -1px rgba(26, 26, 26, 0.1), 0 2px 4px -1px rgba(26, 26, 26, 0.06)',
        'lg': '0 10px 15px -3px rgba(26, 26, 26, 0.1), 0 4px 6px -2px rgba(26, 26, 26, 0.05)',
        'xl': '0 20px 25px -5px rgba(26, 26, 26, 0.1), 0 10px 10px -5px rgba(26, 26, 26, 0.04)',
        'prism-red': '0 4px 6px -1px rgba(229, 9, 20, 0.3)',
        'prism-red-lg': '0 10px 15px -3px rgba(229, 9, 20, 0.2)',
      },
      animation: {
        'spin': 'spin 1s linear infinite',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'prism-pulse': 'prism-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        'prism-pulse': {
          '0%, 100%': {
            opacity: '1',
          },
          '50%': {
            opacity: '0.6',
          },
        },
        'shimmer': {
          '0%': { 
            transform: 'translateX(-100%)' 
          },
          '100%': { 
            transform: 'translateX(100%)' 
          },
        },
      },
      backgroundImage: {
        'gradient-prism': 'linear-gradient(135deg, #1A1A1A 0%, #333333 100%)',
        'gradient-red': 'linear-gradient(135deg, #E50914 0%, #B8070F 100%)',
        'gradient-score-high': 'linear-gradient(135deg, #E50914 0%, #ff4757 100%)',
        'gradient-score-medium': 'linear-gradient(135deg, #ffa502 0%, #ff6348 100%)',
        'gradient-score-low': 'linear-gradient(135deg, #666666 0%, #333333 100%)',
      },
    },
  },
  plugins: [],
}