import React, { useState, useEffect } from 'react';
import { 
  Youtube, 
  Search, 
  BarChart3, 
  TrendingUp, 
  Users, 
  Play, 
  Eye,
  AlertCircle,
  CheckCircle,
  ExternalLink,
  RefreshCw,
  Calendar,
  Clock
} from 'lucide-react';

const YouTubeIntegration = () => {
  const [youtubeStats, setYoutubeStats] = useState(null);
  const [opportunities, setOpportunities] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testLoading, setTestLoading] = useState(false);
  const [testArtist, setTestArtist] = useState('');
  const [selectedOpportunity, setSelectedOpportunity] = useState('no_youtube_presence');

  useEffect(() => {
    fetchYouTubeStats();
    fetchYouTubeOpportunities();
  }, []);

  const fetchYouTubeStats = async () => {
    try {
      const response = await fetch('/api/youtube/stats');
      const data = await response.json();
      setYoutubeStats(data);
    } catch (error) {
      console.error('Failed to fetch YouTube stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchYouTubeOpportunities = async () => {
    try {
      const response = await fetch('/api/youtube/opportunities?limit=20');
      const data = await response.json();
      setOpportunities(data.youtube_opportunities);
    } catch (error) {
      console.error('Failed to fetch YouTube opportunities:', error);
    }
  };

  const testYouTubeIntegration = async () => {
    if (!testArtist.trim()) return;
    
    setTestLoading(true);
    setTestResult(null);
    
    try {
      const response = await fetch('/api/youtube/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ artist_name: testArtist.trim() }),
      });
      
      const data = await response.json();
      setTestResult(data);
    } catch (error) {
      console.error('YouTube integration test failed:', error);
      setTestResult({ 
        status: 'error', 
        error: 'Test failed - check console for details' 
      });
    } finally {
      setTestLoading(false);
    }
  };

  const refreshArtistYouTubeData = async (artistId) => {
    try {
      const response = await fetch(`/api/artist/${artistId}/youtube/refresh`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchYouTubeOpportunities();
      }
      
      return data;
    } catch (error) {
      console.error('Failed to refresh YouTube data:', error);
      return { status: 'error', message: 'Refresh failed' };
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto mb-4"></div>
        <p className="text-prism-medium-gray">Loading YouTube integration...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-prism-black mb-2 flex items-center tracking-wide">
          <Youtube className="h-8 w-8 mr-3 text-red-600" />
          YOUTUBE INTEGRATION
        </h2>
        <p className="text-prism-medium-gray">Analyze YouTube presence and identify growth opportunities for artists</p>
      </div>

      {/* YouTube Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">ARTISTS WITH YOUTUBE</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {youtubeStats?.artists_with_youtube_channels || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BarChart3 className="h-8 w-8 text-prism-red" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">COVERAGE %</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {youtubeStats?.youtube_coverage_percentage?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">TOTAL SUBSCRIBERS</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {(youtubeStats?.total_youtube_subscribers || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Youtube className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">HIGH POTENTIAL</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {youtubeStats?.high_potential_channels || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* API Status */}
      <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Youtube className="h-6 w-6 text-red-600" />
            <div>
              <h3 className="text-lg font-semibold text-prism-black tracking-wide">API STATUS</h3>
              <p className="text-sm text-prism-medium-gray mt-1">
                {youtubeStats?.api_status === 'available' ? (
                  <span className="text-green-600 font-medium">
                    ✅ YouTube Data API v3 is configured and available
                  </span>
                ) : (
                  <span className="text-red-600 font-medium">
                    ❌ YouTube API not configured - set YOUTUBE_API_KEY environment variable
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-prism-medium-gray tracking-wide">GENERATED</p>
            <p className="text-xs text-prism-charcoal-gray font-mono">
              {youtubeStats?.generated_at ? new Date(youtubeStats.generated_at).toLocaleString() : 'Unknown'}
            </p>
          </div>
        </div>
      </div>

      {/* YouTube Integration Test */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">TEST YOUTUBE INTEGRATION</h3>
        <div className="space-y-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={testArtist}
              onChange={(e) => setTestArtist(e.target.value)}
              placeholder="Enter artist name to test (e.g., 'Lorde', 'The Black Seeds')"
              className="flex-1 px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              onKeyPress={(e) => e.key === 'Enter' && testYouTubeIntegration()}
            />
            <button
              onClick={testYouTubeIntegration}
              disabled={testLoading || !testArtist.trim()}
              className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide"
            >
              {testLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  TESTING...
                </div>
              ) : (
                <div className="flex items-center">
                  <Search className="h-4 w-4 mr-2" />
                  TEST INTEGRATION
                </div>
              )}
            </button>
          </div>

          {testResult && (
            <div className="mt-4 p-4 border rounded-lg">
              {testResult.status === 'success' ? (
                <div className="space-y-4">
                  <div className="flex items-center text-green-600">
                    <CheckCircle className="h-5 w-5 mr-2" />
                    <span className="font-medium">YouTube channel found!</span>
                  </div>
                  
                  {testResult.channel_data && (
                    <div className="bg-prism-light-gray rounded-lg p-4">
                      <h4 className="font-medium text-prism-black mb-2 tracking-wide">CHANNEL INFORMATION</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-prism-medium-gray">Channel:</span>
                          <span className="ml-2 font-medium">{testResult.channel_data.title}</span>
                        </div>
                        <div>
                          <span className="text-prism-medium-gray">Subscribers:</span>
                          <span className="ml-2 font-medium font-mono">
                            {(testResult.channel_data.statistics?.subscriber_count || 0).toLocaleString()}
                          </span>
                        </div>
                        <div>
                          <span className="text-prism-medium-gray">Total Views:</span>
                          <span className="ml-2 font-medium font-mono">
                            {(testResult.channel_data.statistics?.view_count || 0).toLocaleString()}
                          </span>
                        </div>
                        <div>
                          <span className="text-prism-medium-gray">Videos:</span>
                          <span className="ml-2 font-medium font-mono">
                            {testResult.channel_data.statistics?.video_count || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {testResult.analytics && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-medium text-prism-black mb-2 tracking-wide">ANALYTICS</h4>
                      <div className="text-sm space-y-1">
                        <div>
                          <span className="text-prism-medium-gray">Upload Frequency:</span>
                          <span className="ml-2 font-medium capitalize">
                            {testResult.analytics.recent_activity?.upload_frequency || 'Unknown'}
                          </span>
                        </div>
                        <div>
                          <span className="text-prism-medium-gray">Growth Potential:</span>
                          <span className="ml-2 font-medium capitalize">
                            {testResult.analytics.growth_potential || 'Unknown'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {testResult.recent_videos && testResult.recent_videos.length > 0 && (
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <h4 className="font-medium text-prism-black mb-2 tracking-wide">RECENT VIDEOS</h4>
                      <div className="space-y-2">
                        {testResult.recent_videos.slice(0, 3).map((video, index) => (
                          <div key={index} className="text-sm">
                            <div className="font-medium">{video.title}</div>
                            <div className="text-prism-medium-gray">
                              Views: <span className="font-mono">{(video.statistics?.view_count || 0).toLocaleString()}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : testResult.status === 'not_found' ? (
                <div className="flex items-center text-yellow-600">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <span>No YouTube channel found for "{testResult.artist_name}"</span>
                </div>
              ) : (
                <div className="flex items-center text-red-600">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <span>Test failed: {testResult.error || 'Unknown error'}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* YouTube Opportunities */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-prism-black tracking-wide">YOUTUBE OPPORTUNITIES</h3>
          <button
            onClick={fetchYouTubeOpportunities}
            className="text-sm text-prism-red hover:text-red-700 flex items-center"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </button>
        </div>

        <div className="mb-4">
          <div className="flex space-x-4">
            <button
              onClick={() => setSelectedOpportunity('no_youtube_presence')}
              className={`px-4 py-2 rounded-md text-sm font-medium tracking-wide ${
                selectedOpportunity === 'no_youtube_presence'
                  ? 'bg-red-100 text-red-700 border border-red-200'
                  : 'bg-prism-light-gray text-prism-charcoal-gray hover:bg-gray-200'
              }`}
            >
              NO YOUTUBE PRESENCE
            </button>
            <button
              onClick={() => setSelectedOpportunity('underperforming_youtube')}
              className={`px-4 py-2 rounded-md text-sm font-medium tracking-wide ${
                selectedOpportunity === 'underperforming_youtube'
                  ? 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                  : 'bg-prism-light-gray text-prism-charcoal-gray hover:bg-gray-200'
              }`}
            >
              UNDERPERFORMING YOUTUBE
            </button>
          </div>
        </div>

        {opportunities && (
          <div className="space-y-4">
            {selectedOpportunity === 'no_youtube_presence' && (
              <div>
                <h4 className="font-medium text-prism-black mb-3 flex items-center tracking-wide">
                  <Youtube className="h-4 w-4 mr-2 text-red-500" />
                  ARTISTS WITH NO YOUTUBE PRESENCE (<span className="font-mono">{opportunities.no_youtube_presence?.length || 0}</span>)
                </h4>
                <p className="text-sm text-prism-medium-gray mb-4">
                  These artists have significant Spotify followings but no YouTube channels - major opportunity!
                </p>
                
                {opportunities.no_youtube_presence?.length > 0 ? (
                  <div className="space-y-3">
                    {opportunities.no_youtube_presence.map((artist) => (
                      <div key={artist.id} className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <div className="font-medium text-prism-black">{artist.name}</div>
                            <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              artist.lead_tier === 'A' ? 'bg-green-100 text-green-800' :
                              artist.lead_tier === 'B' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              TIER {artist.lead_tier}
                            </span>
                          </div>
                          <div className="text-sm text-prism-medium-gray mt-1">
                            {artist.country && `${artist.country} • `}
                            <span className="font-mono">{(artist.monthly_listeners || 0).toLocaleString()}</span> Spotify listeners • 
                            Score: <span className="font-mono">{artist.total_score?.toFixed(1)}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="text-right text-sm">
                            <div className="font-medium text-red-600">Major Opportunity</div>
                            <div className="text-prism-charcoal-gray">No YouTube channel</div>
                          </div>
                          <button
                            onClick={() => refreshArtistYouTubeData(artist.id)}
                            className="p-2 text-prism-charcoal-gray hover:text-prism-black"
                            title="Refresh YouTube data"
                          >
                            <RefreshCw className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-prism-medium-gray">
                    <Youtube className="h-12 w-12 mx-auto mb-4 text-prism-light-gray" />
                    <p>No artists found with missing YouTube presence</p>
                  </div>
                )}
              </div>
            )}

            {selectedOpportunity === 'underperforming_youtube' && (
              <div>
                <h4 className="font-medium text-prism-black mb-3 flex items-center tracking-wide">
                  <TrendingUp className="h-4 w-4 mr-2 text-yellow-500" />
                  ARTISTS WITH UNDERPERFORMING YOUTUBE (<span className="font-mono">{opportunities.underperforming_youtube?.length || 0}</span>)
                </h4>
                <p className="text-sm text-prism-medium-gray mb-4">
                  These artists have YouTube channels but low subscriber counts relative to their Spotify following.
                </p>
                
                {opportunities.underperforming_youtube?.length > 0 ? (
                  <div className="space-y-3">
                    {opportunities.underperforming_youtube.map((artist) => {
                      const youtubeRatio = artist.monthly_listeners > 0 
                        ? ((artist.youtube_subscribers || 0) / artist.monthly_listeners * 100)
                        : 0;
                      
                      return (
                        <div key={artist.id} className="flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center">
                              <div className="font-medium text-prism-black">{artist.name}</div>
                              <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                artist.lead_tier === 'A' ? 'bg-green-100 text-green-800' :
                                artist.lead_tier === 'B' ? 'bg-red-100 text-red-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                TIER {artist.lead_tier}
                              </span>
                            </div>
                            <div className="text-sm text-prism-medium-gray mt-1">
                              Spotify: <span className="font-mono">{(artist.monthly_listeners || 0).toLocaleString()}</span> • 
                              YouTube: <span className="font-mono">{(artist.youtube_subscribers || 0).toLocaleString()}</span> subs •
                              Ratio: <span className="font-mono">{youtubeRatio.toFixed(1)}%</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="text-right text-sm">
                              <div className="font-medium text-yellow-600">Growth Opportunity</div>
                              <div className="text-prism-charcoal-gray">Underperforming channel</div>
                            </div>
                            {artist.youtube_channel_url && (
                              <a
                                href={artist.youtube_channel_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-2 text-red-500 hover:text-red-600"
                                title="View YouTube channel"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            )}
                            <button
                              onClick={() => refreshArtistYouTubeData(artist.id)}
                              className="p-2 text-prism-charcoal-gray hover:text-prism-black"
                              title="Refresh YouTube data"
                            >
                              <RefreshCw className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8 text-prism-medium-gray">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 text-prism-light-gray" />
                    <p>No artists found with underperforming YouTube channels</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Integration Guide */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">YOUTUBE INTEGRATION GUIDE</h3>
        <div className="space-y-4 text-sm text-prism-medium-gray">
          <div>
            <h4 className="font-medium text-prism-black mb-2 tracking-wide">HOW YOUTUBE INTEGRATION WORKS</h4>
            <ul className="list-disc list-inside space-y-1">
              <li>Automatically searches for artist YouTube channels during ISRC analysis</li>
              <li>Collects subscriber counts, view counts, and upload frequency data</li>
              <li>Identifies artists with no YouTube presence (major opportunities)</li>
              <li>Finds artists with underperforming YouTube channels relative to Spotify</li>
              <li>Integrates YouTube metrics into lead scoring algorithm</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-prism-black mb-2 tracking-wide">OPPORTUNITY TYPES</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <div className="font-medium text-red-800 mb-1">No YouTube Presence</div>
                <div className="text-xs text-red-600">
                  Artists with significant Spotify following but no YouTube channel. 
                  Major opportunity for YouTube growth and monetization.
                </div>
              </div>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <div className="font-medium text-yellow-800 mb-1">Underperforming YouTube</div>
                <div className="text-xs text-yellow-600">
                  Artists with YouTube channels but low subscriber counts relative to Spotify.
                  Opportunity for channel optimization and growth strategies.
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-prism-black mb-2 tracking-wide">SETUP REQUIREMENTS</h4>
            <div className="p-3 bg-blue-50 border border-blue-200 rounded">
              <ol className="list-decimal list-inside space-y-1 text-xs">
                <li>Obtain YouTube Data API v3 key from Google Cloud Console</li>
                <li>Set YOUTUBE_API_KEY environment variable</li>
                <li>Ensure daily quota limit of 10,000 units is sufficient</li>
                <li>Monitor API usage in rate limits panel</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YouTubeIntegration;