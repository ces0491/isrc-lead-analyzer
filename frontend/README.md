# Prism Analytics Engine - Frontend

**Complete React Frontend with Triangular Prism Branding and Full Backend Integration**

Prism Analytics Engine transforms music industry data into actionable insights for independent artists and labels, featuring comprehensive YouTube integration and professional lead generation capabilities.

## 🎯 Project Overview

This is the React frontend for the Precise Digital Lead Generation Tool, fully branded as **Prism Analytics Engine**. The interface provides a professional, data-driven experience for music industry professionals to identify and analyze potential leads.

### ✨ Key Features

- **🎨 Prism Brand Integration**: Complete visual identity with triangular prism loading animations
- **📊 Real-time Analytics Dashboard**: Live data visualization and KPI tracking
- **🎵 ISRC Analysis**: Individual track analysis with comprehensive scoring
- **📁 Bulk Processing**: Handle hundreds of ISRCs with progress tracking
- **🗃️ Leads Database**: Advanced filtering, sorting, and management
- **📺 YouTube Integration**: Channel discovery and opportunity identification
- **⚙️ Settings & Configuration**: API management and system monitoring

## 🎨 Triangular Prism Brand Implementation

### Visual Identity Updates

The frontend now implements the complete Prism brand identity with **triangular prism** elements:

- **Loading Animation**: 3D triangular prism with rotation and pulsing effects
- **Logo**: Custom SVG showing music notes → triangular prism → sin wave analytics
- **Colors**: Prism Black (#1A1A1A), Precise Red (#E50914), strategic grays
- **Typography**: Segoe UI with precise letter spacing for the PRISM wordmark

### Brand Elements

```css
/* Updated Prism Color Palette */
--prism-black: #1A1A1A        /* Primary brand color */
--prism-red: #E50914          /* Accent & energy color */
--prism-charcoal-gray: #333333 /* Secondary dark */
--prism-white: #FFFFFF        /* Primary background */
--prism-light-gray: #F8F9FA   /* Background accent */
--prism-medium-gray: #666666  /* Body text */
```

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm 8+
- Backend API running (see backend deployment guide)
- YouTube Data API key (optional, for full functionality)

### Installation

```bash
# Clone the repository
git clone https://github.com/precise-digital/prism-analytics-engine
cd prism-analytics-engine/frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Configure your environment
nano .env

# Start development server
npm start
```

The app will open at `http://localhost:3000` with hot reloading enabled.

### Environment Configuration

Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:5000/api

# Application Configuration  
REACT_APP_VERSION=1.0.0
REACT_APP_PRISM_ENVIRONMENT=development
REACT_APP_COMPANY_NAME=Precise Digital
REACT_APP_APP_NAME=Prism Analytics Engine

# Feature Flags
REACT_APP_ENABLE_YOUTUBE_INTEGRATION=true
REACT_APP_ENABLE_BULK_PROCESSING=true
REACT_APP_ENABLE_EXPORT_FEATURES=true

# Branding
REACT_APP_BRAND_PRIMARY_COLOR=#1A1A1A
REACT_APP_BRAND_ACCENT_COLOR=#E50914
REACT_APP_BRAND_COMPANY_URL=https://precise.digital
```

## 📁 Updated Project Structure

```
frontend/
├── public/
│   ├── index.html              # Updated with triangular prism loading
│   ├── favicon.ico             # Prism-branded favicon
│   └── manifest.json           # PWA manifest
├── src/
│   ├── components/
│   │   ├── Dashboard.js        # Enhanced analytics overview
│   │   ├── ISRCAnalyzer.js     # Updated with full API integration
│   │   ├── BulkProcessor.js    # Batch processing interface
│   │   ├── LeadsList.js        # Lead management with filtering
│   │   ├── YouTubeIntegration.js # YouTube-specific features
│   │   └── Settings.js         # Enhanced configuration panel
│   ├── styles/
│   │   ├── globals.css         # Updated Prism brand styles
│   │   └── index.css           # Main stylesheet
│   ├── utils/
│   │   ├── api.js              # Centralized API client
│   │   └── constants.js        # Application constants
│   ├── App.js                  # Main application with triangular prism
│   └── index.js                # Application entry point
├── tailwind.config.js          # Custom Tailwind with Prism colors
├── package.json                # Updated dependencies
└── README.md                   # This file
```

## 🛠️ Development

### Available Scripts

```bash
npm start          # Start development server
npm run build      # Build for production
npm run build:production # Build with production API URL
npm run build:development # Build with local API URL
npm test           # Run test suite
npm run test:coverage # Run tests with coverage
npm run lint       # ESLint checking
npm run lint:fix   # Auto-fix ESLint issues
npm run format     # Prettier formatting
npm run analyze    # Bundle size analysis
npm run clean      # Clean node_modules and reinstall
npm run serve      # Serve production build locally
```

### Code Quality

The project includes:

- **ESLint**: Code quality and consistency
- **Prettier**: Automatic code formatting
- **Husky**: Pre-commit hooks
- **Jest**: Unit testing framework
- **TypeScript**: Type checking (optional)

## 🎨 Enhanced Styling & Theming

### Prism Design System

The application uses a comprehensive design system with triangular prism elements:

```css
/* Custom Prism Components */
.prism-card           /* Standard card component */
.prism-button         /* Primary action button */
.prism-input          /* Form input styling */
.prism-table          /* Data table styling */
.prism-badge-tier-a   /* Lead tier badges */
.prism-stat-card      /* Dashboard statistics */
.prism-progress-bar   /* Progress indicators */
.prism-triangular-loader /* Triangular prism loading animation */
```

### Triangular Prism Loading Animation

The loading screen now features a 3D triangular prism:

```css
.prism-triangular-loader {
    width: 60px;
    height: 60px;
    animation: prism-rotate 2s linear infinite;
}

@keyframes prism-rotate {
    0% { transform: rotateY(0deg); }
    100% { transform: rotateY(360deg); }
}
```

## 📊 Features Deep Dive

### Enhanced Dashboard
- Real-time KPI visualization with triangular prism elements
- Lead distribution charts with tier-based color coding
- YouTube integration status with detailed metrics
- System health monitoring
- Quick action buttons for common tasks

### Advanced ISRC Analyzer
- Enhanced input validation with real-time feedback
- Comprehensive results display with score breakdowns
- YouTube channel discovery and analysis
- Contact information extraction and display
- Data source tracking and processing summaries

### Improved Bulk Processing
- Drag & drop file upload with validation
- Real-time progress tracking with prism-themed indicators
- Configurable batch sizes and processing options
- Detailed results summary with YouTube statistics
- Enhanced error handling and retry logic

### Comprehensive Leads Database
- Advanced filtering with multiple criteria
- Sortable columns with visual indicators
- Expandable lead details with contact information
- YouTube opportunity highlighting
- Bulk actions and CSV export

### YouTube Integration Hub
- Channel discovery testing interface
- Opportunity identification and categorization
- API status monitoring and quota tracking
- Growth potential analysis
- Integration setup guide

### Enhanced Settings Panel
- API configuration with testing capabilities
- System status overview with health indicators
- Processing preferences and customization
- Security and privacy information
- Comprehensive setup instructions

## 🔧 API Integration

### Updated API Client

The frontend uses a centralized API client with enhanced error handling:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};
```

### Backend Endpoints

The frontend integrates with these backend endpoints:

- `POST /api/analyze-isrc` - Single ISRC analysis
- `POST /api/analyze-bulk` - Bulk processing
- `GET /api/leads` - Lead management with filtering
- `POST /api/export` - Data export functionality
- `GET /api/youtube/*` - YouTube integration features
- `GET /api/status` - System status and health
- `GET /api/dashboard/stats` - Dashboard analytics

## 🚀 Deployment

### Production Build

```bash
# Create optimized production build
npm run build:production

# Test locally
npm run serve
```

### Environment Variables for Production

```env
REACT_APP_API_BASE_URL=https://isrc-analyzer-api.onrender.com/api
REACT_APP_VERSION=1.0.0
REACT_APP_PRISM_ENVIRONMENT=production
REACT_APP_DEBUG=false
```

### Deployment Platforms

#### Render (Recommended)
1. Connect GitHub repository
2. Set build command: `npm run build:production`
3. Set publish directory: `build`
4. Configure environment variables

#### Vercel
1. Import from GitHub
2. Framework preset: Create React App
3. Build command: `npm run build:production`
4. Output directory: `build`

#### Netlify
1. Connect repository
2. Build command: `npm run build:production`
3. Publish directory: `build`
4. Set environment variables

## 🔒 Security & Performance

### Security Features

- No sensitive data stored in frontend
- API keys managed server-side
- HTTPS enforcement in production
- Content Security Policy headers
- XSS protection with input validation

### Performance Optimizations

- **Code Splitting**: Lazy loading of components
- **Image Optimization**: WebP format with fallbacks
- **Caching**: Aggressive caching of static assets
- **Bundle Analysis**: Regular bundle size monitoring
- **Progressive Loading**: Enhanced loading experience

### Performance Targets

- **First Contentful Paint**: < 2s
- **Largest Contentful Paint**: < 3s
- **Time to Interactive**: < 5s
- **Lighthouse Score**: 90+

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

3. **Triangular Prism Loading Not Showing**
   ```bash
   # Check CSS animations are enabled
   # Verify SVG elements are properly loaded
   ```

4. **Styling Issues**
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

## 📈 Monitoring & Analytics

### Performance Monitoring

- Integrated Web Vitals tracking
- Error boundary implementation
- API response time monitoring
- Bundle size tracking
- User interaction analytics

### Health Checks

- API connectivity status
- Feature flag monitoring
- Error rate tracking
- Performance metrics collection

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with triangular prism theming in mind
4. Commit changes (`git commit -m 'Add triangular prism loading animation'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

### Code Standards

- Follow existing Prism design patterns
- Maintain triangular prism visual consistency
- Add tests for new features
- Update documentation
- Ensure accessibility compliance
- Test across browsers

### Design Guidelines

- Use triangular prism elements where appropriate
- Maintain Prism color palette consistency
- Implement smooth animations and transitions
- Ensure responsive design works on all devices
- Follow accessibility best practices

## 🎯 Future Enhancements

### Planned Features

- **Advanced Visualizations**: 3D data representations with triangular prism themes
- **Real-time Collaboration**: Multi-user lead management
- **Mobile App**: React Native implementation
- **AI Integration**: Machine learning-powered lead scoring
- **Advanced Analytics**: Deeper insights and reporting

### Performance Improvements

- **Service Worker**: Offline functionality
- **PWA Features**: Install prompts and app-like experience
- **Edge Caching**: CDN integration for global performance
- **Micro-frontends**: Modular architecture for scalability

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.