import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Database, 
  Upload, 
  BarChart3, 
  Youtube,
  Settings as SettingsIcon
} from 'lucide-react';

// Import components
import Dashboard from './components/Dashboard';
import ISRCAnalyzer from './components/ISRCAnalyzer';
import BulkProcessor from './components/BulkProcessor';
import LeadsList from './components/LeadsList';
import YouTubeIntegration from './components/YouTubeIntegration';
import Settings from './components/Settings';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

// Utility function for API calls
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

const App = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeRoute, setActiveRoute] = useState('dashboard');

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const status = await apiCall('/status');
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, component: Dashboard },
    { id: 'analyze', label: 'ISRC Analyzer', icon: Search, component: ISRCAnalyzer },
    { id: 'bulk', label: 'Bulk Processing', icon: Upload, component: BulkProcessor },
    { id: 'leads', label: 'Leads Database', icon: Database, component: LeadsList },
    { id: 'youtube', label: 'YouTube Integration', icon: Youtube, component: YouTubeIntegration },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, component: Settings },
  ];

  const renderActiveComponent = () => {
    const activeItem = navigationItems.find(item => item.id === activeRoute);
    if (!activeItem) return <Dashboard systemStatus={systemStatus} />;
    
    const Component = activeItem.component;
    return <Component systemStatus={systemStatus} />;
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
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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

      <div className="flex">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-white shadow-sm min-h-screen border-r border-gray-200">
          <div className="p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveRoute(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left tracking-wide ${
                      activeRoute === item.id
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

          {/* API Status Panel */}
          {systemStatus && (
            <div className="p-4 border-t border-gray-200">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-3">
                API STATUS
              </h3>
              <div className="space-y-2">
                {Object.entries(systemStatus.rate_limits || {}).map(([api, status]) => (
                  <div key={api} className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 capitalize tracking-wide">{api.toUpperCase()}</span>
                    <span className={`font-medium font-mono ${
                      status.minute_remaining > 10 ? 'text-green-600' : 
                      status.minute_remaining > 0 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {status.minute_remaining}/{status.minute_limit}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prism Branding Footer */}
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

        {/* Main Content */}
        <main className="flex-1 p-6 bg-white">
          {renderActiveComponent()}
        </main>
      </div>
    </div>
  );
};

export default App;