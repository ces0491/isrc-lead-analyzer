import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  Music, 
  Youtube,
  Globe,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  TrendingUp,
  Users,
  BarChart3,
  Save,
  RefreshCw,
  Mail,
  FileText
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

const ISRCAnalyzer = () => {
  const navigate = useNavigate();
  const [isrc, setIsrc] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [includeYoutube, setIncludeYoutube] = useState(true);
  const [saveToDb, setSaveToDb] = useState(true);
  const [forceRefresh, setForceRefresh] = useState(false);

  const validateISRC = (isrcCode) => {
    if (!isrcCode) return false;
    // Remove any hyphens or spaces
    const cleaned = isrcCode.replace(/[-\s]/g, '').toUpperCase();
    // ISRC format: CC-XXX-YY-NNNNN (12 characters total)
    return cleaned.length === 12 && /^[A-Z]{2}[A-Z0-9]{3}[0-9]{2}[A-Z0-9]{5}$/.test(cleaned);
  };

  const formatISRC = (isrcCode) => {
    if (!isrcCode) return '';
    const cleaned = isrcCode.replace(/[-\s]/g, '').toUpperCase();
    return cleaned;
  };

  const analyzeISRC = async () => {
    if (!isrc.trim()) return;
    
    const formattedISRC = formatISRC(isrc.trim());
    
    if (!validateISRC(formattedISRC)) {
      setResult({ 
        status: 'error', 
        error: 'Invalid ISRC format. Expected format: CC-XXX-YY-NNNNN (e.g., USRC17607839)',
        isrc: formattedISRC
      });
      return;
    }
    
    setLoading(true);
    setResult(null);
    
    try {
      const data = await apiCall('/analyze-isrc', {
        method: 'POST',
        body: JSON.stringify({ 
          isrc: formattedISRC, 
          save_to_db: saveToDb,
          include_youtube: includeYoutube,
          force_refresh: forceRefresh
        })
      });
      
      setResult(data);
    } catch (error) {
      console.error('Failed to analyze ISRC:', error);
      setResult({ 
        status: 'error', 
        error: error.message || 'Failed to analyze ISRC. Please check your connection and try again.',
        isrc: formattedISRC
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      analyzeISRC();
    }
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'A': return 'bg-green-100 text-green-800 border-green-200';
      case 'B': return 'bg-red-100 text-red-800 border-red-200';
      case 'C': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'D': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTierDescription = (tier) => {
    switch (tier) {
      case 'A': return 'High Priority - Excellent independent artist with strong opportunity';
      case 'B': return 'Medium Priority - Good potential with moderate opportunity';
      case 'C': return 'Low Priority - Some potential but limited opportunity';
      case 'D': return 'Very Low Priority - Limited independence or opportunity';
      default: return 'Not classified';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2 tracking-wide">ISRC ANALYZER</h2>
        <p className="text-gray-600">Lead scoring and opportunity assessment with YouTube integration</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="isrc" className="block text-sm font-medium text-gray-900 mb-2 tracking-wide">
              ISRC CODE
            </label>
            <div className="relative">
              <input
                type="text"
                id="isrc"
                value={isrc}
                onChange={(e) => setIsrc(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., USRC17607839 or US-RC1-76-07839"
                className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 font-mono ${
                  isrc && !validateISRC(formatISRC(isrc)) 
                    ? 'border-red-300 bg-red-50' 
                    : 'border-gray-300'
                }`}
              />
              {isrc && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  {validateISRC(formatISRC(isrc)) ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              )}
            </div>
            {isrc && !validateISRC(formatISRC(isrc)) && (
              <p className="text-sm text-red-600 mt-1">
                Invalid ISRC format. Expected 12 characters: CC-XXX-YY-NNNNN
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeYoutube}
                onChange={(e) => setIncludeYoutube(e.target.checked)}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600 flex items-center">
                <Youtube className="h-4 w-4 mr-1 text-red-500" />
                Include YouTube data collection
              </span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={saveToDb}
                onChange={(e) => setSaveToDb(e.target.checked)}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600 flex items-center">
                <Save className="h-4 w-4 mr-1 text-gray-500" />
                Save to database
              </span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={forceRefresh}
                onChange={(e) => setForceRefresh(e.target.checked)}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600 flex items-center">
                <RefreshCw className="h-4 w-4 mr-1 text-gray-500" />
                Force refresh data
              </span>
            </label>
          </div>

          {/* Analysis Button */}
          <div className="flex space-x-4">
            <button
              onClick={analyzeISRC}
              disabled={loading || !isrc.trim() || !validateISRC(formatISRC(isrc))}
              className="flex-1 bg-red-600 text-white py-3 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  ANALYZING...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <Search className="h-5 w-5 mr-2" />
                  ANALYZE FOR LEADS
                </div>
              )}
            </button>

            <button
              onClick={() => navigate(`/track/${formatISRC(isrc)}`)}
              disabled={!isrc.trim() || !validateISRC(formatISRC(isrc))}
              className="bg-purple-600 text-white py-3 px-4 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide transition-colors"
            >
              <div className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                FULL METADATA
              </div>
            </button>
          </div>

          {/* Analysis Info */}
          <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">📊 LEAD ANALYSIS</h4>
                <ul className="space-y-1">
                  <li>• Lead scoring and tier classification (A, B, C, D)</li>
                  <li>• Independence, opportunity, and geographic scoring</li>
                  <li>• YouTube channel discovery and analytics</li>
                  <li>• Contact information extraction</li>
                  <li>• Platform availability assessment</li>
                  <li>• Artist and track metadata collection</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">📋 FULL METADATA ANALYSIS</h4>
                <ul className="space-y-1">
                  <li>• Complete track credits & personnel database</li>
                  <li>• Full lyrics with copyright information</li>
                  <li>• Technical audio analysis & production metrics</li>
                  <li>• Publishing rights & splits breakdown</li>
                  <li>• Recording location & production details</li>
                </ul>
                <div className="mt-3 p-2 bg-purple-50 border border-purple-200 rounded text-xs">
                  <strong>Use "Full Metadata" button →</strong> for comprehensive track analysis
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 tracking-wide">ANALYSIS RESULTS</h3>
          
          {result.status === 'completed' ? (
            <div className="space-y-6">
              {/* Header with ISRC and Status */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span className="font-medium text-green-800">Lead Analysis Completed</span>
                    </div>
                    <p className="text-sm text-green-600 mt-1 font-mono">ISRC: {result.isrc}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm text-green-600">Processing Time</p>
                      <p className="font-mono text-green-800">{result.processing_time || 'N/A'}s</p>
                    </div>
                    <button
                      onClick={() => navigate(`/track/${result.isrc}`)}
                      className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm font-medium tracking-wide transition-colors"
                    >
                      <FileText className="h-3 w-3 mr-1 inline" />
                      FULL METADATA
                    </button>
                  </div>
                </div>
              </div>

              {/* Artist and Track Information */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 tracking-wide">ARTIST INFORMATION</h4>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                      <div>
                        <span className="text-sm text-gray-600">Artist:</span>
                        <p className="text-lg font-semibold text-red-600">
                          {result.artist_data?.name || 'Unknown Artist'}
                        </p>
                      </div>
                      {result.artist_data?.country && (
                        <div>
                          <span className="text-sm text-gray-600">Country:</span>
                          <p className="font-medium">{result.artist_data.country}</p>
                        </div>
                      )}
                      {result.artist_data?.genre && (
                        <div>
                          <span className="text-sm text-gray-600">Genre:</span>
                          <p className="font-medium">{result.artist_data.genre}</p>
                        </div>
                      )}
                      {result.artist_data?.monthly_listeners && (
                        <div>
                          <span className="text-sm text-gray-600">Monthly Listeners:</span>
                          <p className="font-medium font-mono">{result.artist_data.monthly_listeners.toLocaleString()}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 tracking-wide">TRACK INFORMATION</h4>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                      <div>
                        <span className="text-sm text-gray-600">Title:</span>
                        <p className="font-medium">{result.track_data?.title || 'Unknown Track'}</p>
                      </div>
                      {result.track_data?.label && (
                        <div>
                          <span className="text-sm text-gray-600">Label:</span>
                          <p className="font-medium">{result.track_data.label}</p>
                        </div>
                      )}
                      {result.track_data?.release_date && (
                        <div>
                          <span className="text-sm text-gray-600">Release Date:</span>
                          <p className="font-medium">{new Date(result.track_data.release_date).toLocaleDateString()}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3 tracking-wide">LEAD SCORING</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-center mb-4">
                      <div className="flex items-center justify-center space-x-3">
                        <span className="text-4xl font-bold text-gray-900 font-mono">
                          {result.scores?.total_score?.toFixed(1) || 0}
                        </span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getTierColor(result.scores?.tier)}`}>
                          TIER {result.scores?.tier || 'D'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        {getTierDescription(result.scores?.tier)}
                      </p>
                      {result.scores?.confidence && (
                        <p className="text-xs text-gray-500 mt-1 font-mono">
                          Confidence: {result.scores.confidence}%
                        </p>
                      )}
                    </div>

                    {/* Score Breakdown */}
                    <div className="space-y-3">
                      {[
                        { 
                          label: 'Independence', 
                          score: result.scores?.independence_score || 0, 
                          color: 'bg-red-600',
                          description: 'How independent the artist is from major labels'
                        },
                        { 
                          label: 'Opportunity', 
                          score: result.scores?.opportunity_score || 0, 
                          color: 'bg-green-500',
                          description: 'Growth potential and service opportunities'
                        },
                        { 
                          label: 'Geographic', 
                          score: result.scores?.geographic_score || 0, 
                          color: 'bg-blue-500',
                          description: 'Regional targeting relevance'
                        }
                      ].map(({ label, score, color, description }) => (
                        <div key={label}>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-gray-700">{label}</span>
                            <span className="text-sm font-mono text-gray-600">{score}/100</span>
                          </div>
                          <div className="bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-1000 ${color}`}
                              style={{ width: `${score}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* YouTube Integration Results */}
              {includeYoutube && result.youtube_data && (
                <div className="border-t pt-6">
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Youtube className="h-5 w-5 mr-2 text-red-600" />
                    YOUTUBE ANALYSIS
                  </h4>
                  
                  {result.youtube_data.channel ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                            <span className="font-medium text-green-800">YouTube Channel Found!</span>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Channel:</span>
                              <p className="font-medium">{result.youtube_data.channel.title}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">Subscribers:</span>
                              <p className="font-medium font-mono">{(result.youtube_data.channel.statistics?.subscriber_count || 0).toLocaleString()}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">Total Views:</span>
                              <p className="font-medium font-mono">{(result.youtube_data.channel.statistics?.view_count || 0).toLocaleString()}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">Videos:</span>
                              <p className="font-medium font-mono">{result.youtube_data.channel.statistics?.video_count || 0}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">Upload Frequency:</span>
                              <p className="font-medium">{result.youtube_data.analytics?.upload_frequency || 'Unknown'}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">Growth Potential:</span>
                              <p className="font-medium capitalize">{result.youtube_data.analytics?.growth_potential || 'Unknown'}</p>
                            </div>
                          </div>
                        </div>
                        {result.youtube_data.channel.custom_url && (
                          <a
                            href={`https://youtube.com/${result.youtube_data.channel.custom_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-4 p-2 text-red-600 hover:text-red-700 bg-white border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <TrendingUp className="h-5 w-5 text-yellow-600 mr-2" />
                        <div>
                          <p className="font-medium text-yellow-800">Major YouTube Opportunity!</p>
                          <p className="text-sm text-yellow-600 mt-1">
                            No YouTube channel found for this artist. This represents a significant opportunity for YouTube growth and monetization.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Contact Information */}
              {result.contacts && result.contacts.length > 0 && (
                <div className="border-t pt-6">
                  <h4 className="font-medium text-gray-900 mb-3 tracking-wide">CONTACT INFORMATION</h4>
                  <div className="space-y-2">
                    {result.contacts.map((contact, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          {contact.type === 'email' ? (
                            <Mail className="h-4 w-4 text-gray-500 mr-2" />
                          ) : contact.type === 'website' ? (
                            <Globe className="h-4 w-4 text-gray-500 mr-2" />
                          ) : (
                            <Users className="h-4 w-4 text-gray-500 mr-2" />
                          )}
                          <span className="font-medium">{contact.value}</span>
                          <span className="ml-2 text-sm text-gray-500">({contact.type})</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500">
                            Confidence: {contact.confidence}%
                          </span>
                          {contact.type === 'email' && (
                            <a
                              href={`mailto:${contact.value}`}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Mail className="h-4 w-4" />
                            </a>
                          )}
                          {contact.type === 'website' && (
                            <a
                              href={contact.value}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-red-600 hover:text-red-700"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Data Sources */}
              <div className="border-t pt-6">
                <h4 className="font-medium text-gray-900 mb-3 tracking-wide">DATA SOURCES</h4>
                <div className="flex flex-wrap gap-2">
                  {(result.data_sources_used || []).map(source => (
                    <span key={source} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-900 border">
                      {source === 'youtube' && <Youtube className="h-3 w-3 mr-1 text-red-500" />}
                      {source === 'spotify' && <Music className="h-3 w-3 mr-1 text-green-500" />}
                      {source === 'musicbrainz' && <BarChart3 className="h-3 w-3 mr-1 text-gray-500" />}
                      {source.charAt(0).toUpperCase() + source.slice(1)}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : result.status === 'not_found' ? (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">Track Not Found</h4>
              <p className="text-gray-600 mb-4">
                No data found for ISRC: <span className="font-mono">{result.isrc}</span>
              </p>
              <p className="text-sm text-gray-500">
                This ISRC may not exist in the databases we search, or the track may not be distributed digitally.
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">Analysis Failed</h4>
              <p className="text-red-600 font-medium mb-2">{result.error || 'Unknown error occurred'}</p>
              <p className="text-sm text-gray-500">
                Please check your connection and try again. If the problem persists, the ISRC may be invalid or the service may be temporarily unavailable.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ISRCAnalyzer;