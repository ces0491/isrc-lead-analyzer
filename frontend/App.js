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

// Component imports will be created
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard</h2>
        <p className="text-gray-600">Overview of your lead generation activities</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Artists</p>
              <p className="text-2xl font-semibold text-gray-900">
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
              <p className="text-sm font-medium text-gray-500">A-Tier Leads</p>
              <p className="text-2xl font-semibold text-gray-900">
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
              <p className="text-sm font-medium text-gray-500">YouTube Channels</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.youtube_statistics?.artists_with_youtube || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BarChart3 className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg. Score</p>
              <p className="text-2xl font-semibold text-gray-900">
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
              <h3 className="text-lg font-semibold text-gray-900">YouTube Integration</h3>
              <p className="text-sm text-gray-600 mt-1">
                {systemStatus.youtube_integration.api_key_configured ? (
                  <>
                    <span className="text-green-600 font-medium">Active</span> - 
                    Quota used today: {systemStatus.youtube_integration.daily_quota_used || 0} / {systemStatus.youtube_integration.daily_quota_limit || 10000}
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
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Distribution by Tier</h3>
        <div className="space-y-3">
          {['A', 'B', 'C', 'D'].map(tier => {
            const count = stats?.tier_distribution?.[tier] || 0;
            const total = stats?.total_artists || 1;
            const percentage = (count / total) * 100;
            
            return (
              <div key={tier} className="flex items-center">
                <div className="w-16 text-sm font-medium text-gray-700">Tier {tier}</div>
                <div className="flex-1 mx-4">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        tier === 'A' ? 'bg-green-500' :
                        tier === 'B' ? 'bg-blue-500' :
                        tier === 'C' ? 'bg-yellow-500' : 'bg-gray-400'
                      }`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-sm text-gray-600 text-right">
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Bulk Processing</h2>
        <p className="text-gray-600">Process multiple ISRCs with YouTube integration</p>
      </div>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload ISRC File</h3>
        
        {!file ? (
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Drop your CSV or TXT file here
            </p>
            <p className="text-sm text-gray-600 mb-4">
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
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
            >
              <Upload className="h-4 w-4 mr-2" />
              Choose File
            </label>
          </div>
        ) : (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-600">
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
              <div className="mt-4 p-3 bg-gray-50 rounded-md">
                <p className="text-sm font-medium text-gray-700 mb-2">Preview:</p>
                <div className="text-xs text-gray-600 space-y-1">
                  {isrcs.slice(0, 5).map((isrc, index) => (
                    <div key={index}>{isrc}</div>
                  ))}
                  {isrcs.length > 5 && (
                    <div className="text-gray-500">... and {isrcs.length - 5} more</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Processing Settings */}
      {isrcs.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Batch Size
              </label>
              <select
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value={5}>5 ISRCs per batch (Slower, more reliable)</option>
                <option value={10}>10 ISRCs per batch (Recommended)</option>
                <option value={20}>20 ISRCs per batch (Faster, may hit rate limits)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Smaller batches are more reliable but slower
              </p>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeYoutube}
                  onChange={(e) => setIncludeYoutube(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700 flex items-center">
                  <Youtube className="h-4 w-4 mr-1 text-red-500" />
                  Include YouTube data collection
                </span>
              </label>
              <p className="text-xs text-gray-500 mt-1 ml-6">
                Collects YouTube channel and video data for enhanced scoring
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Ready to process {isrcs.length} ISRCs
              {includeYoutube && ' with YouTube integration'}
            </div>
            <button
              onClick={startBulkProcessing}
              disabled={processing || isrcs.length === 0}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </div>
              ) : (
                <div className="flex items-center">
                  <Play className="h-4 w-4 mr-2" />
                  Start Processing
                </div>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Processing Progress */}
      {processing && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Progress</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Processing ISRCs...</span>
                <span>{progress}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="h-4 w-4 mr-2" />
              This may take several minutes depending on the number of ISRCs and API rate limits.
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Processing Results</h3>
            {results.successful > 0 && (
              <button
                onClick={exportResults}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
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
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Total</span>
                  </div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {results.total_processed || 0}
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Successful</span>
                  </div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {results.successful || 0}
                  </p>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Failed</span>
                  </div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {results.failed || 0}
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Clock className="h-5 w-5 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Success Rate</span>
                  </div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {results.success_rate?.toFixed(1) || 0}%
                  </p>
                </div>
              </div>

              {/* YouTube Statistics */}
              {includeYoutube && results.youtube_statistics && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                    <Youtube className="h-4 w-4 mr-2 text-red-600" />
                    YouTube Integration Results
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Artists with YouTube:</span>
                      <span className="ml-2 font-medium">
                        {results.youtube_statistics.artists_with_youtube || 0}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">YouTube data collected:</span>
                      <span className="ml-2 font-medium">
                        {results.youtube_statistics.youtube_data_collected || 0}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Total subscribers:</span>
                      <span className="ml-2 font-medium">
                        {(results.youtube_statistics.total_youtube_subscribers || 0).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Processing Time */}
              <div className="text-sm text-gray-600">
                Processing completed in {results.total_time}s
                {results.average_time_per_isrc && (
                  <span> (avg: {results.average_time_per_isrc}s per ISRC)</span>
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
      case 'B': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'C': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'D': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getOutreachStatusColor = (status) => {
    switch (status) {
      case 'not_contacted': return 'bg-gray-100 text-gray-800';
      case 'contacted': return 'bg-blue-100 text-blue-800';
      case 'responded': return 'bg-yellow-100 text-yellow-800';
      case 'interested': return 'bg-green-100 text-green-800';
      case 'not_interested': return 'bg-red-100 text-red-800';
      case 'converted': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && leads.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading leads...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Leads Database</h2>
          <p className="text-gray-600">Manage and track your music industry leads with YouTube insights</p>
        </div>
        <button
          onClick={exportLeads}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filters
          </h3>
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear All
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search Artists
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Artist name..."
                className="pl-10 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            </div>
          </div>

          {/* Tier Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lead Tier
            </label>
            <select
              value={filters.tier}
              onChange={(e) => handleFilterChange('tier', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Region
            </label>
            <select
              value={filters.region}
              onChange={(e) => handleFilterChange('region', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Youtube className="inline h-4 w-4 mr-1 text-red-500" />
              YouTube Status
            </label>
            <select
              value={filters.youtube_filter}
              onChange={(e) => handleFilterChange('youtube_filter', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Score
            </label>
            <input
              type="number"
              value={filters.min_score}
              onChange={(e) => handleFilterChange('min_score', e.target.value)}
              placeholder="0"
              min="0"
              max="100"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Score
            </label>
            <input
              type="number"
              value={filters.max_score}
              onChange={(e) => handleFilterChange('max_score', e.target.value)}
              placeholder="100"
              min="0"
              max="100"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {leads.length} of {pagination.total} leads
          </p>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border-gray-300 rounded-md"
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
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  onClick={() => handleSort('name')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Artist
                    {sortBy === 'name' && (
                      sortOrder === 'desc' ? <ChevronDown className="ml-1 h-3 w-3" /> : <ChevronUp className="ml-1 h-3 w-3" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Region
                </th>
                <th 
                  onClick={() => handleSort('total_score')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Score
                    {sortBy === 'total_score' && (
                      sortOrder === 'desc' ? <ChevronDown className="ml-1 h-3 w-3" /> : <ChevronUp className="ml-1 h-3 w-3" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <Youtube className="inline h-4 w-4 mr-1 text-red-500" />
                  YouTube
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {leads.map((lead) => (
                <React.Fragment key={lead.id}>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                            <Music className="h-5 w-5 text-gray-500" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {lead.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {lead.genre || 'Unknown Genre'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {lead.country || 'Unknown'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {lead.region?.replace('_', ' ') || 'Unknown Region'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-lg font-semibold text-gray-900 mr-2">
                          {lead.total_score?.toFixed(1) || 0}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getTierColor(lead.lead_tier)}`}>
                          Tier {lead.lead_tier || 'D'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {lead.youtube_summary?.has_channel ? (
                        <div className="text-sm">
                          <div className="flex items-center text-green-600">
                            <Youtube className="h-4 w-4 mr-1" />
                            {(lead.youtube_summary.subscribers || 0).toLocaleString()} subs
                          </div>
                          <div className="text-xs text-gray-500">
                            {lead.youtube_summary.growth_potential || 'Unknown potential'}
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500">
                          <div className="flex items-center">
                            <Youtube className="h-4 w-4 mr-1 text-gray-400" />
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
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {lead.contact_email && (
                        <a
                          href={`mailto:${lead.contact_email}`}
                          className="text-green-600 hover:text-green-900 mr-3"
                        >
                          <Mail className="h-4 w-4" />
                        </a>
                      )}
                      {lead.website && (
                        <a
                          href={lead.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-600 hover:text-gray-900"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </td>
                  </tr>
                  
                  {/* Expanded Details */}
                  {expandedLead === lead.id && (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 bg-gray-50">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                          {/* Contact Information */}
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Contact Information</h4>
                            <div className="space-y-1 text-sm">
                              {lead.contact_email && (
                                <div className="flex items-center">
                                  <Mail className="h-4 w-4 mr-2 text-gray-400" />
                                  <a href={`mailto:${lead.contact_email}`} className="text-blue-600 hover:underline">
                                    {lead.contact_email}
                                  </a>
                                </div>
                              )}
                              {lead.website && (
                                <div className="flex items-center">
                                  <Globe className="h-4 w-4 mr-2 text-gray-400" />
                                  <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                    Website
                                  </a>
                                </div>
                              )}
                              {lead.social_handles && Object.keys(lead.social_handles).length > 0 && (
                                <div className="mt-2">
                                  <div className="text-xs text-gray-500 mb-1">Social Media:</div>
                                  {Object.entries(lead.social_handles).map(([platform, handle]) => (
                                    <div key={platform} className="text-xs text-gray-600">
                                      {platform}: {handle}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Metrics */}
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Metrics</h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Monthly Listeners:</span>
                                <span className="font-medium">{(lead.monthly_listeners || 0).toLocaleString()}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Independence:</span>
                                <span className="font-medium">{lead.independence_score || 0}/100</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Opportunity:</span>
                                <span className="font-medium">{lead.opportunity_score || 0}/100</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Geographic:</span>
                                <span className="font-medium">{lead.geographic_score || 0}/100</span>
                              </div>
                            </div>
                          </div>

                          {/* YouTube Details */}
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                              <Youtube className="h-4 w-4 mr-1 text-red-500" />
                              YouTube Details
                            </h4>
                            {lead.youtube_summary?.has_channel ? (
                              <div className="space-y-1 text-sm">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Subscribers:</span>
                                  <span className="font-medium">{(lead.youtube_summary.subscribers || 0).toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Total Views:</span>
                                  <span className="font-medium">{(lead.youtube_summary.total_views || 0).toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Videos:</span>
                                  <span className="font-medium">{lead.youtube_summary.video_count || 0}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Upload Frequency:</span>
                                  <span className="font-medium">{lead.youtube_summary.upload_frequency || 'Unknown'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Growth Potential:</span>
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
                              <div className="text-sm text-gray-500">
                                <div className="flex items-center text-yellow-600">
                                  <TrendingUp className="h-4 w-4 mr-1" />
                                  Major YouTube Opportunity
                                </div>
                                <p className="text-xs mt-1">
                                  Artist has {(lead.monthly_listeners || 0).toLocaleString()} Spotify listeners but no YouTube presence.
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
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPagination(prev => ({ 
                  ...prev, 
                  offset: Math.max(0, prev.offset - prev.limit) 
                }))}
                disabled={pagination.offset === 0}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPagination(prev => ({ 
                  ...prev, 
                  offset: prev.offset + prev.limit 
                }))}
                disabled={!pagination.has_more}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">ISRC Analyzer</h2>
        <p className="text-gray-600">Analyze individual tracks and discover lead opportunities</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="isrc" className="block text-sm font-medium text-gray-700 mb-2">
              ISRC Code
            </label>
            <input
              type="text"
              id="isrc"
              value={isrc}
              onChange={(e) => setIsrc(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., USRC17607839"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeYoutube}
                onChange={(e) => setIncludeYoutube(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">Include YouTube data collection</span>
            </label>
          </div>

          <button
            onClick={analyzeISRC}
            disabled={loading || !isrc.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </div>
            ) : (
              'Analyze ISRC'
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
          
          {result.status === 'completed' ? (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Artist Information</h4>
                  <p className="text-lg font-semibold text-blue-600">
                    {result.artist_data?.name || 'Unknown Artist'}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.track_data?.title || 'Unknown Track'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Label: {result.track_data?.label || 'Unknown'}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Lead Score</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-3xl font-bold text-gray-900">
                      {result.scores?.total_score || 0}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      result.scores?.tier === 'A' ? 'bg-green-100 text-green-800' :
                      result.scores?.tier === 'B' ? 'bg-blue-100 text-blue-800' :
                      result.scores?.tier === 'C' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      Tier {result.scores?.tier || 'D'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Confidence: {result.scores?.confidence || 0}%
                  </p>
                </div>
              </div>

              {/* Score Breakdown */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Score Breakdown</h4>
                <div className="space-y-2">
                  {[
                    { label: 'Independence', score: result.scores?.independence_score, color: 'bg-blue-500' },
                    { label: 'Opportunity', score: result.scores?.opportunity_score, color: 'bg-green-500' },
                    { label: 'Geographic', score: result.scores?.geographic_score, color: 'bg-purple-500' }
                  ].map(({ label, score, color }) => (
                    <div key={label} className="flex items-center">
                      <div className="w-24 text-sm text-gray-700">{label}</div>
                      <div className="flex-1 mx-4">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${color}`}
                            style={{ width: `${score || 0}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-12 text-sm text-gray-600 text-right">{score || 0}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* YouTube Integration Results */}
              {result.youtube_integration?.enabled && (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                    <Youtube className="h-4 w-4 mr-2 text-red-600" />
                    YouTube Analysis
                  </h4>
                  {result.youtube_integration.data_found ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-sm text-green-600 font-medium mb-2">✅ YouTube channel found!</p>
                      {/* YouTube channel details would be displayed here */}
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
                <h4 className="font-medium text-gray-900 mb-2">Data Sources</h4>
                <div className="flex flex-wrap gap-2">
                  {result.data_sources_used?.map(source => (
                    <span key={source} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Precise Digital Lead Generation Tool...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Music className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Precise Digital</h1>
                <p className="text-sm text-gray-500">Lead Generation Tool with YouTube Integration</p>
              </div>
            </div>
            
            {/* System Status Indicator */}
            <div className="flex items-center space-x-4">
              {systemStatus && (
                <div className="flex items-center space-x-2">
                  <div className={`h-3 w-3 rounded-full ${
                    systemStatus.database_status === 'connected' ? 'bg-green-400' : 'bg-red-400'
                  }`}></div>
                  <span className="text-sm text-gray-600">
                    {systemStatus.database_status === 'connected' ? 'System Online' : 'System Issues'}
                  </span>
                  
                  {/* YouTube Integration Status */}
                  {systemStatus.youtube_integration && (
                    <div className="flex items-center space-x-1 ml-4">
                      <Youtube className={`h-4 w-4 ${
                        systemStatus.youtube_integration.status === 'available' 
                          ? 'text-red-500' 
                          : 'text-gray-400'
                      }`} />
                      <span className="text-xs text-gray-500">
                        YouTube {systemStatus.youtube_integration.api_key_configured ? 'Active' : 'Disabled'}
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
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left ${
                      activeRoute === item.id
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* API Status Panel */}
          {systemStatus && (
            <div className="p-4 border-t border-gray-200">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
                API Status
              </h3>
              <div className="space-y-2">
                {Object.entries(systemStatus.rate_limits || {}).map(([api, status]) => (
                  <div key={api} className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 capitalize">{api}</span>
                    <span className={`font-medium ${
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
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {renderActiveComponent()}
        </main>
      </div>
    </div>
  );
};

export default App;