# ISRC Analyzer - Frontend

**Phase 2 Implementation: Web Interface with Prism Brand Integration**

Prism Analytics Engine transforms music industry data into actionable insights for independent artists and labels, with complete YouTube integration and professional lead generation capabilities.

## 🎯 Project Overview

This is the React frontend for the Precise Digital Lead Generation Tool, now fully branded as **Prism Analytics Engine**. The interface provides a professional, data-driven experience for music industry professionals to identify and analyze potential leads.

### Key Features

- **🎨 Prism Brand Integration**: Complete visual identity implementation following brand guidelines
- **📊 Real-time Analytics Dashboard**: Live data visualization and KPI tracking
- **🎵 ISRC Analysis**: Individual track analysis with comprehensive scoring
- **📁 Bulk Processing**: Handle hundreds of ISRCs with progress tracking
- **🗃️ Leads Database**: Advanced filtering, sorting, and management
- **📺 YouTube Integration**: Channel discovery and opportunity identification
- **⚙️ Settings & Configuration**: API management and system monitoring

## 🎨 Prism Brand Implementation

### Visual Identity

The frontend implements the complete Prism brand identity:

- **Colors**: Prism Black (#1A1A1A), Precise Red (#E50914), strategic grays
- **Typography**: Segoe UI with precise letter spacing for the PRISM wordmark
- **Logo**: Custom SVG implementation showing music notes → triangular prism → sin wave analytics
- **Design**: Clean, modern interface emphasizing data and functionality

### Brand Elements

```css
/* Prism Color Palette */
--prism-black: #1A1A1A        /* Primary brand color */
--prism-red: #E50914          /* Accent & energy color */
--prism-charcoal-gray: #333333 /* Secondary dark */
--prism-white: #FFFFFF        /* Primary background */
--prism-light-gray: #F8F9FA   /* Background accent */
--prism-medium-gray: #666666  /* Body text */
```

### Typography Hierarchy

- **Wordmark**: `P R I S M` with 0.3em letter spacing
- **Headers**: Segoe UI with tracking adjustments
- **Data**: Monospace fonts for numerical precision
- **Body**: Clean, readable sans-serif

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm 8+
- Backend API running on `localhost:5000`
- YouTube Data API key (optional, for full functionality)

### Installation

```bash
# Clone the repository
git clone https://github.com/precise-digital/prism-analytics-engine
cd prism-analytics-engine/frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at `http://localhost:3000` with hot reloading enabled.

### Environment Setup

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_VERSION=1.0.0
REACT_APP_PRISM_ENVIRONMENT=development
```

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html              # HTML template with Prism meta tags
│   └── favicon.ico             # Prism-branded favicon
├── src/
│   ├── components/
│   │   ├── Dashboard.js        # Analytics overview
│   │   ├── ISRCAnalyzer.js     # Single ISRC analysis
│   │   ├── BulkProcessor.js    # Batch processing interface
│   │   ├── LeadsList.js        # Lead management
│   │   ├── YouTubeIntegration.js # YouTube features
│   │   └── Settings.js         # Configuration panel
│   ├── styles/
│   │   ├── globals.css         # Prism brand styles
│   │   └── tailwind.config.js  # Custom Tailwind configuration
│   ├── utils/
│   │   ├── api.js              # API client
│   │   └── constants.js        # App constants
│   ├── App.js                  # Main application with Prism branding
│   └── index.js                # Application entry point
├── package.json                # Dependencies and scripts
└── README.md                   # This file
```

## 🛠️ Development

### Available Scripts

```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run test suite
npm run lint       # ESLint checking
npm run format     # Prettier formatting
npm run analyze    # Bundle size analysis
```

### Code Quality

The project includes:

- **ESLint**: Code quality and consistency
- **Prettier**: Automatic code formatting
- **Husky**: Pre-commit hooks
- **Jest**: Unit testing framework

### Development Guidelines

1. **Component Structure**: Each major feature is a separate component
2. **Styling**: Use Prism-specific Tailwind classes and CSS custom properties
3. **State Management**: React hooks for local state, context for global state
4. **API Integration**: Centralized API client with error handling
5. **Accessibility**: WCAG 2.1 AA compliance

## 🎨 Styling & Theming

### Prism Design System

The application uses a comprehensive design system:

```css
/* Custom Prism Components */
.prism-card           /* Standard card component */
.prism-button         /* Primary action button */
.prism-input          /* Form input styling */
.prism-table          /* Data table styling */
.prism-badge-tier-a   /* Lead tier badges */
.prism-stat-card      /* Dashboard statistics */
.prism-progress-bar   /* Progress indicators */
```

### Responsive Design

- **Mobile First**: Optimized for mobile devices
- **Breakpoints**: Standard Tailwind responsive breakpoints
- **Touch Friendly**: Appropriate touch targets and spacing
- **Performance**: Optimized images and lazy loading

## 📊 Features Deep Dive

### Dashboard
- Real-time KPI visualization
- Lead distribution charts
- YouTube integration status
- System health monitoring

### ISRC Analyzer
- Single track analysis
- Multi-source data aggregation
- Lead scoring visualization
- YouTube channel discovery

### Bulk Processing
- Drag & drop file upload
- CSV/TXT parsing
- Progress tracking
- Batch size optimization
- Export functionality

### Leads Database
- Advanced filtering and sorting
- Contact information management
- Outreach status tracking
- YouTube opportunity highlighting
- CSV export

### YouTube Integration
- Channel discovery and analysis
- Growth opportunity identification
- API status monitoring
- Test functionality

### Settings
- API configuration management
- System status overview
- Processing preferences
- Security and privacy information

## 🔧 Configuration

### Tailwind CSS

Custom Tailwind configuration includes:

- Prism brand colors
- Custom spacing scale
- Typography utilities
- Component classes
- Animation utilities

### API Integration

The frontend communicates with the backend via:

- RESTful API endpoints
- JSON data exchange
- Error handling and retry logic
- Rate limiting awareness
- Progress tracking for long operations

## 🚀 Deployment

### Production Build

```bash
# Create optimized production build
npm run build

# Serve locally for testing
npx serve -s build -l 3000
```

### Environment Variables

Production environment should include:

```env
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_VERSION=1.0.0
REACT_APP_PRISM_ENVIRONMENT=production
REACT_APP_SENTRY_DSN=your_sentry_dsn
```

### Hosting Options

- **Vercel**: Recommended for easy deployment
- **Netlify**: Great for static hosting
- **AWS S3 + CloudFront**: Enterprise solution
- **Docker**: Containerized deployment

## 🔒 Security

### Data Protection

- No sensitive data stored in frontend
- API keys managed server-side
- HTTPS enforcement in production
- Content Security Policy headers
- XSS protection

### Privacy Compliance

- GDPR-compliant data handling
- No tracking without consent
- Transparent data usage
- User control over data processing

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Issues**
   ```bash
   # Check backend is running
   curl http://localhost:5000/api/status
   ```

2. **Build Failures**
   ```bash
   # Clear cache and reinstall
   npm run clean
   npm install
   ```

3. **Styling Issues**
   ```bash
   # Rebuild Tailwind
   npm run build:css
   ```

### Debug Mode

Enable debug logging:

```env
REACT_APP_DEBUG=true
REACT_APP_LOG_LEVEL=debug
```

## 📈 Performance

### Optimization Features

- **Code Splitting**: Lazy loading of routes
- **Image Optimization**: WebP format with fallbacks
- **Caching**: Aggressive caching of static assets
- **Bundle Analysis**: Regular bundle size monitoring
- **Lighthouse Scores**: Target 90+ in all categories

### Monitoring

- Performance metrics tracking
- Error boundary implementation
- User analytics (privacy-compliant)
- API response time monitoring

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards

- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure accessibility compliance
- Test across browsers

## 📄 License
This project is licensed under the MIT License - see LICENSE file for details.
