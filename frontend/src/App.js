import React, { useState, useEffect, useCallback } from 'react';
import { 
  Music, 
  Search, 
  Database, 
  Upload, 
  Download, 
  BarChart3, 
  Youtube,
  Settings,
  Users,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Play,
  Pause,
  FileText,
  Filter,
  Eye,
  EyeOff,
  Mail,
  Globe,
  ExternalLink,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Key,
  Zap,
  Shield,
  Save
} from 'lucide-react';

// API Configuration for separate deployment
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

// ISRC Analyzer Logo Component (updated from Prism)
const ISRCAnalyzerLogo = ({ className = "h-8 w-8" }) => (
  <div className={`${className} flex items-center justify-center`}>
    <svg viewBox="0 0 100 100" className="w-full h-full">
      {/* Musical notation lines */}
      <g className="opacity-60">
        <line x1="10" y1="20" x2="35" y2="20" stroke="#1A1A1A" strokeWidth="1"/>
        <line x1="10" y1="25" x2="35" y2="25" stroke="#1A1A1A" strokeWidth="1"/>
        <line x1="10" y1="30" x2="35" y2="30" stroke="#1A1A1A" strokeWidth="1"/>
        <circle cx="15" cy="22.5" r="1.5" fill="#1A1A1A"/>
        <circle cx="25" cy="27.5" r="1.5" fill="#1A1A1A"/>
      </g>
      
      {/* Triangular prism (keeping Prism visual identity) */}
      <path 
        d="M40 25 L65 40 L65 65 L40 50 Z" 
        fill="#1A1A1A" 
        stroke="#E50914" 
        strokeWidth="2"
      />
      <path 
        d="M40 25 L60 10 L85 25 L65 40 Z" 
        fill="#333333" 
        stroke="#E50914" 
        strokeWidth="2"
      />
      <path 
        d="M65 40 L85 25 L85 50 L65 65 Z" 
        fill="#666666" 
        stroke="#E50914" 
        strokeWidth="2"
      />
      
      {/* Sin wave output */}
      <path 
        d="M85 25 Q90 20 95 25 Q100 30 105 25" 
        stroke="#E50914" 
        strokeWidth="2" 
        fill="none"
      />
      <path 
        d="M85 35 Q90 30 95 35 Q100 40 105 35" 
        stroke="#E50914" 
        strokeWidth="2" 
        fill="none"
      />
      <path 
        d="M85 45 Q90 40 95 45 Q100 50 105 45" 
        stroke="#E50914" 
        strokeWidth="2" 
        fill="none"
      />
    </svg>
  </div>
);

const Dashboard = ({ systemStatus }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const data = await apiCall('/dashboard/stats');
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2 tracking-wide">DASHBOARD</h2>
        <p className="text-gray-600">Overview of your lead generation activities</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">TOTAL ARTISTS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.total_artists || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">A-TIER LEADS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.tier_distribution?.A || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Youtube className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">YOUTUBE CHANNELS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.youtube_statistics?.artists_with_youtube || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BarChart3 className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">AVG. SCORE</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats ? Math.round(
                  (stats.tier_distribution?.A * 85 + 
                   stats.tier_distribution?.B * 65 + 
                   stats.tier_distribution?.C * 45 + 
                   stats.tier_distribution?.D * 25) / 
                  Math.max(stats.total_artists, 1)
                ) : 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* YouTube Integration Status */}
      {systemStatus?.youtube_integration && (
        <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <Youtube className="h-6 w-6 text-red-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 tracking-wide">YOUTUBE INTEGRATION</h3>
              <p className="text-sm text-gray-600 mt-1">
                {systemStatus.youtube_integration.api_key_configured ? (
                  <>
                    <span className="text-green-600 font-medium">Active</span> - 
                    Quota used today: <span className="font-mono">{systemStatus.youtube_integration.daily_quota_used || 0}</span> / <span className="font-mono">{systemStatus.youtube_integration.daily_quota_limit || 10000}</span>
                  </>
                ) : (
                  <span className="text-red-600 font-medium">Configure YouTube API key to enable YouTube features</span>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">LEAD DISTRIBUTION BY TIER</h3>
        <div className="space-y-3">
          {['A', 'B', 'C', 'D'].map(tier => {
            const count = stats?.tier_distribution?.[tier] || 0;
            const total = stats?.total_artists || 1;
            const percentage = (count / total) * 100;
            
            return (
              <div key={tier} className="flex items-center">
                <div className="w-16 text-sm font-medium text-gray-600 tracking-wide">TIER {tier}</div>
                <div className="flex-1 mx-4">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        tier === 'A' ? 'bg-green-500' :
                        tier === 'B' ? 'bg-red-600' :
                        tier === 'C' ? 'bg-yellow-500' : 'bg-gray-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-sm text-gray-600 text-right font-mono">
                  {count} ({percentage.toFixed(1)}%)
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const ISRCAnalyzer = () => {
  const [isrc, setIsrc] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [includeYoutube, setIncludeYoutube] = useState(true);

  const analyzeISRC = async () => {
    if (!isrc.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const data = await apiCall('/analyze-isrc', {
        method: 'POST',
        body: JSON.stringify({ 
          isrc: isrc.trim(), 
          save_to_db: true,
          include_youtube: includeYoutube 
        })
      });
      
      setResult(data);
    } catch (error) {
      console.error('Failed to analyze ISRC:', error);
      setResult({ status: 'error', error: 'Failed to analyze ISRC' });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      analyzeISRC();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2 tracking-wide">ISRC ANALYZER</h2>
        <p className="text-gray-600">Analyze individual tracks and discover lead opportunities</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="isrc" className="block text-sm font-medium text-gray-900 mb-2 tracking-wide">
              ISRC CODE
            </label>
            <input
              type="text"
              id="isrc"
              value={isrc}
              onChange={(e) => setIsrc(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., USRC17607839"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 font-mono"
            />
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeYoutube}
                onChange={(e) => setIncludeYoutube(e.target.checked)}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600">Include YouTube data collection</span>
            </label>
          </div>

          <button
            onClick={analyzeISRC}
            disabled={loading || !isrc.trim()}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ANALYZING...
              </div>
            ) : (
              'ANALYZE ISRC'
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">ANALYSIS RESULTS</h3>
          
          {result.status === 'completed' ? (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 tracking-wide">ARTIST INFORMATION</h4>
                  <p className="text-lg font-semibold text-red-600">
                    {result.artist_data?.name || 'Unknown Artist'}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.track_data?.title || 'Unknown Track'}
                  </p>
                  <p className="text-sm text-gray-700 font-mono">
                    Label: {result.track_data?.label || 'Unknown'}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2 tracking-wide">LEAD SCORE</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-3xl font-bold text-gray-900 font-mono">
                      {result.scores?.total_score || 0}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      result.scores?.tier === 'A' ? 'bg-green-100 text-green-800' :
                      result.scores?.tier === 'B' ? 'bg-red-100 text-red-800' :
                      result.scores?.tier === 'C' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      TIER {result.scores?.tier || 'D'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1 font-mono">
                    Confidence: {result.scores?.confidence || 0}%
                  </p>
                </div>
              </div>

              {/* Score Breakdown */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3 tracking-wide">SCORE BREAKDOWN</h4>
                <div className="space-y-2">
                  {[
                    { label: 'Independence', score: result.scores?.independence_score, color: 'bg-red-600' },
                    { label: 'Opportunity', score: result.scores?.opportunity_score, color: 'bg-green-500' },
                    { label: 'Geographic', score: result.scores?.geographic_score, color: 'bg-gray-600' }
                  ].map(({ label, score, color }) => (
                    <div key={label} className="flex items-center">
                      <div className="w-24 text-sm text-gray-600 tracking-wide">{label.toUpperCase()}</div>
                      <div className="flex-1 mx-4">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${color}`}
                            style={{ width: `${score || 0}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-12 text-sm text-gray-600 text-right font-mono">{score || 0}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* YouTube Integration Results */}
              {result.youtube_integration?.enabled && (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Youtube className="h-4 w-4 mr-2 text-red-600" />
                    YOUTUBE ANALYSIS
                  </h4>
                  {result.youtube_integration.data_found ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-sm text-green-600 font-medium mb-2">✅ YouTube channel found!</p>
                      <p className="text-xs text-gray-600">
                        YouTube data has been integrated into the opportunity scoring.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-yellow-700 font-medium mb-1">
                        ⚠️ No YouTube channel found
                      </p>
                      <p className="text-xs text-gray-600">
                        This represents a significant YouTube opportunity for the artist.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Data Sources */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-2 tracking-wide">DATA SOURCES</h4>
                <div className="flex flex-wrap gap-2">
                  {result.data_sources_used?.map(source => (
                    <span key={source} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-900">
                      {source === 'youtube' ? (
                        <Youtube className="h-3 w-3 mr-1 text-red-500" />
                      ) : null}
                      {source.charAt(0).toUpperCase() + source.slice(1)}
                    </span>
                  )) || []}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
              <p className="text-red-600 font-medium">Analysis Failed</p>
              <p className="text-sm text-gray-600">{result.error || 'Unknown error occurred'}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Continue with other components (BulkProcessor, LeadsList, etc.) 
// but with updated branding and API calls...

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
    // Add other components here...
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
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ISRC Analyzer...</p>
        </div>
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
              <ISRCAnalyzerLogo className="h-10 w-10" />
              <div>
                <h1 className="text-xl font-bold text-gray-900 tracking-wider">
                  ISRC ANALYZER
                  <span className="text-xs text-gray-600 ml-2 font-normal tracking-normal">
                    BY PRECISE DIGITAL
                  </span>
                </h1>
                <p className="text-sm text-gray-600">
                  Lead generation for independent music services
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

          {/* ISRC Analyzer Branding Footer */}
          <div className="absolute bottom-4 left-4 right-4">
            <div className="text-center">
              <ISRCAnalyzerLogo className="h-6 w-6 mx-auto mb-2 opacity-60" />
              <p className="text-xs text-gray-700 tracking-wider">
                PRECISE DIGITAL
              </p>
              <p className="text-xs text-gray-500">
                ISRC Analyzer v1.0
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