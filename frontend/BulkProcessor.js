import React, { useState, useCallback } from 'react';
import { 
  Upload, 
  FileText, 
  Download, 
  Play, 
  Pause, 
  Youtube,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react';

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

export default BulkProcessor;