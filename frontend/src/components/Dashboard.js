import React, { useState, useEffect } from 'react';
import { 
  Users, 
  TrendingUp, 
  Youtube,
  BarChart3,
  Music,
  Globe,
  AlertCircle,
  CheckCircle,
  RefreshCw
} from 'lucide-react';

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

const Dashboard = ({ systemStatus }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const data = await apiCall('/dashboard/stats');
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      // Set default stats if API fails
      setStats({
        total_artists: 0,
        tier_distribution: { A: 0, B: 0, C: 0, D: 0 },
        youtube_statistics: { artists_with_youtube: 0 },
        total_tracks: 0,
        recent_activity: []
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshStats = async () => {
    setRefreshing(true);
    await fetchDashboardStats();
    setRefreshing(false);
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 tracking-wide">DASHBOARD</h2>
          <p className="text-gray-600">Analytics overview and lead generation insights</p>
        </div>
        <button
          onClick={refreshStats}
          disabled={refreshing}
          className="flex items-center px-4 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">TOTAL ARTISTS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.total_artists?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">A-TIER LEADS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.tier_distribution?.A?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Youtube className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">YOUTUBE CHANNELS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.youtube_statistics?.artists_with_youtube?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Music className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-700 tracking-wide">TOTAL TRACKS</p>
              <p className="text-2xl font-semibold text-gray-900 font-mono">
                {stats?.total_tracks?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Average Score Calculation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 tracking-wide">AVERAGE LEAD SCORE</h3>
          <div className="text-right">
            <span className="text-3xl font-bold text-gray-900 font-mono">
              {stats && stats.total_artists > 0 ? Math.round(
                ((stats.tier_distribution?.A || 0) * 85 + 
                 (stats.tier_distribution?.B || 0) * 65 + 
                 (stats.tier_distribution?.C || 0) * 45 + 
                 (stats.tier_distribution?.D || 0) * 25) / 
                Math.max(stats.total_artists, 1)
              ) : 0}
            </span>
            <p className="text-sm text-gray-600">out of 100</p>
          </div>
        </div>
        
        {/* Score distribution visualization */}
        <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
          <div className="h-full flex">
            {['A', 'B', 'C', 'D'].map((tier, index) => {
              const count = stats?.tier_distribution?.[tier] || 0;
              const total = stats?.total_artists || 1;
              const percentage = (count / total) * 100;
              const colors = ['bg-green-500', 'bg-red-600', 'bg-yellow-500', 'bg-gray-500'];
              
              return (
                <div 
                  key={tier}
                  className={`${colors[index]} transition-all duration-1000`}
                  style={{ width: `${percentage}%` }}
                  title={`Tier ${tier}: ${count} (${percentage.toFixed(1)}%)`}
                ></div>
              );
            })}
          </div>
        </div>
      </div>

      {/* YouTube Integration Status */}
      {systemStatus?.youtube_integration && (
        <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <Youtube className="h-6 w-6 text-red-600" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 tracking-wide">YOUTUBE INTEGRATION</h3>
              <p className="text-sm text-gray-600 mt-1">
                {systemStatus.youtube_integration.api_key_configured ? (
                  <>
                    <span className="text-green-600 font-medium">✅ Active</span> - 
                    Quota used today: <span className="font-mono">{systemStatus.youtube_integration.daily_quota_used || 0}</span> / <span className="font-mono">{systemStatus.youtube_integration.daily_quota_limit || 10000}</span>
                  </>
                ) : (
                  <span className="text-red-600 font-medium">❌ Configure YouTube API key to enable YouTube features</span>
                )}
              </p>
            </div>
            {stats?.youtube_statistics && (
              <div className="text-right">
                <p className="text-sm text-gray-600">Coverage</p>
                <p className="text-lg font-semibold text-red-600 font-mono">
                  {stats.total_artists > 0 
                    ? ((stats.youtube_statistics.artists_with_youtube / stats.total_artists) * 100).toFixed(1)
                    : 0}%
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Lead Distribution by Tier */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">LEAD DISTRIBUTION BY TIER</h3>
        <div className="space-y-4">
          {['A', 'B', 'C', 'D'].map(tier => {
            const count = stats?.tier_distribution?.[tier] || 0;
            const total = stats?.total_artists || 1;
            const percentage = (count / total) * 100;
            
            return (
              <div key={tier} className="flex items-center">
                <div className="w-20 text-sm font-medium text-gray-600 tracking-wide">TIER {tier}</div>
                <div className="flex-1 mx-4">
                  <div className="bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-1000 ${
                        tier === 'A' ? 'bg-green-500' :
                        tier === 'B' ? 'bg-red-600' :
                        tier === 'C' ? 'bg-yellow-500' : 'bg-gray-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-24 text-sm text-gray-600 text-right">
                  <span className="font-mono">{count.toLocaleString()}</span>
                  <span className="text-gray-500 ml-1">({percentage.toFixed(1)}%)</span>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Tier Descriptions */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3 bg-green-50 border border-green-200 rounded">
            <div className="font-medium text-green-800 mb-1">TIER A - HIGH PRIORITY</div>
            <div className="text-green-600">
              Independent artists with strong potential, good metrics, and high opportunity scores.
            </div>
          </div>
          <div className="p-3 bg-red-50 border border-red-200 rounded">
            <div className="font-medium text-red-800 mb-1">TIER B - MEDIUM PRIORITY</div>
            <div className="text-red-600">
              Good potential artists with moderate independence and opportunity scores.
            </div>
          </div>
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <div className="font-medium text-yellow-800 mb-1">TIER C - LOW PRIORITY</div>
            <div className="text-yellow-600">
              Artists with some potential but lower opportunity or independence scores.
            </div>
          </div>
          <div className="p-3 bg-gray-50 border border-gray-200 rounded">
            <div className="font-medium text-gray-800 mb-1">TIER D - VERY LOW PRIORITY</div>
            <div className="text-gray-600">
              Artists with limited independence or low opportunity scores.
            </div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">SYSTEM HEALTH</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className={`h-4 w-4 rounded-full mx-auto mb-2 ${
              systemStatus?.database_status === 'connected' ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
            <div className="text-sm font-medium text-gray-900 tracking-wide">DATABASE</div>
            <div className="text-xs text-gray-600 font-mono">
              {systemStatus?.database_status === 'connected' ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          
          <div className="text-center">
            <div className={`h-4 w-4 rounded-full mx-auto mb-2 ${
              systemStatus?.youtube_integration?.status === 'available' ? 'bg-green-400' : 'bg-yellow-400'
            }`}></div>
            <div className="text-sm font-medium text-gray-900 tracking-wide">YOUTUBE API</div>
            <div className="text-xs text-gray-600 font-mono">
              {systemStatus?.youtube_integration?.api_key_configured ? 'Configured' : 'Available'}
            </div>
          </div>
          
          <div className="text-center">
            <div className="h-4 w-4 rounded-full bg-green-400 mx-auto mb-2"></div>
            <div className="text-sm font-medium text-gray-900 tracking-wide">PROCESSING ENGINE</div>
            <div className="text-xs text-gray-600 font-mono">Active</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;