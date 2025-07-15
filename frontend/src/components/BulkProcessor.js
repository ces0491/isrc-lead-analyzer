import React, { useState, useCallback } from 'react';
import { 
  Upload, 
  FileText, 
  Download, 
  Play, 
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

  const isValidISRC = useCallback((isrc) => {
    if (!isrc || typeof isrc !== 'string') return false;
    const cleaned = isrc.replace(/[-\s_]/g, '').toUpperCase();
    return cleaned.length === 12 && /^[A-Z]{2}[A-Z0-9]{3}[0-9]{2}[A-Z0-9]{5}$/.test(cleaned);
  }, []);

  // File parsing function
  const parseISRCs = useCallback((content, filename) => {
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
  }, [isValidISRC]);

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
  }, [parseISRCs]);

  // Drag and drop handling
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e) => {
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
  }, [parseISRCs]);

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

export default BulkProcessor;