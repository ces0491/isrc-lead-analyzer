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

// Prism Logo Component
const PrismLogo = ({ className = "h-8 w-8" }) => (
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
      
      {/* Triangular prism */}
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
      const response = await fetch('/api/dashboard/stats');
      const data = await response.json();
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-prism-red mx-auto mb-4"></div>
        <p className="text-prism-medium-gray">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-prism-black mb-2 tracking-wide">DASHBOARD</h2>
        <p className="text-prism-medium-gray">Overview of your lead generation activities</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-prism-red" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">TOTAL ARTISTS</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {stats?.total_artists || 0}
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
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">A-TIER LEADS</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {stats?.tier_distribution?.A || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Youtube className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">YOUTUBE CHANNELS</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
                {stats?.youtube_statistics?.artists_with_youtube || 0}
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
              <p className="text-sm font-medium text-prism-charcoal-gray tracking-wide">AVG. SCORE</p>
              <p className="text-2xl font-semibold text-prism-black font-mono">
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
              <h3 className="text-lg font-semibold text-prism-black tracking-wide">YOUTUBE INTEGRATION</h3>
              <p className="text-sm text-prism-medium-gray mt-1">
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
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">LEAD DISTRIBUTION BY TIER</h3>
        <div className="space-y-3">
          {['A', 'B', 'C', 'D'].map(tier => {
            const count = stats?.tier_distribution?.[tier] || 0;
            const total = stats?.total_artists || 1;
            const percentage = (count / total) * 100;
            
            return (
              <div key={tier} className="flex items-center">
                <div className="w-16 text-sm font-medium text-prism-medium-gray tracking-wide">TIER {tier}</div>
                <div className="flex-1 mx-4">
                  <div className="bg-prism-light-gray rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        tier === 'A' ? 'bg-green-500' :
                        tier === 'B' ? 'bg-prism-red' :
                        tier === 'C' ? 'bg-yellow-500' : 'bg-prism-charcoal-gray'
                      }`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-sm text-prism-medium-gray text-right font-mono">
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
      const response = await fetch('/api/analyze-isrc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          isrc: isrc.trim(), 
          save_to_db: true,
          include_youtube: includeYoutube 
        }),
      });
      
      const data = await response.json();
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
        <h2 className="text-2xl font-bold text-prism-black mb-2 tracking-wide">ISRC ANALYZER</h2>
        <p className="text-prism-medium-gray">Analyze individual tracks and discover lead opportunities</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="isrc" className="block text-sm font-medium text-prism-black mb-2 tracking-wide">
              ISRC CODE
            </label>
            <input
              type="text"
              id="isrc"
              value={isrc}
              onChange={(e) => setIsrc(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., USRC17607839"
              className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red font-mono"
            />
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeYoutube}
                onChange={(e) => setIncludeYoutube(e.target.checked)}
                className="h-4 w-4 text-prism-red focus:ring-prism-red border-prism-light-gray rounded"
              />
              <span className="ml-2 text-sm text-prism-medium-gray">Include YouTube data collection</span>
            </label>
          </div>

          <button
            onClick={analyzeISRC}
            disabled={loading || !isrc.trim()}
            className="w-full bg-prism-red text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-prism-red focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide"
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
        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">ANALYSIS RESULTS</h3>
          
          {result.status === 'completed' ? (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-prism-black mb-2 tracking-wide">ARTIST INFORMATION</h4>
                  <p className="text-lg font-semibold text-prism-red">
                    {result.artist_data?.name || 'Unknown Artist'}
                  </p>
                  <p className="text-sm text-prism-medium-gray">
                    {result.track_data?.title || 'Unknown Track'}
                  </p>
                  <p className="text-sm text-prism-charcoal-gray font-mono">
                    Label: {result.track_data?.label || 'Unknown'}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-prism-black mb-2 tracking-wide">LEAD SCORE</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-3xl font-bold text-prism-black font-mono">
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
                  <p className="text-sm text-prism-medium-gray mt-1 font-mono">
                    Confidence: {result.scores?.confidence || 0}%
                  </p>
                </div>
              </div>

              {/* Score Breakdown */}
              <div>
                <h4 className="font-medium text-prism-black mb-3 tracking-wide">SCORE BREAKDOWN</h4>
                <div className="space-y-2">
                  {[
                    { label: 'Independence', score: result.scores?.independence_score, color: 'bg-prism-red' },
                    { label: 'Opportunity', score: result.scores?.opportunity_score, color: 'bg-green-500' },
                    { label: 'Geographic', score: result.scores?.geographic_score, color: 'bg-prism-charcoal-gray' }
                  ].map(({ label, score, color }) => (
                    <div key={label} className="flex items-center">
                      <div className="w-24 text-sm text-prism-medium-gray tracking-wide">{label.toUpperCase()}</div>
                      <div className="flex-1 mx-4">
                        <div className="bg-prism-light-gray rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${color}`}
                            style={{ width: `${score || 0}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-12 text-sm text-prism-medium-gray text-right font-mono">{score || 0}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* YouTube Integration Results */}
              {result.youtube_integration?.enabled && (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-prism-black mb-3 flex items-center tracking-wide">
                    <Youtube className="h-4 w-4 mr-2 text-red-600" />
                    YOUTUBE ANALYSIS
                  </h4>
                  {result.youtube_integration.data_found ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-sm text-green-600 font-medium mb-2">✅ YouTube channel found!</p>
                      <p className="text-xs text-prism-medium-gray">
                        YouTube data has been integrated into the opportunity scoring.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-yellow-700 font-medium mb-1">
                        ⚠️ No YouTube channel found
                      </p>
                      <p className="text-xs text-prism-medium-gray">
                        This represents a significant YouTube opportunity for the artist.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Data Sources */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-prism-black mb-2 tracking-wide">DATA SOURCES</h4>
                <div className="flex flex-wrap gap-2">
                  {result.data_sources_used?.map(source => (
                    <span key={source} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-prism-light-gray text-prism-black">
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
              <p className="text-sm text-prism-medium-gray">{result.error || 'Unknown error occurred'}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const BulkProcessor = () => {
  const [file, setFile] = useState(null);
  const [isrcs, setIsrcs] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState(0);
  const [includeYoutube, setIncludeYoutube] = useState(true);
  const [batchSize, setBatchSize] = useState(10);

  // File upload and parsing
  const handleFileUpload = useCallback((event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const content = e.target.result;
      parseISRCs(content, uploadedFile.name);
    };
    
    reader.readAsText(uploadedFile);
  }, []);

  const parseISRCs = (content, filename) => {
    const lines = content.split('\n');
    const parsedISRCs = [];
    
    // Parse CSV or TXT
    if (filename.toLowerCase().endsWith('.csv')) {
      lines.forEach((line, index) => {
        // Skip header row if it contains 'ISRC'
        if (index === 0 && line.toLowerCase().includes('isrc')) return;
        
        const columns = line.split(',');
        for (const column of columns) {
          const cleaned = column.trim().replace(/['"]/g, '');
          if (isValidISRC(cleaned)) {
            parsedISRCs.push(cleaned.toUpperCase());
            break; // Take first valid ISRC from row
          }
        }
      });
    } else {
      // Plain text - one ISRC per line
      lines.forEach(line => {
        const cleaned = line.trim().replace(/['"]/g, '');
        if (isValidISRC(cleaned)) {
          parsedISRCs.push(cleaned.toUpperCase());
        }
      });
    }
    
    // Remove duplicates
    const uniqueISRCs = [...new Set(parsedISRCs)];
    setIsrcs(uniqueISRCs);
  };

  const isValidISRC = (isrc) => {
    if (!isrc || typeof isrc !== 'string') return false;
    const cleaned = isrc.replace(/[-\s_]/g, '').toUpperCase();
    return cleaned.length === 12 && /^[A-Z]{2}[A-Z0-9]{3}[0-9]{2}[A-Z0-9]{5}$/.test(cleaned);
  };

  // Drag and drop handling
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      const reader = new FileReader();
      reader.onload = (event) => {
        parseISRCs(event.target.result, droppedFile.name);
      };
      reader.readAsText(droppedFile);
    }
  };

  // Bulk processing
  const startBulkProcessing = async () => {
    if (isrcs.length === 0) return;
    
    setProcessing(true);
    setProgress(0);
    setResults(null);
    
    try {
      const response = await fetch('/api/analyze-bulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          isrcs: isrcs,
          batch_size: batchSize,
          include_youtube: includeYoutube
        }),
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Bulk processing failed:', error);
      setResults({ 
        error: 'Bulk processing failed', 
        total_processed: 0, 
        successful: 0, 
        failed: isrcs.length 
      });
    } finally {
      setProcessing(false);
      setProgress(100);
    }
  };

  // Export results
  const exportResults = async () => {
    if (!results || !results.results) return;
    
    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filters: {}, // Export all results from bulk processing
          include_youtube_data: includeYoutube
        }),
      });
      
      const data = await response.json();
      
      if (data.csv_data) {
        // Create download link
        const blob = new Blob([data.csv_data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename || 'bulk_processing_results.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-prism-black mb-2 tracking-wide">BULK PROCESSING</h2>
        <p className="text-prism-medium-gray">Process multiple ISRCs with YouTube integration</p>
      </div>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">UPLOAD ISRC FILE</h3>
        
        {!file ? (
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="border-2 border-dashed border-prism-light-gray rounded-lg p-8 text-center hover:border-prism-red transition-colors"
          >
            <Upload className="h-12 w-12 text-prism-charcoal-gray mx-auto mb-4" />
            <p className="text-lg font-medium text-prism-black mb-2">
              Drop your CSV or TXT file here
            </p>
            <p className="text-sm text-prism-medium-gray mb-4">
              Or click to browse and select a file
            </p>
            <input
              type="file"
              accept=".csv,.txt"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-prism-red hover:bg-red-700 cursor-pointer tracking-wide"
            >
              <Upload className="h-4 w-4 mr-2" />
              CHOOSE FILE
            </label>
          </div>
        ) : (
          <div className="border border-prism-light-gray rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-prism-red" />
                <div>
                  <p className="font-medium text-prism-black">{file.name}</p>
                  <p className="text-sm text-prism-medium-gray font-mono">
                    {isrcs.length} valid ISRCs found
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setFile(null);
                  setIsrcs([]);
                  setResults(null);
                }}
                className="text-red-600 hover:text-red-700 text-sm font-medium"
              >
                Remove
              </button>
            </div>
            
            {isrcs.length > 0 && (
              <div className="mt-4 p-3 bg-prism-light-gray rounded-md">
                <p className="text-sm font-medium text-prism-black mb-2 tracking-wide">PREVIEW:</p>
                <div className="text-xs text-prism-medium-gray space-y-1 font-mono">
                  {isrcs.slice(0, 5).map((isrc, index) => (
                    <div key={index}>{isrc}</div>
                  ))}
                  {isrcs.length > 5 && (
                    <div className="text-prism-charcoal-gray">... and {isrcs.length - 5} more</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Processing Settings */}
      {isrcs.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">PROCESSING SETTINGS</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-prism-black mb-2 tracking-wide">
                BATCH SIZE
              </label>
              <select
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red"
              >
                <option value={5}>5 ISRCs per batch (Slower, more reliable)</option>
                <option value={10}>10 ISRCs per batch (Recommended)</option>
                <option value={20}>20 ISRCs per batch (Faster, may hit rate limits)</option>
              </select>
              <p className="text-xs text-prism-medium-gray mt-1">
                Smaller batches are more reliable but slower
              </p>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeYoutube}
                  onChange={(e) => setIncludeYoutube(e.target.checked)}
                  className="h-4 w-4 text-prism-red focus:ring-prism-red border-prism-light-gray rounded"
                />
                <span className="ml-2 text-sm text-prism-medium-gray flex items-center">
                  <Youtube className="h-4 w-4 mr-1 text-red-500" />
                  Include YouTube data collection
                </span>
              </label>
              <p className="text-xs text-prism-medium-gray mt-1 ml-6">
                Collects YouTube channel and video data for enhanced scoring
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-prism-medium-gray">
              Ready to process <span className="font-mono">{isrcs.length}</span> ISRCs
              {includeYoutube && ' with YouTube integration'}
            </div>
            <button
              onClick={startBulkProcessing}
              disabled={processing || isrcs.length === 0}
              className="bg-prism-red text-white px-6 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-prism-red focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium tracking-wide"
            >
              {processing ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  PROCESSING...
                </div>
              ) : (
                <div className="flex items-center">
                  <Play className="h-4 w-4 mr-2" />
                  START PROCESSING
                </div>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Processing Progress */}
      {processing && (
        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <h3 className="text-lg font-semibold text-prism-black mb-4 tracking-wide">PROCESSING PROGRESS</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-prism-medium-gray mb-1">
                <span>Processing ISRCs...</span>
                <span className="font-mono">{progress}%</span>
              </div>
              <div className="bg-prism-light-gray rounded-full h-2">
                <div 
                  className="bg-prism-red h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
            <div className="flex items-center text-sm text-prism-medium-gray">
              <Clock className="h-4 w-4 mr-2" />
              This may take several minutes depending on the number of ISRCs and API rate limits.
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-prism-black tracking-wide">PROCESSING RESULTS</h3>
            {results.successful > 0 && (
              <button
                onClick={exportResults}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 font-medium tracking-wide"
              >
                <Download className="h-4 w-4 mr-2" />
                EXPORT CSV
              </button>
            )}
          </div>

          {results.error ? (
            <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
              <div>
                <p className="font-medium text-red-800">Processing Failed</p>
                <p className="text-sm text-red-600">{results.error}</p>
              </div>
            </div>
          ) : (
            <>
              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-prism-light-gray border border-prism-charcoal-gray rounded-lg p-4">
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-prism-red mr-2" />
                    <span className="text-sm font-medium text-prism-medium-gray tracking-wide">TOTAL</span>
                  </div>
                  <p className="text-2xl font-semibold text-prism-black font-mono">
                    {results.total_processed || 0}
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-prism-medium-gray tracking-wide">SUCCESSFUL</span>
                  </div>
                  <p className="text-2xl font-semibold text-prism-black font-mono">
                    {results.successful || 0}
                  </p>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
                    <span className="text-sm font-medium text-prism-medium-gray tracking-wide">FAILED</span>
                  </div>
                  <p className="text-2xl font-semibold text-prism-black font-mono">
                    {results.failed || 0}
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Clock className="h-5 w-5 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-prism-medium-gray tracking-wide">SUCCESS RATE</span>
                  </div>
                  <p className="text-2xl font-semibold text-prism-black font-mono">
                    {results.success_rate?.toFixed(1) || 0}%
                  </p>
                </div>
              </div>

              {/* YouTube Statistics */}
              {includeYoutube && results.youtube_statistics && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="font-medium text-prism-black mb-2 flex items-center tracking-wide">
                    <Youtube className="h-4 w-4 mr-2 text-red-600" />
                    YOUTUBE INTEGRATION RESULTS
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-prism-medium-gray">Artists with YouTube:</span>
                      <span className="ml-2 font-medium font-mono">
                        {results.youtube_statistics.artists_with_youtube || 0}
                      </span>
                    </div>
                    <div>
                      <span className="text-prism-medium-gray">YouTube data collected:</span>
                      <span className="ml-2 font-medium font-mono">
                        {results.youtube_statistics.youtube_data_collected || 0}
                      </span>
                    </div>
                    <div>
                      <span className="text-prism-medium-gray">Total subscribers:</span>
                      <span className="ml-2 font-medium font-mono">
                        {(results.youtube_statistics.total_youtube_subscribers || 0).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Processing Time */}
              <div className="text-sm text-prism-medium-gray">
                Processing completed in <span className="font-mono">{results.total_time}s</span>
                {results.average_time_per_isrc && (
                  <span> (avg: <span className="font-mono">{results.average_time_per_isrc}s</span> per ISRC)</span>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

const LeadsList = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    tier: '',
    region: '',
    min_score: '',
    max_score: '',
    youtube_filter: '',
    search: ''
  });
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 25,
    offset: 0,
    has_more: false
  });
  const [selectedLeads, setSelectedLeads] = useState([]);
  const [expandedLead, setExpandedLead] = useState(null);
  const [sortBy, setSortBy] = useState('total_score');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    fetchLeads();
  }, [filters, pagination.offset, sortBy, sortOrder]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...filters,
        limit: pagination.limit,
        offset: pagination.offset,
        sort_by: sortBy,
        sort_order: sortOrder
      });

      // Remove empty filters
      Object.keys(filters).forEach(key => {
        if (!filters[key]) params.delete(key);
      });

      const response = await fetch(`/api/leads?${params}`);
      const data = await response.json();
      
      setLeads(data.leads || []);
      setPagination(prev => ({
        ...prev,
        total: data.pagination?.total || 0,
        has_more: data.pagination?.has_more || false
      }));
    } catch (error) {
      console.error('Failed to fetch leads:', error);
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setPagination(prev => ({ ...prev, offset: 0 })); // Reset to first page
  };

  const clearFilters = () => {
    setFilters({
      tier: '',
      region: '',
      min_score: '',
      max_score: '',
      youtube_filter: '',
      search: ''
    });
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const exportLeads = async () => {
    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filters: filters,
          include_youtube_data: true
        }),
      });
      
      const data = await response.json();
      
      if (data.csv_data) {
        const blob = new Blob([data.csv_data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename || 'leads_export.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const updateOutreachStatus = async (artistId, status) => {
    try {
      const response = await fetch(`/api/artist/${artistId}/outreach`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });
      
      if (response.ok) {
        // Refresh leads list
        fetchLeads();
      }
    } catch (error) {
      console.error('Failed to update outreach status:', error);
    }
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'A': return 'bg-green-100 text-green-800 border-green-200';
      case 'B': return 'bg-red-100 text-red-800 border-red-200';
      case 'C': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'D': return 'bg-prism-light-gray text-prism-charcoal-gray border-prism-charcoal-gray';
      default: return 'bg-prism-light-gray text-prism-charcoal-gray border-prism-charcoal-gray';
    }
  };

  const getOutreachStatusColor = (status) => {
    switch (status) {
      case 'not_contacted': return 'bg-prism-light-gray text-prism-charcoal-gray';
      case 'contacted': return 'bg-blue-100 text-blue-800';
      case 'responded': return 'bg-yellow-100 text-yellow-800';
      case 'interested': return 'bg-green-100 text-green-800';
      case 'not_interested': return 'bg-red-100 text-red-800';
      case 'converted': return 'bg-purple-100 text-purple-800';
      default: return 'bg-prism-light-gray text-prism-charcoal-gray';
    }
  };

  if (loading && leads.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-prism-red mx-auto mb-4"></div>
        <p className="text-prism-medium-gray">Loading leads...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-prism-black mb-2 tracking-wide">LEADS DATABASE</h2>
          <p className="text-prism-medium-gray">Manage and track your music industry leads with YouTube insights</p>
        </div>
        <button
          onClick={exportLeads}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 font-medium tracking-wide"
        >
          <Download className="h-4 w-4 mr-2" />
          EXPORT CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-prism-black flex items-center tracking-wide">
            <Filter className="h-5 w-5 mr-2" />
            FILTERS
          </h3>
          <button
            onClick={clearFilters}
            className="text-sm text-prism-red hover:text-red-700 font-medium"
          >
            Clear All
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-prism-black mb-1 tracking-wide">
              SEARCH ARTISTS
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-prism-charcoal-gray" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Artist name..."
                className="pl-10 block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red text-sm"
              />
            </div>
          </div>

          {/* Tier Filter */}
          <div>
            <label className="block text-sm font-medium text-prism-black mb-1 tracking-wide">
              LEAD TIER
            </label>
            <select
              value={filters.tier}
              onChange={(e) => handleFilterChange('tier', e.target.value)}
              className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red text-sm"
            >
              <option value="">All Tiers</option>
              <option value="A">Tier A (High Priority)</option>
              <option value="B">Tier B (Medium Priority)</option>
              <option value="C">Tier C (Low Priority)</option>
              <option value="D">Tier D (Very Low Priority)</option>
            </select>
          </div>

          {/* Region Filter */}
          <div>
            <label className="block text-sm font-medium text-prism-black mb-1 tracking-wide">
              REGION
            </label>
            <select
              value={filters.region}
              onChange={(e) => handleFilterChange('region', e.target.value)}
              className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red text-sm"
            >
              <option value="">All Regions</option>
              <option value="new_zealand">New Zealand</option>
              <option value="australia">Australia</option>
              <option value="pacific_islands">Pacific Islands</option>
              <option value="other_english_speaking">Other English Speaking</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* YouTube Filter */}
          <div>
            <label className="block text-sm font-medium text-prism-black mb-1 tracking-wide">
              <Youtube className="inline h-4 w-4 mr-1 text-red-500" />
              YOUTUBE STATUS
            </label>
            <select
              value={filters.youtube_filter}
              onChange={(e) => handleFilterChange('youtube_filter', e.target.value)}
              className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red text-sm"
            >
              <option value="">All YouTube Statuses</option>
              <option value="has_channel">Has YouTube Channel</option>
              <option value="no_channel">No YouTube Channel</option>
              <option value="high_potential">High YouTube Potential</option>
              <option value="underperforming">Underperforming YouTube</option>
              <option value="active_uploaders">Active Uploaders</option>
            </select>
          </div>
        </div>

        {/* Score Range */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-prism-black mb-1 tracking-wide">
              MIN SCORE
            </label>
            <input
              type="number"
              value={filters.min_score}
              onChange={(e) => handleFilterChange('min_score', e.target.value)}
              placeholder="0"
              min="0"
              max="100"
              className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red text-sm font-mono"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-prism-black mb-1 tracking-wide">
              MAX SCORE
            </label>
            <input
              type="number"
              value={filters.max_score}
              onChange={(e) => handleFilterChange('max_score', e.target.value)}
              placeholder="100"
              min="0"
              max="100"
              className="block w-full px-3 py-2 border border-prism-light-gray rounded-md shadow-sm focus:outline-none focus:ring-prism-red focus:border-prism-red text-sm font-mono"
            />
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-prism-medium-gray">
            Showing <span className="font-mono">{leads.length}</span> of <span className="font-mono">{pagination.total}</span> leads
          </p>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-prism-medium-gray">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border-prism-light-gray rounded-md focus:ring-prism-red focus:border-prism-red"
            >
              <option value="total_score">Score</option>
              <option value="name">Name</option>
              <option value="created_at">Date Added</option>
              <option value="youtube_subscribers">YouTube Subscribers</option>
            </select>
          </div>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg shadow-sm border border-prism-light-gray overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-prism-light-gray">
            <thead className="bg-prism-light-gray">
              <tr>
                <th 
                  onClick={() => handleSort('name')}
                  className="px-6 py-3 text-left text-xs font-medium text-prism-charcoal-gray uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    ARTIST
                    {sortBy === 'name' && (
                      sortOrder === 'desc' ? <ChevronDown className="ml-1 h-3 w-3" /> : <ChevronUp className="ml-1 h-3 w-3" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-prism-charcoal-gray uppercase tracking-wider">
                  REGION
                </th>
                <th 
                  onClick={() => handleSort('total_score')}
                  className="px-6 py-3 text-left text-xs font-medium text-prism-charcoal-gray uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    SCORE
                    {sortBy === 'total_score' && (
                      sortOrder === 'desc' ? <ChevronDown className="ml-1 h-3 w-3" /> : <ChevronUp className="ml-1 h-3 w-3" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-prism-charcoal-gray uppercase tracking-wider">
                  <Youtube className="inline h-4 w-4 mr-1 text-red-500" />
                  YOUTUBE
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-prism-charcoal-gray uppercase tracking-wider">
                  STATUS
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-prism-charcoal-gray uppercase tracking-wider">
                  ACTIONS
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-prism-light-gray">
              {leads.map((lead) => (
                <React.Fragment key={lead.id}>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-prism-light-gray flex items-center justify-center">
                            <Music className="h-5 w-5 text-prism-charcoal-gray" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-prism-black">
                            {lead.name}
                          </div>
                          <div className="text-sm text-prism-medium-gray">
                            {lead.genre || 'Unknown Genre'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-prism-black">
                        {lead.country || 'Unknown'}
                      </div>
                      <div className="text-sm text-prism-medium-gray">
                        {lead.region?.replace('_', ' ') || 'Unknown Region'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-lg font-semibold text-prism-black mr-2 font-mono">
                          {lead.total_score?.toFixed(1) || 0}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getTierColor(lead.lead_tier)}`}>
                          TIER {lead.lead_tier || 'D'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {lead.youtube_summary?.has_channel ? (
                        <div className="text-sm">
                          <div className="flex items-center text-green-600">
                            <Youtube className="h-4 w-4 mr-1" />
                            <span className="font-mono">{(lead.youtube_summary.subscribers || 0).toLocaleString()}</span> subs
                          </div>
                          <div className="text-xs text-prism-medium-gray">
                            {lead.youtube_summary.growth_potential || 'Unknown potential'}
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-prism-medium-gray">
                          <div className="flex items-center">
                            <Youtube className="h-4 w-4 mr-1 text-prism-charcoal-gray" />
                            No channel
                          </div>
                          <div className="text-xs text-red-600">
                            Opportunity!
                          </div>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={lead.outreach_status || 'not_contacted'}
                        onChange={(e) => updateOutreachStatus(lead.id, e.target.value)}
                        className={`text-xs rounded-full px-2 py-1 font-medium border-0 ${getOutreachStatusColor(lead.outreach_status)}`}
                      >
                        <option value="not_contacted">Not Contacted</option>
                        <option value="contacted">Contacted</option>
                        <option value="responded">Responded</option>
                        <option value="interested">Interested</option>
                        <option value="not_interested">Not Interested</option>
                        <option value="converted">Converted</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => setExpandedLead(expandedLead === lead.id ? null : lead.id)}
                        className="text-prism-red hover:text-red-700 mr-3"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {lead.contact_email && (
                        <a
                          href={`mailto:${lead.contact_email}`}
                          className="text-green-600 hover:text-green-700 mr-3"
                        >
                          <Mail className="h-4 w-4" />
                        </a>
                      )}
                      {lead.website && (
                        <a
                          href={lead.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-prism-charcoal-gray hover:text-prism-black"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </td>
                  </tr>
                  
                  {/* Expanded Details */}
                  {expandedLead === lead.id && (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 bg-prism-light-gray">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                          {/* Contact Information */}
                          <div>
                            <h4 className="font-medium text-prism-black mb-2 tracking-wide">CONTACT INFORMATION</h4>
                            <div className="space-y-1 text-sm">
                              {lead.contact_email && (
                                <div className="flex items-center">
                                  <Mail className="h-4 w-4 mr-2 text-prism-charcoal-gray" />
                                  <a href={`mailto:${lead.contact_email}`} className="text-prism-red hover:underline">
                                    {lead.contact_email}
                                  </a>
                                </div>
                              )}
                              {lead.website && (
                                <div className="flex items-center">
                                  <Globe className="h-4 w-4 mr-2 text-prism-charcoal-gray" />
                                  <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-prism-red hover:underline">
                                    Website
                                  </a>
                                </div>
                              )}
                              {lead.social_handles && Object.keys(lead.social_handles).length > 0 && (
                                <div className="mt-2">
                                  <div className="text-xs text-prism-medium-gray mb-1 tracking-wide">SOCIAL MEDIA:</div>
                                  {Object.entries(lead.social_handles).map(([platform, handle]) => (
                                    <div key={platform} className="text-xs text-prism-medium-gray">
                                      {platform}: {handle}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Metrics */}
                          <div>
                            <h4 className="font-medium text-prism-black mb-2 tracking-wide">METRICS</h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-prism-medium-gray">Monthly Listeners:</span>
                                <span className="font-medium font-mono">{(lead.monthly_listeners || 0).toLocaleString()}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-prism-medium-gray">Independence:</span>
                                <span className="font-medium font-mono">{lead.independence_score || 0}/100</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-prism-medium-gray">Opportunity:</span>
                                <span className="font-medium font-mono">{lead.opportunity_score || 0}/100</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-prism-medium-gray">Geographic:</span>
                                <span className="font-medium font-mono">{lead.geographic_score || 0}/100</span>
                              </div>
                            </div>
                          </div>

                          {/* YouTube Details */}
                          <div>
                            <h4 className="font-medium text-prism-black mb-2 flex items-center tracking-wide">
                              <Youtube className="h-4 w-4 mr-1 text-red-500" />
                              YOUTUBE DETAILS
                            </h4>
                            {lead.youtube_summary?.has_channel ? (
                              <div className="space-y-1 text-sm">
                                <div className="flex justify-between">
                                  <span className="text-prism-medium-gray">Subscribers:</span>
                                  <span className="font-medium font-mono">{(lead.youtube_summary.subscribers || 0).toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-prism-medium-gray">Total Views:</span>
                                  <span className="font-medium font-mono">{(lead.youtube_summary.total_views || 0).toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-prism-medium-gray">Videos:</span>
                                  <span className="font-medium font-mono">{lead.youtube_summary.video_count || 0}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-prism-medium-gray">Upload Frequency:</span>
                                  <span className="font-medium">{lead.youtube_summary.upload_frequency || 'Unknown'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-prism-medium-gray">Growth Potential:</span>
                                  <span className="font-medium">{lead.youtube_summary.growth_potential || 'Unknown'}</span>
                                </div>
                                {lead.youtube_summary.channel_url && (
                                  <div className="mt-2">
                                    <a 
                                      href={lead.youtube_summary.channel_url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="text-red-600 hover:underline text-xs flex items-center"
                                    >
                                      <Youtube className="h-3 w-3 mr-1" />
                                      View Channel
                                    </a>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="text-sm text-prism-medium-gray">
                                <div className="flex items-center text-yellow-600">
                                  <TrendingUp className="h-4 w-4 mr-1" />
                                  Major YouTube Opportunity
                                </div>
                                <p className="text-xs mt-1">
                                  Artist has <span className="font-mono">{(lead.monthly_listeners || 0).toLocaleString()}</span> Spotify listeners but no YouTube presence.
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {pagination.total > pagination.limit && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-prism-light-gray">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPagination(prev => ({ 
                  ...prev, 
                  offset: Math.max(0, prev.offset - prev.limit) 
                }))}
                disabled={pagination.offset === 0}
                className="relative inline-flex items-center px-4 py-2 border border-prism-light-gray text-sm font-medium rounded-md text-prism-medium-gray bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPagination(prev => ({ 
                  ...prev, 
                  offset: prev.offset + prev.limit 
                }))}
                disabled={!pagination.has_more}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-prism-light-gray text-sm font-medium rounded-md text-prism-medium-gray bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

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

const SettingsComponent = () => {
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
          <Settings className="h-8 w-8 mr-3 text-prism-charcoal-gray" />
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
          <Settings className="h-5 w-5 mr-2 text-prism-charcoal-gray" />
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

const App = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeRoute, setActiveRoute] = useState('dashboard');

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const status = await response.json();
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
    { id: 'settings', label: 'Settings', icon: Settings, component: SettingsComponent }
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-prism-red mx-auto mb-4"></div>
          <p className="text-prism-medium-gray">Loading Prism Analytics Engine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-prism-light-gray">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <PrismLogo className="h-10 w-10" />
              <div>
                <h1 className="text-xl font-bold text-prism-black tracking-wider">
                  P R I S M
                  <span className="text-xs text-prism-charcoal-gray ml-2 font-normal tracking-normal">
                    ANALYTICS ENGINE
                  </span>
                </h1>
                <p className="text-sm text-prism-medium-gray">
                  Transforming music industry data into actionable insights
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
                  <span className="text-sm text-prism-medium-gray font-mono">
                    {systemStatus.database_status === 'connected' ? 'SYSTEM ONLINE' : 'SYSTEM ISSUES'}
                  </span>
                  
                  {/* YouTube Integration Status */}
                  {systemStatus.youtube_integration && (
                    <div className="flex items-center space-x-1 ml-4">
                      <Youtube className={`h-4 w-4 ${
                        systemStatus.youtube_integration.status === 'available' 
                          ? 'text-red-500' 
                          : 'text-prism-charcoal-gray'
                      }`} />
                      <span className="text-xs text-prism-medium-gray tracking-wide">
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
        <nav className="w-64 bg-white shadow-sm min-h-screen border-r border-prism-light-gray">
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
                        ? 'bg-red-50 text-prism-red border border-red-200'
                        : 'text-prism-medium-gray hover:bg-prism-light-gray hover:text-prism-black'
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
            <div className="p-4 border-t border-prism-light-gray">
              <h3 className="text-xs font-semibold text-prism-charcoal-gray uppercase tracking-wide mb-3">
                API STATUS
              </h3>
              <div className="space-y-2">
                {Object.entries(systemStatus.rate_limits || {}).map(([api, status]) => (
                  <div key={api} className="flex items-center justify-between text-xs">
                    <span className="text-prism-medium-gray capitalize tracking-wide">{api.toUpperCase()}</span>
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
              <PrismLogo className="h-6 w-6 mx-auto mb-2 opacity-60" />
              <p className="text-xs text-prism-charcoal-gray tracking-wider">
                PRECISE DIGITAL
              </p>
              <p className="text-xs text-prism-medium-gray">
                Analytics Engine v1.0
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