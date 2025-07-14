/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // Prism Brand Colors from Brand Pack
        'prism-black': '#1A1A1A',           // Primary Brand Color - Sophistication, authority, premium quality
        'prism-red': '#E50914',             // Accent & Energy Color - Passion, energy, innovation, urgency  
        'prism-charcoal-gray': '#333333',   // Secondary Dark - Support text, subtle elements
        'prism-white': '#FFFFFF',           // Primary Background - Clean, modern, spacious
        'prism-light-gray': '#F8F9FA',      // Background Accent - Subtle backgrounds, sections
        'prism-medium-gray': '#666666',     // Body Text - Readable body text, descriptions
      },
      fontFamily: {
        // Prism Typography
        'sans': ['Segoe UI', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        'mono': ['Consolas', 'Monaco', 'Liberation Mono', 'Lucida Console', 'monospace'],
      },
      letterSpacing: {
        'widest': '0.3em',  // For PRISM brand wordmark spacing
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      boxShadow: {
        'prism': '0 4px 6px -1px rgba(229, 9, 20, 0.1), 0 2px 4px -1px rgba(229, 9, 20, 0.06)',
        'prism-lg': '0 10px 15px -3px rgba(229, 9, 20, 0.1), 0 4px 6px -2px rgba(229, 9, 20, 0.05)',
      },
      backgroundImage: {
        'prism-gradient': 'linear-gradient(135deg, #E50914 0%, #1A1A1A 100%)',
        'prism-subtle': 'linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%)',
      },
      borderColor: {
        'prism-red': '#E50914',
        'prism-light-gray': '#F8F9FA',
        'prism-charcoal-gray': '#333333',
      },
      ringColor: {
        'prism-red': '#E50914',
      },
      focusColor: {
        'prism-red': '#E50914',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    // Custom plugin for Prism-specific utilities
    function({ addUtilities }) {
      const newUtilities = {
        '.text-prism-gradient': {
          background: 'linear-gradient(135deg, #E50914 0%, #1A1A1A 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
        '.border-prism-gradient': {
          border: '1px solid',
          'border-image': 'linear-gradient(135deg, #E50914 0%, #1A1A1A 100%) 1',
        },
        '.prism-card': {
          'background': '#FFFFFF',
          'border': '1px solid #F8F9FA',
          'border-radius': '0.5rem',
          'box-shadow': '0 1px 3px 0 rgba(26, 26, 26, 0.1), 0 1px 2px 0 rgba(26, 26, 26, 0.06)',
          'transition': 'all 0.2s ease-in-out',
        },
        '.prism-card:hover': {
          'box-shadow': '0 4px 6px -1px rgba(229, 9, 20, 0.1), 0 2px 4px -1px rgba(229, 9, 20, 0.06)',
          'border-color': '#E50914',
        },
        '.prism-button': {
          'background': '#E50914',
          'color': '#FFFFFF',
          'font-weight': '500',
          'letter-spacing': '0.05em',
          'border-radius': '0.375rem',
          'transition': 'all 0.2s ease-in-out',
          'border': 'none',
        },
        '.prism-button:hover': {
          'background': '#B8070F',
          'box-shadow': '0 4px 6px -1px rgba(229, 9, 20, 0.3)',
        },
        '.prism-button:focus': {
          'outline': 'none',
          'box-shadow': '0 0 0 3px rgba(229, 9, 20, 0.3)',
        },
        '.prism-input': {
          'border': '1px solid #F8F9FA',
          'border-radius': '0.375rem',
          'background': '#FFFFFF',
          'color': '#1A1A1A',
          'transition': 'all 0.2s ease-in-out',
        },
        '.prism-input:focus': {
          'outline': 'none',
          'border-color': '#E50914',
          'box-shadow': '0 0 0 3px rgba(229, 9, 20, 0.1)',
        },
        '.prism-table-header': {
          'background': '#F8F9FA',
          'color': '#333333',
          'font-weight': '500',
          'font-size': '0.75rem',
          'letter-spacing': '0.1em',
          'text-transform': 'uppercase',
          'padding': '0.75rem 1.5rem',
          'border-bottom': '1px solid #F8F9FA',
        },
        '.prism-data': {
          'font-family': 'Consolas, Monaco, Liberation Mono, Lucida Console, monospace',
          'font-weight': '400',
          'letter-spacing': '0.025em',
        },
        '.prism-stat-card': {
          'background': '#FFFFFF',
          'border': '1px solid #F8F9FA',
          'border-radius': '0.5rem',
          'padding': '1.5rem',
          'transition': 'all 0.2s ease-in-out',
        },
        '.prism-stat-card:hover': {
          'border-color': '#E50914',
          'box-shadow': '0 4px 6px -1px rgba(229, 9, 20, 0.1)',
        },
        '.prism-progress-bar': {
          'background': '#F8F9FA',
          'border-radius': '9999px',
          'height': '0.5rem',
          'overflow': 'hidden',
        },
        '.prism-progress-fill': {
          'background': 'linear-gradient(90deg, #E50914 0%, #B8070F 100%)',
          'height': '100%',
          'border-radius': '9999px',
          'transition': 'all 0.3s ease-in-out',
        },
        '.prism-badge-a': {
          'background': '#10B981',
          'color': '#FFFFFF',
          'border': '1px solid #059669',
        },
        '.prism-badge-b': {
          'background': '#E50914',
          'color': '#FFFFFF',
          'border': '1px solid #B8070F',
        },
        '.prism-badge-c': {
          'background': '#F59E0B',
          'color': '#FFFFFF',
          'border': '1px solid #D97706',
        },
        '.prism-badge-d': {
          'background': '#F8F9FA',
          'color': '#333333',
          'border': '1px solid #333333',
        },
        '.prism-youtube-accent': {
          'background': 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)',
          'color': '#FFFFFF',
        },
        '.prism-spotify-accent': {
          'background': 'linear-gradient(135deg, #1DB954 0%, #1ED760 100%)',
          'color': '#FFFFFF',
        }
      }
      
      addUtilities(newUtilities)
    }
  ],
}