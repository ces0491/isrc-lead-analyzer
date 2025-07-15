import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { 
  Search, 
  Database, 
  Upload, 
  BarChart3, 
  Youtube,
  Settings as SettingsIcon,
  FileText
} from 'lucide-react';

// Import components
import Dashboard from './components/Dashboard';
import ISRCAnalyzer from './components/ISRCAnalyzer';
import BulkProcessor from './components/BulkProcessor';
import LeadsList from './components/LeadsList';
import YouTubeIntegration from './components/YouTubeIntegration';
import Settings from './components/Settings';
import TrackAnalysisPage from './components/TrackAnalysisPage';

// API Configuration
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

// Prism Analytics Engine Logo Component with Triangular Prism
const PrismLogo = ({ className = "h-8 w-8", animated = false }) => (
  <div className={`${className} flex items-center justify-center`}>
    <svg viewBox="0 0 100 40" className="w-full h-full">
      {/* Musical notation lines - representing raw music data */}
      <g>
        <line x1="2" y1="12" x2="18" y2="12" stroke="#1A1A1A" strokeWidth="1"/>
        <line x1="2" y1="16" x2="18" y2="16" stroke="#1A1A1A" strokeWidth="1"/>
        <line x1="2" y1="20" x2="18" y2="20" stroke="#1A1A1A" strokeWidth="1"/>
        <line x1="2" y1="24" x2="18" y2="24" stroke="#1A1A1A" strokeWidth="1"/>
        <line x1="2" y1="28" x2="18" y2="28" stroke="#1A1A1A" strokeWidth="1"/>
        {/* Musical notes */}
        <circle cx="6" cy="14" r="1" fill="#1A1A1A"/>
        <circle cx="12" cy="22" r="1" fill="#1A1A1A"/>
        <circle cx="16" cy="18" r="1" fill="#1A1A1A"/>
      </g>
      
      {/* Triangular prism - 3D appearance */}
      <g className={animated ? "animate-pulse" : ""}>
        {/* Front face - main triangle */}
        <path 
          d="M30 28 L40 12 L50 28 Z" 
          fill="#1A1A1A" 
          stroke="#E50914" 
          strokeWidth="1"
        />
        {/* Back face - offset triangle */}
        <path 
          d="M35 25 L45 9 L55 25 Z" 
          fill="#333333" 
          stroke="#E50914" 
          strokeWidth="1"
        />
        {/* Connecting edges to create 3D effect */}
        <line x1="30" y1="28" x2="35" y2="25" stroke="#E50914" strokeWidth="1"/>
        <line x1="40" y1="12" x2="45" y2="9" stroke="#E50914" strokeWidth="1"/>
        <line x1="50" y1="28" x2="55" y2="25" stroke="#E50914" strokeWidth="1"/>
        
        {/* Red accent line through center */}
        <line x1="35" y1="20" x2="45" y2="17" stroke="#E50914" strokeWidth="2"/>
      </g>
      
      {/* Sin wave output - representing refined insights */}
      <g className={animated ? "animate-pulse" : ""}>
        <path 
          d="M60 16 Q65 12 70 16 Q75 20 80 16 Q85 12 90 16 Q95 20 98 16" 
          stroke="#E50914" 
          strokeWidth="2" 
          fill="none"
        />
        <path 
          d="M60 24 Q65 20 70 24 Q75 28 80 24 Q85 20 90 24 Q95 28 98 24" 
          stroke="#E50914" 
          strokeWidth="2" 
          fill="none"
        />
      </g>
    </svg>
  </div>
);

// Loading Component with Triangular Prism
const PrismLoading = ({ message = "Loading..." }) => (
  <div className="text-center py-12">
    <PrismLogo className="h-16 w-32 mx-auto mb-4" animated={true} />
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto mb-4"></div>
    <p className="text-gray-600">{message}</p>
  </div>
);

// Rate Limit Display Component
const formatRateLimit = (api, status) => {
  if (!status) return { display: 'N/A', color: 'text-gray-500', description: 'Not configured' };

  const getUsageColor = (used, limit) => {
    const percentage = (used / limit) * 100;
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-green-600';
  };

  switch (api) {
    case 'musicbrainz':
      if (status.second_limit) {
        const used = status.requests_this_second || 0;
        const limit = status.second_limit;
        return {
          display: `${used}/${limit}/sec`,
          color: getUsageColor(used, limit),
          description: '1 request per second (respectful usage)'
        };
      }
      const usedMin = status.requests_this_minute || 0;
      const limitMin = status.minute_limit || 50;
      return {
        display: `${usedMin}/${limitMin}/min`,
        color: getUsageColor(usedMin, limitMin),
        description: '~50 requests per minute'
      };

    case 'spotify':
      const spotifyUsed = status.requests_this_minute || 0;
      const spotifyLimit = status.minute_limit || 100;
      return {
        display: `${spotifyUsed}/${spotifyLimit}/min`,
        color: getUsageColor(spotifyUsed, spotifyLimit),
        description: '~100 requests per minute (varies by endpoint)'
      };

    case 'youtube':
      if (status.quota_limit_daily) {
        const quotaUsed = status.quota_used_today || 0;
        const quotaLimit = status.quota_limit_daily;
        return {
          display: `${quotaUsed.toLocaleString()}/${quotaLimit.toLocaleString()}`,
          color: getUsageColor(quotaUsed, quotaLimit),
          description: 'Daily quota units (search=100, details=1)'
        };
      }
      return {
        display: 'Not configured',
        color: 'text-gray-500',
        description: 'YouTube API key not set'
      };

    case 'lastfm':
      if (status.second_limit) {
        const used = status.requests_this_second || 0;
        const limit = status.second_limit;
        return {
          display: `${used}/${limit}/sec`,
          color: getUsageColor(used, limit),
          description: '5 requests per second when authenticated'
        };
      }
      const lastfmUsedMin = status.requests_this_minute || 0;
      const lastfmLimitMin = status.minute_limit || 200;
      return {
        display: `${lastfmUsedMin}/${lastfmLimitMin}/min`,
        color: getUsageColor(lastfmUsedMin, lastfmLimitMin),
        description: '~200 requests per minute'
      };

    case 'discogs':
      if (status.second_limit) {
        const used = status.requests_this_second || 0;
        const limit = status.second_limit;
        return {
          display: `${used}/${limit}/sec`,
          color: getUsageColor(used, limit),
          description: '1 request per second, 60 per minute'
        };
      }
      const discogsUsedMin = status.requests_this_minute || 0;
      const discogsLimitMin = status.minute_limit || 60;
      return {
        display: `${discogsUsedMin}/${discogsLimitMin}/min`,
        color: getUsageColor(discogsUsedMin, discogsLimitMin),
        description: '60 requests per minute'
      };

    // Enhanced APIs
    case 'genius':
      const geniusUsedMin = status.requests_this_minute || 0;
      const geniusLimitMin = status.minute_limit || 100;
      return {
        display: `${geniusUsedMin}/${geniusLimitMin}/min`,
        color: getUsageColor(geniusUsedMin, geniusLimitMin),
        description: '100 requests per minute'
      };

    case 'musixmatch':
      const musixUsedMin = status.requests_this_minute || 0;
      const musixLimitMin = status.minute_limit || 20;
      return {
        display: `${musixUsedMin}/${musixLimitMin}/min`,
        color: getUsageColor(musixUsedMin, musixLimitMin),
        description: '20 requests per minute'
      };

    default:
      return {
        display: 'Unknown',
        color: 'text-gray-500',
        description: 'Unknown API'
      };
  }
};

// Navigation Component
const Navigation = ({ activeRoute, setActiveRoute, systemStatus }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, path: '/' },
    { id: 'analyze', label: 'ISRC Analyzer', icon: Search, path: '/analyze' },
    { id: 'track-analysis', label: 'Track Analysis', icon: FileText, path: '/track' },
    { id: 'bulk', label: 'Bulk Processing', icon: Upload, path: '/bulk' },
    { id: 'leads', label: 'Leads Database', icon: Database, path: '/leads' },
    { id: 'youtube', label: 'YouTube Integration', icon: Youtube, path: '/youtube' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' },
  ];

  const handleNavigation = (item) => {
    setActiveRoute(item.id);
    navigate(item.path);
  };

  // Determine active route based on current path
  const currentPath = location.pathname;
  const activeItem = navigationItems.find(item => {
    if (item.path === '/' && currentPath === '/') return true;
    if (item.path !== '/' && currentPath.startsWith(item.path)) return true;
    return false;
  }) || navigationItems[0];

  return (
    <nav className="fixed left-0 w-64 bg-white shadow-sm border-r border-gray-200 z-40 overflow-y-auto" 
         style={{ height: 'calc(100vh - 80px)', top: '80px' }}>
      <div className="p-4">
        <div className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeItem.id === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left tracking-wide ${
                  isActive
                    ? 'bg-red-50 text-red-600 border border-red-200'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label.toUpperCase()}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* API Rate Limits Panel */}
      {systemStatus?.rate_limits && (
        <div className="p-4 border-t border-gray-200">
          <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-3">
            API RATE LIMITS
          </h3>
          
          <div className="space-y-3">
            {Object.entries(systemStatus.rate_limits).map(([api, status]) => {
              const limitInfo = formatRateLimit(api, status);
              
              return (
                <div key={api} className="group relative">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 capitalize tracking-wide font-medium">
                      {api.toUpperCase()}
                    </span>
                    <span className={`font-medium font-mono ${limitInfo.color}`}>
                      {limitInfo.display}
                    </span>
                  </div>
                  
                  {/* Tooltip on hover */}
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 absolute left-0 top-full mt-1 z-50 bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap pointer-events-none">
                    {limitInfo.description}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-4 pt-3 border-t border-gray-100">
            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between text-gray-500">
                <span>Usage indicators:</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-500">Good</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-gray-500">High</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-gray-500">Limit</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Prism Branding Footer - Fixed at bottom */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="text-center">
          <PrismLogo className="h-8 w-16 mx-auto mb-2 opacity-60" />
          <p className="text-xs text-gray-700 tracking-widest">
            P R I S M
          </p>
          <p className="text-xs text-gray-500 tracking-wide">
            Analytics Engine v1.0
          </p>
          <p className="text-xs text-gray-500 mt-1">
            by Precise Digital
          </p>
        </div>
      </div>
    </nav>
  );
};

// Main App Content Component
const AppContent = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeRoute, setActiveRoute] = useState('dashboard');

  useEffect(() => {
    fetchSystemStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const status = await apiCall('/status');
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      // Set fallback status
      setSystemStatus({
        database_status: 'disconnected',
        youtube_integration: { status: 'unavailable', api_key_configured: false },
        rate_limits: {}
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <PrismLoading message="Loading Prism Analytics Engine..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 bg-white shadow-sm border-b border-gray-200 z-50">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <PrismLogo className="h-12 w-20" />
              <div>
                <h1 className="text-xl font-bold text-gray-900 tracking-widest">
                  P R I S M
                  <span className="text-xs text-gray-600 ml-3 font-normal tracking-normal">
                    ANALYTICS ENGINE
                  </span>
                </h1>
                <p className="text-sm text-gray-600">
                  Transforming music data into actionable insights
                </p>
              </div>
            </div>
            
            {/* System Status Indicator */}
            <div className="flex items-center space-x-4">
              {systemStatus && (
                <div className="flex items-center space-x-2">
                  <div className={`h-3 w-3 rounded-full ${
                    systemStatus.database_status === 'connected' ? 'bg-green-400' : 'bg-red-400'
                  }`}></div>
                  <span className="text-sm text-gray-600 font-mono">
                    {systemStatus.database_status === 'connected' ? 'SYSTEM ONLINE' : 'SYSTEM ISSUES'}
                  </span>
                  
                  {/* YouTube Integration Status */}
                  {systemStatus.youtube_integration && (
                    <div className="flex items-center space-x-1 ml-4">
                      <Youtube className={`h-4 w-4 ${
                        systemStatus.youtube_integration.status === 'available' 
                          ? 'text-red-500' 
                          : 'text-gray-500'
                      }`} />
                      <span className="text-xs text-gray-600 tracking-wide">
                        YOUTUBE {systemStatus.youtube_integration.api_key_configured ? 'ACTIVE' : 'DISABLED'}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout with Fixed Sidebar */}
      <div className="flex pt-20"> {/* Added top padding for fixed header */}
        {/* Fixed Sidebar Navigation */}
        <Navigation 
          activeRoute={activeRoute} 
          setActiveRoute={setActiveRoute} 
          systemStatus={systemStatus} 
        />

        {/* Main Content - Adjusted for fixed sidebar */}
        <main className="flex-1 ml-64 min-h-screen bg-white">
          <div className="p-6">
            <Routes>
              <Route path="/" element={<Dashboard systemStatus={systemStatus} />} />
              <Route path="/analyze" element={<ISRCAnalyzer systemStatus={systemStatus} />} />
              <Route path="/track" element={<TrackAnalysisPage />} />
              <Route path="/track/:isrc" element={<TrackAnalysisPage />} />
              <Route path="/bulk" element={<BulkProcessor systemStatus={systemStatus} />} />
              <Route path="/leads" element={<LeadsList systemStatus={systemStatus} />} />
              <Route path="/youtube" element={<YouTubeIntegration systemStatus={systemStatus} />} />
              <Route path="/settings" element={<Settings systemStatus={systemStatus} />} />
              {/* Catch-all route */}
              <Route path="*" element={<Dashboard systemStatus={systemStatus} />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
};

// Main App Component with Router
const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;