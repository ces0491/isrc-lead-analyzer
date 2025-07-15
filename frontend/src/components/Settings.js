import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Key, 
  Database, 
  Zap, 
  Shield, 
  Youtube,
  Music,
  Globe,
  AlertCircle,
  CheckCircle,
  Save,
  RefreshCw,
  Eye,
  EyeOff,
  Info,
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';

const Settings = ({ systemStatus }) => {
  const [databaseStatus, setDatabaseStatus] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState(false);
  const [copiedKey, setCopiedKey] = useState('');

  useEffect(() => {
    fetchDatabaseStatus();
    fetchApiStatus();
  }, []);

  const fetchDatabaseStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      
      // Extract database info from system status
      setDatabaseStatus({
        status: data.database_status || 'unknown',
        database_type: data.database_type || 'Unknown',
        connected: data.database_status === 'connected',
        database_url_masked: data.database_url_masked,
        version_info: data.database_version,
        error: data.database_error
      });
    } catch (error) {
      console.error('Failed to fetch database status:', error);
      setDatabaseStatus({
        status: 'error',
        database_type: 'Unknown',
        connected: false,
        error: 'Failed to fetch status'
      });
    }
  };

  const fetchApiStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setApiStatus(data.rate_limits || {});
    } catch (error) {
      console.error('Failed to fetch API status:', error);
      setApiStatus({});
    } finally {
      setLoading(false);
    }
  };

  const testApiIntegration = async (apiName) => {
    setTesting(true);
    setTestResults(prev => ({ ...prev, [apiName]: { status: 'testing' } }));

    try {
      let response;
      
      switch (apiName) {
        case 'youtube':
          response = await fetch('/api/youtube/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist_name: 'Test Artist' })
          });
          break;
        
        case 'spotify':
          response = await fetch('/api/analyze-isrc', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              isrc: 'USRC17607839', 
              save_to_db: false,
              include_youtube: false 
            })
          });
          break;
        
        case 'lastfm':
          response = await fetch('/api/lastfm/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist_name: 'Test Artist' })
          });
          break;
        
        case 'musicbrainz':
          response = await fetch('/api/musicbrainz/test', {
            method: 'POST'
          });
          break;
        
        case 'database':
          response = await fetch('/api/database/test', {
            method: 'POST'
          });
          break;
        
        default:
          throw new Error(`No test available for ${apiName}`);
      }

      const data = await response.json();
      
      setTestResults(prev => ({
        ...prev,
        [apiName]: {
          status: response.ok ? 'success' : 'error',
          message: response.ok ? 
            (data.message || 'Test completed successfully') : 
            (data.error || 'Test failed'),
          data: data
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [apiName]: {
          status: 'error',
          message: error.message || 'Connection failed'
        }
      }));
    } finally {
      setTesting(false);
    }
  };

  const copyToClipboard = async (text, key) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(''), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const refreshAllStatus = async () => {
    setLoading(true);
    await Promise.all([
      fetchDatabaseStatus(),
      fetchApiStatus()
    ]);
    setLoading(false);
  };

  const getApiStatusColor = (status) => {
    if (!status) return 'text-gray-500';
    
    // For YouTube, check quota usage
    if (status.quota_limit_daily) {
      const percentage = (status.quota_used_today / status.quota_limit_daily) * 100;
      if (percentage > 90) return 'text-red-600';
      if (percentage > 70) return 'text-yellow-600';
      return 'text-green-600';
    }
    
    // For other APIs, check per-minute usage
    const remaining = status.minute_remaining || 0;
    const limit = status.minute_limit || 1;
    const percentage = (remaining / limit) * 100;
    
    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading settings...</p>
      </div>
    );
  }

  const apiConfigurations = [
    {
      name: 'YouTube Data API v3',
      key: 'youtube',
      icon: Youtube,
      color: 'text-red-500',
      description: 'Channel analytics and video data for opportunity identification',
      required: false,
      configured: Boolean(systemStatus?.youtube_integration?.api_key_configured),
      status: apiStatus?.youtube,
      envVar: 'YOUTUBE_API_KEY',
      setupUrl: 'https://console.developers.google.com/'
    },
    {
      name: 'Spotify Web API',
      key: 'spotify',
      icon: Music,
      color: 'text-green-500',
      description: 'Artist and track metadata from Spotify',
      required: true,
      configured: Boolean(apiStatus?.spotify?.configured),
      status: apiStatus?.spotify,
      envVar: 'SPOTIFY_CLIENT_ID & SPOTIFY_CLIENT_SECRET',
      setupUrl: 'https://developer.spotify.com/dashboard/applications'
    },
    {
      name: 'Last.fm API',
      key: 'lastfm',
      icon: Globe,
      color: 'text-red-600',
      description: 'Social listening data and music trends',
      required: false,
      configured: Boolean(apiStatus?.lastfm?.configured),
      status: apiStatus?.lastfm,
      envVar: 'LASTFM_API_KEY',
      setupUrl: 'https://www.last.fm/api/account/create'
    },
    {
      name: 'MusicBrainz',
      key: 'musicbrainz',
      icon: Database,
      color: 'text-gray-600',
      description: 'Open music metadata database (no API key required)',
      required: true,
      configured: true,
      status: apiStatus?.musicbrainz,
      envVar: 'None required',
      setupUrl: 'https://musicbrainz.org/'
    }
  ];

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center tracking-wide">
            <SettingsIcon className="h-8 w-8 mr-3 text-gray-600" />
            SETTINGS
          </h2>
          <p className="text-gray-600">Configure API integrations and system settings for Prism Analytics Engine</p>
        </div>
        <button
          onClick={refreshAllStatus}
          className="flex items-center px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium tracking-wide"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          REFRESH STATUS
        </button>
      </div>

      {/* Database Configuration */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center tracking-wide">
          <Database className="h-5 w-5 mr-2 text-blue-500" />
          DATABASE CONFIGURATION
        </h3>
        
        {databaseStatus ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className={`h-4 w-4 rounded-full mx-auto mb-2 ${
                  databaseStatus.connected ? 'bg-green-400' : 'bg-red-400'
                }`}></div>
                <div className="text-sm font-medium text-gray-900 tracking-wide">CONNECTION STATUS</div>
                <div className="text-xs text-gray-600">
                  {databaseStatus.connected ? 'Connected' : 'Disconnected'}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900 mb-1">
                  {databaseStatus.database_type}
                </div>
                <div className="text-sm font-medium text-gray-900 tracking-wide">DATABASE TYPE</div>
                <div className="text-xs text-gray-600">
                  {databaseStatus.version_info ? 
                    databaseStatus.version_info.substring(0, 30) + '...' : 
                    'Version unknown'
                  }
                </div>
              </div>
              
              <div className="text-center">
                <button
                  onClick={() => testApiIntegration('database')}
                  disabled={testing}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium tracking-wide"
                >
                  {testing && testResults.database?.status === 'testing' ? 'TESTING...' : 'TEST CONNECTION'}
                </button>
                <div className="text-sm font-medium text-gray-900 tracking-wide mt-1">CONNECTION TEST</div>
              </div>
            </div>

            {databaseStatus.database_url_masked && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <div className="text-sm">
                  <span className="font-medium text-gray-900">Connection URL:</span>
                  <div className="mt-1 flex items-center">
                    <code className="text-xs text-gray-700 bg-white px-2 py-1 rounded border font-mono">
                      {databaseStatus.database_url_masked}
                    </code>
                    <button
                      onClick={() => copyToClipboard(databaseStatus.database_url_masked, 'db_url')}
                      className="ml-2 p-1 text-gray-500 hover:text-gray-700"
                    >
                      {copiedKey === 'db_url' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {databaseStatus.error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center text-red-800">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  <span className="font-medium">Connection Error:</span>
                </div>
                <div className="text-sm text-red-600 mt-1">{databaseStatus.error}</div>
              </div>
            )}

            {/* Database Test Result */}
            {testResults.database && (
              <div className={`p-3 rounded-lg ${
                testResults.database.status === 'success' ? 'bg-green-50 border border-green-200' :
                testResults.database.status === 'error' ? 'bg-red-50 border border-red-200' :
                'bg-yellow-50 border border-yellow-200'
              }`}>
                <div className="flex items-center">
                  {testResults.database.status === 'success' ? (
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  ) : testResults.database.status === 'error' ? (
                    <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                  ) : (
                    <RefreshCw className="h-4 w-4 text-yellow-500 mr-2 animate-spin" />
                  )}
                  <span className={`text-sm font-medium ${
                    testResults.database.status === 'success' ? 'text-green-800' :
                    testResults.database.status === 'error' ? 'text-red-800' :
                    'text-yellow-800'
                  }`}>
                    {testResults.database.message}
                  </span>
                </div>
              </div>
            )}

            {/* Database Configuration Guide */}
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <Info className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
                <div className="text-sm text-blue-700">
                  <div className="font-medium mb-2 tracking-wide">DATABASE CONFIGURATION:</div>
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="font-medium">For PostgreSQL:</span>
                      <code className="block bg-white px-2 py-1 rounded mt-1 font-mono">
                        DATABASE_URL=postgresql://user:password@host:port/database
                      </code>
                    </div>
                    <div>
                      <span className="font-medium">For SQLite (current):</span>
                      <code className="block bg-white px-2 py-1 rounded mt-1 font-mono">
                        DATABASE_URL=sqlite:///data/leads.db
                      </code>
                    </div>
                    <div className="text-blue-600">
                      SQLite is suitable for development and small deployments. 
                      For production with multiple users, consider PostgreSQL.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Database className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Database status unavailable</p>
          </div>
        )}
      </div>

      {/* System Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center tracking-wide">
          <Zap className="h-5 w-5 mr-2 text-red-600" />
          SYSTEM OVERVIEW
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className={`h-3 w-3 rounded-full mx-auto mb-2 ${
              databaseStatus?.connected ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
            <div className="text-sm font-medium text-gray-900 tracking-wide">DATABASE</div>
            <div className="text-xs text-gray-600">
              {databaseStatus?.connected ? 'Connected' : 'Disconnected'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {databaseStatus?.database_type || 'Unknown'}
            </div>
          </div>
          
          <div className="text-center">
            <div className={`h-3 w-3 rounded-full mx-auto mb-2 ${
              systemStatus?.youtube_integration?.api_key_configured ? 'bg-green-400' : 'bg-yellow-400'
            }`}></div>
            <div className="text-sm font-medium text-gray-900 tracking-wide">YOUTUBE API</div>
            <div className="text-xs text-gray-600">
              {systemStatus?.youtube_integration?.api_key_configured ? 'Configured' : 'Available'}
            </div>
          </div>
          
          <div className="text-center">
            <div className="h-3 w-3 rounded-full bg-green-400 mx-auto mb-2"></div>
            <div className="text-sm font-medium text-gray-900 tracking-wide">PROCESSING ENGINE</div>
            <div className="text-xs text-gray-600">Active</div>
          </div>
        </div>
      </div>

      {/* API Configurations */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center tracking-wide">
            <Key className="h-5 w-5 mr-2 text-yellow-500" />
            API INTEGRATIONS
          </h3>
          <div className="flex items-center space-x-4">
            <div className="text-xs text-gray-500">
              Rate limits show current usage vs limits
            </div>
            <button
              onClick={() => setShowApiKeys(!showApiKeys)}
              className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              {showApiKeys ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
              {showApiKeys ? 'Hide' : 'Show'} Details
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {apiConfigurations.map((api) => {
            const Icon = api.icon;
            const testResult = testResults[api.key];
            
            return (
              <div key={api.key} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Icon className={`h-6 w-6 mr-3 ${api.color}`} />
                    <div>
                      <div className="font-medium text-gray-900 flex items-center tracking-wide">
                        {api.name.toUpperCase()}
                        {api.required && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            REQUIRED
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">{api.description}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    {api.configured ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    )}
                    
                    <button
                      onClick={() => testApiIntegration(api.key)}
                      disabled={testing || (api.key !== 'musicbrainz' && !api.configured)}
                      className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium tracking-wide"
                    >
                      {testing && testResult?.status === 'testing' ? 'TESTING...' : 'TEST'}
                    </button>
                  </div>
                </div>

                {/* API Status Details */}
                {api.status && showApiKeys && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-sm">
                    {/* Current Usage */}
                    <div>
                      <span className="text-gray-600">Current Usage:</span>
                      <div className={`font-medium font-mono ${getApiStatusColor(api.status)}`}>
                        {api.key === 'youtube' && api.status.quota_limit_daily ? 
                          `${api.status.quota_used_today || 0}/${api.status.quota_limit_daily} quota` :
                          `${api.status.requests_this_minute || 0}/${api.status.minute_limit || 0} per minute`
                        }
                      </div>
                    </div>
                    
                    {/* Today's Requests */}
                    <div>
                      <span className="text-gray-600">Today's Requests:</span>
                      <span className="ml-2 font-medium font-mono text-gray-900">
                        {api.status.requests_today || 0}
                      </span>
                    </div>
                    
                    {/* Status */}
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <span className={`ml-2 font-medium ${api.configured ? 'text-green-600' : 'text-red-600'}`}>
                        {api.configured ? 'Active' : 'Not Configured'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Test Results */}
                {testResult && (
                  <div className={`p-3 rounded-lg mb-4 ${
                    testResult.status === 'success' ? 'bg-green-50 border border-green-200' :
                    testResult.status === 'error' ? 'bg-red-50 border border-red-200' :
                    'bg-yellow-50 border border-yellow-200'
                  }`}>
                    <div className="flex items-center">
                      {testResult.status === 'success' ? (
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      ) : testResult.status === 'error' ? (
                        <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                      ) : (
                        <RefreshCw className="h-4 w-4 text-yellow-500 mr-2 animate-spin" />
                      )}
                      <span className={`text-sm font-medium ${
                        testResult.status === 'success' ? 'text-green-800' :
                        testResult.status === 'error' ? 'text-red-800' :
                        'text-yellow-800'
                      }`}>
                        {testResult.message}
                      </span>
                    </div>
                  </div>
                )}

                {/* Configuration Instructions */}
                {!api.configured && showApiKeys && api.key !== 'musicbrainz' && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-700">
                      <div className="font-medium mb-2 tracking-wide flex items-center">
                        <Info className="h-4 w-4 mr-2" />
                        SETUP INSTRUCTIONS:
                      </div>
                      <ol className="list-decimal list-inside space-y-1 text-xs">
                        <li>
                          Go to{' '}
                          <a 
                            href={api.setupUrl} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="text-red-600 hover:underline inline-flex items-center"
                          >
                            {api.setupUrl.replace('https://', '')}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </li>
                        {api.key === 'youtube' && (
                          <>
                            <li>Create a project or select existing one</li>
                            <li>Enable "YouTube Data API v3"</li>
                            <li>Create credentials (API Key)</li>
                            <li>Set <code className="bg-white px-1 rounded">YOUTUBE_API_KEY</code> environment variable</li>
                          </>
                        )}
                        {api.key === 'spotify' && (
                          <>
                            <li>Create a new application</li>
                            <li>Copy Client ID and Client Secret</li>
                            <li>Set <code className="bg-white px-1 rounded">SPOTIFY_CLIENT_ID</code> and <code className="bg-white px-1 rounded">SPOTIFY_CLIENT_SECRET</code> environment variables</li>
                          </>
                        )}
                        {api.key === 'lastfm' && (
                          <>
                            <li>Create an account and request API key</li>
                            <li>Set <code className="bg-white px-1 rounded">LASTFM_API_KEY</code> environment variable</li>
                          </>
                        )}
                        <li>Restart the application to apply changes</li>
                      </ol>
                      
                      <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                        <strong>Environment Variable:</strong> {api.envVar}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Environment Variables Reference */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">ENVIRONMENT VARIABLES REFERENCE</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3 tracking-wide">DATABASE</h4>
            <div className="space-y-2 text-sm font-mono">
              <div className="p-2 bg-gray-50 rounded">
                <div className="text-gray-600">SQLite (current):</div>
                <code className="text-xs">DATABASE_URL=sqlite:///data/leads.db</code>
              </div>
              <div className="p-2 bg-gray-50 rounded">
                <div className="text-gray-600">PostgreSQL:</div>
                <code className="text-xs">DATABASE_URL=postgresql://user:pass@host:5432/db</code>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-3 tracking-wide">API KEYS</h4>
            <div className="space-y-2 text-sm font-mono">
              <div className="p-2 bg-gray-50 rounded">
                <code className="text-xs">YOUTUBE_API_KEY=your_key_here</code>
              </div>
              <div className="p-2 bg-gray-50 rounded">
                <code className="text-xs">SPOTIFY_CLIENT_ID=your_id_here</code>
                <br />
                <code className="text-xs">SPOTIFY_CLIENT_SECRET=your_secret_here</code>
              </div>
              <div className="p-2 bg-gray-50 rounded">
                <code className="text-xs">LASTFM_API_KEY=your_key_here</code>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">SYSTEM INFORMATION</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Application Version:</span>
            <span className="ml-2 font-medium font-mono">1.0.0</span>
          </div>
          <div>
            <span className="text-gray-600">Database Type:</span>
            <span className="ml-2 font-medium">{databaseStatus?.database_type || 'Unknown'}</span>
          </div>
          <div>
            <span className="text-gray-600">YouTube Integration:</span>
            <span className="ml-2 font-medium">
              {systemStatus?.youtube_integration?.api_key_configured ? 'Enabled' : 'Available'}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Last Updated:</span>
            <span className="ml-2 font-medium font-mono">
              {new Date().toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;