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
  EyeOff
} from 'lucide-react';

const Settings = () => {
  const [systemInfo, setSystemInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetchSystemInfo();
    fetchApiStatus();
  }, []);

  const fetchSystemInfo = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setSystemInfo(data);
    } catch (error) {
      console.error('Failed to fetch system info:', error);
    }
  };

  const fetchApiStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setApiStatus(data.rate_limits);
    } catch (error) {
      console.error('Failed to fetch API status:', error);
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
            body: JSON.stringify({ artist_name: 'test artist' })
          });
          break;
        case 'spotify':
          response = await fetch('/api/analyze-isrc', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ isrc: 'USRC17607839', save_to_db: false })
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
          message: response.ok ? 'API is working correctly' : data.error || 'Test failed',
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

  const getApiStatusColor = (status) => {
    if (!status) return 'text-prism-charcoal-gray';
    
    const remaining = status.minute_remaining || 0;
    const limit = status.minute_limit || 1;
    const percentage = (remaining / limit) * 100;
    
    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatApiKey = (key) => {
    if (!key) return 'Not configured';
    if (!showApiKeys) return '••••••••••••' + key.slice(-4);
    return key;
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-prism-red mx-auto mb-4"></div>
        <p className="text-prism-medium-gray">Loading settings...</p>
      </div>
    );
  }

  const apiConfigurations = [
    {
      name: 'YouTube Data API',
      key: 'youtube',
      icon: Youtube,
      color: 'text-red-500',
      description: 'Channel analytics and video data',
      required: false,
      configured: systemInfo?.youtube_integration?.api_key_configured || false,
      status: apiStatus?.youtube
    },
    {
      name: 'Spotify Web API',
      key: 'spotify',
      icon: Music,
      color: 'text-green-500',
      description: 'Artist and track metadata',
      required: true,
      configured: true,
      status: apiStatus?.spotify
    },
    {
      name: 'Last.fm API',
      key: 'lastfm',
      icon: Globe,
      color: 'text-prism-red',
      description: 'Social listening data',
      required: false,
      configured: apiStatus?.lastfm?.minute_limit > 0,
      status: apiStatus?.lastfm
    },
    {
      name: 'MusicBrainz',
      key: 'musicbrainz',
      icon: Database,
      color: 'text-prism-charcoal-gray',
      description: 'Open music metadata',
      required: true,
      configured: true,
      status: apiStatus?.musicbrainz
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-prism-black mb-2 flex items-center tracking-wide">
          <SettingsIcon className="h-8 w-8 mr-3 text-prism-charcoal-gray" />
          SETTINGS
        </h2>
        <p className="text-prism-medium-gray">Configure API integrations and system settings</p>
      </div>

      {/* System Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 flex items-center tracking-wide">
          <Zap className="h-5 w-5 mr-2 text-prism-red" />
          SYSTEM OVERVIEW
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className={`h-3 w-3 rounded-full mx-auto mb-2 ${
              systemInfo?.database_status === 'connected' ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
            <div className="text-sm font-medium text-prism-black tracking-wide">DATABASE</div>
            <div className="text-xs text-prism-medium-gray">
              {systemInfo?.database_status === 'connected' ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          
          <div className="text-center">
            <div className={`h-3 w-3 rounded-full mx-auto mb-2 ${
              systemInfo?.youtube_integration?.status === 'available' ? 'bg-green-400' : 'bg-yellow-400'
            }`}></div>
            <div className="text-sm font-medium text-prism-black tracking-wide">YOUTUBE INTEGRATION</div>
            <div className="text-xs text-prism-medium-gray">
              {systemInfo?.youtube_integration?.api_key_configured ? 'Configured' : 'Available'}
            </div>
          </div>
          
          <div className="text-center">
            <div className="h-3 w-3 rounded-full bg-green-400 mx-auto mb-2"></div>
            <div className="text-sm font-medium text-prism-black tracking-wide">PROCESSING ENGINE</div>
            <div className="text-xs text-prism-medium-gray">Active</div>
          </div>
        </div>
      </div>

      {/* API Configurations */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-prism-black flex items-center tracking-wide">
            <Key className="h-5 w-5 mr-2 text-yellow-500" />
            API INTEGRATIONS
          </h3>
          <button
            onClick={() => setShowApiKeys(!showApiKeys)}
            className="flex items-center text-sm text-prism-medium-gray hover:text-prism-black"
          >
            {showApiKeys ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
            {showApiKeys ? 'Hide' : 'Show'} API Keys
          </button>
        </div>

        <div className="space-y-4">
          {apiConfigurations.map((api) => {
            const Icon = api.icon;
            const testResult = testResults[api.key];
            
            return (
              <div key={api.key} className="border border-prism-light-gray rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <Icon className={`h-5 w-5 mr-3 ${api.color}`} />
                    <div>
                      <div className="font-medium text-prism-black flex items-center tracking-wide">
                        {api.name.toUpperCase()}
                        {api.required && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            REQUIRED
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-prism-medium-gray">{api.description}</div>
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
                      disabled={testing || !api.configured}
                      className="px-3 py-1 text-xs bg-prism-red text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide"
                    >
                      {testing && testResult?.status === 'testing' ? 'TESTING...' : 'TEST'}
                    </button>
                  </div>
                </div>

                {/* API Status */}
                {api.status && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3 text-sm">
                    <div>
                      <span className="text-prism-medium-gray">Rate Limit:</span>
                      <span className={`ml-2 font-medium font-mono ${getApiStatusColor(api.status)}`}>
                        {api.status.requests_this_minute || 0}/{api.status.minute_limit || 0} per minute
                      </span>
                    </div>
                    
                    {api.status.daily_limit && (
                      <div>
                        <span className="text-prism-medium-gray">Daily Usage:</span>
                        <span className="ml-2 font-medium text-prism-black font-mono">
                          {api.status.requests_today || 0}/{api.status.daily_limit}
                        </span>
                      </div>
                    )}
                    
                    <div>
                      <span className="text-prism-medium-gray">Status:</span>
                      <span className={`ml-2 font-medium ${api.configured ? 'text-green-600' : 'text-red-600'}`}>
                        {api.configured ? 'Active' : 'Not Configured'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Test Results */}
                {testResult && (
                  <div className={`p-3 rounded-md ${
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
                {!api.configured && (
                  <div className="mt-3 p-3 bg-prism-light-gray rounded-md">
                    <div className="text-sm text-prism-medium-gray">
                      <div className="font-medium mb-1 tracking-wide">SETUP INSTRUCTIONS:</div>
                      {api.key === 'youtube' && (
                        <ol className="list-decimal list-inside space-y-1 text-xs">
                          <li>Go to <a href="https://console.developers.google.com/" target="_blank" rel="noopener noreferrer" className="text-prism-red hover:underline">Google Cloud Console</a></li>
                          <li>Create a project or select existing one</li>
                          <li>Enable "YouTube Data API v3"</li>
                          <li>Create credentials (API Key)</li>
                          <li>Set YOUTUBE_API_KEY environment variable</li>
                        </ol>
                      )}
                      {api.key === 'lastfm' && (
                        <ol className="list-decimal list-inside space-y-1 text-xs">
                          <li>Go to <a href="https://www.last.fm/api/account/create" target="_blank" rel="noopener noreferrer" className="text-prism-red hover:underline">Last.fm API</a></li>
                          <li>Create an account and request API key</li>
                          <li>Set LASTFM_API_KEY environment variable</li>
                        </ol>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Processing Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 flex items-center tracking-wide">
          <SettingsIcon className="h-5 w-5 mr-2 text-prism-charcoal-gray" />
          PROCESSING SETTINGS
        </h3>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-prism-black mb-2 tracking-wide">
                DEFAULT BATCH SIZE
              </label>
              <select className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red">
                <option value="5">5 ISRCs per batch</option>
                <option value="10" selected>10 ISRCs per batch (Recommended)</option>
                <option value="20">20 ISRCs per batch</option>
              </select>
              <p className="text-xs text-prism-medium-gray mt-1">
                Smaller batches are more reliable but slower
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-prism-black mb-2 tracking-wide">
                YOUTUBE INTEGRATION
              </label>
              <select className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red">
                <option value="enabled" selected>Enabled by default</option>
                <option value="disabled">Disabled by default</option>
                <option value="ask">Ask user each time</option>
              </select>
              <p className="text-xs text-prism-medium-gray mt-1">
                Whether to include YouTube data collection by default
              </p>
            </div>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                defaultChecked
                className="h-4 w-4 text-prism-red focus:ring-prism-red border-prism-light-gray rounded"
              />
              <span className="ml-2 text-sm text-prism-medium-gray">
                Save all processed ISRCs to database
              </span>
            </label>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                defaultChecked
                className="h-4 w-4 text-prism-red focus:ring-prism-red border-prism-light-gray rounded"
              />
              <span className="ml-2 text-sm text-prism-medium-gray">
                Automatically discover contact information
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Security & Privacy */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 flex items-center tracking-wide">
          <Shield className="h-5 w-5 mr-2 text-green-500" />
          SECURITY & PRIVACY
        </h3>
        
        <div className="space-y-4 text-sm text-prism-medium-gray">
          <div className="p-3 bg-green-50 border border-green-200 rounded-md">
            <div className="font-medium text-green-800 mb-1">✅ Data Privacy</div>
            <ul className="list-disc list-inside space-y-1 text-green-700">
              <li>All data processing happens locally on your server</li>
              <li>API keys are stored securely in environment variables</li>
              <li>No sensitive data is transmitted to third parties</li>
              <li>Contact information is only collected from public sources</li>
            </ul>
          </div>
          
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div className="font-medium text-blue-800 mb-1">🔒 Security Features</div>
            <ul className="list-disc list-inside space-y-1 text-blue-700">
              <li>Rate limiting prevents API abuse</li>
              <li>Input validation protects against malicious data</li>
              <li>CORS protection limits unauthorized access</li>
              <li>Database access is protected by authentication</li>
            </ul>
          </div>

          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="font-medium text-yellow-800 mb-1">⚠️ Best Practices</div>
            <ul className="list-disc list-inside space-y-1 text-yellow-700">
              <li>Keep API keys confidential and rotate regularly</li>
              <li>Monitor API usage to avoid quota limits</li>
              <li>Backup your database regularly</li>
              <li>Use ethical outreach practices when contacting artists</li>
            </ul>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">SYSTEM INFORMATION</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-prism-medium-gray">Application Version:</span>
            <span className="ml-2 font-medium font-mono">1.0.0</span>
          </div>
          <div>
            <span className="text-prism-medium-gray">YouTube Integration:</span>
            <span className="ml-2 font-medium">Enabled</span>
          </div>
          <div>
            <span className="text-prism-medium-gray">Database Type:</span>
            <span className="ml-2 font-medium">SQLite</span>
          </div>
          <div>
            <span className="text-prism-medium-gray">Last Updated:</span>
            <span className="ml-2 font-medium font-mono">
              {systemInfo?.timestamp ? new Date(systemInfo.timestamp).toLocaleString() : 'Unknown'}
            </span>
          </div>
        </div>
      </div>

      {/* Save Settings */}
      <div className="flex justify-end">
        <button className="flex items-center px-6 py-2 bg-prism-red text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-prism-red focus:ring-offset-2 font-medium tracking-wide">
          <Save className="h-4 w-4 mr-2" />
          SAVE SETTINGS
        </button>
      </div>
    </div>
  );
};

export default Settings;