import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Search, FileText, Loader2 } from 'lucide-react';
import EnhancedTrackViewer from './EnhancedTrackViewer';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const TrackAnalysisPage = () => {
  const { isrc } = useParams();
  const navigate = useNavigate();
  const [trackData, setTrackData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [inputIsrc, setInputIsrc] = useState(isrc || '');

  useEffect(() => {
    if (isrc) {
      fetchEnhancedTrackData(isrc);
    } else {
      setLoading(false);
    }
  }, [isrc]);

  const validateISRC = (isrcCode) => {
    if (!isrcCode) return false;
    const cleaned = isrcCode.replace(/[-\s]/g, '').toUpperCase();
    return cleaned.length === 12 && /^[A-Z]{2}[A-Z0-9]{3}[0-9]{2}[A-Z0-9]{5}$/.test(cleaned);
  };

  const formatISRC = (isrcCode) => {
    if (!isrcCode) return '';
    return isrcCode.replace(/[-\s]/g, '').toUpperCase();
  };

  const fetchEnhancedTrackData = async (isrcCode) => {
    try {
      setLoading(true);
      setError(null);
      
      const cleanIsrc = formatISRC(isrcCode);
      
      if (!validateISRC(cleanIsrc)) {
        throw new Error('Invalid ISRC format. Expected format: CC-XXX-YY-NNNNN');
      }

      const response = await fetch(`${API_BASE_URL}/track/${cleanIsrc}/enhanced`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Track not found. Please verify the ISRC and try again.');
        }
        throw new Error(`Failed to fetch track data: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setTrackData(data);
    } catch (err) {
      console.error('Error fetching track data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeIsrc = () => {
    const cleanIsrc = formatISRC(inputIsrc);
    if (validateISRC(cleanIsrc)) {
      navigate(`/track/${cleanIsrc}`);
      fetchEnhancedTrackData(cleanIsrc);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAnalyzeIsrc();
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-wide">
              ENHANCED TRACK ANALYSIS
            </h1>
            <p className="text-gray-600 mt-2">
              Comprehensive track metadata for distribution teams
            </p>
          </div>
          <button
            onClick={() => navigate('/analyze')}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analyzer
          </button>
        </div>

        <div className="text-center py-24">
          <Loader2 className="h-12 w-12 text-red-600 mx-auto mb-6 animate-spin" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Loading Enhanced Track Analysis
          </h2>
          <p className="text-gray-600 mb-4">
            Gathering comprehensive metadata for ISRC: <span className="font-mono font-semibold">{isrc}</span>
          </p>
          <div className="max-w-md mx-auto">
            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
              <div className="bg-red-600 h-full rounded-full animate-pulse" style={{ width: '70%' }}></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Collecting data from multiple sources...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-wide">
              ENHANCED TRACK ANALYSIS
            </h1>
            <p className="text-gray-600 mt-2">
              Comprehensive track metadata for distribution teams
            </p>
          </div>
          <button
            onClick={() => navigate('/analyze')}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analyzer
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <div className="bg-red-100 rounded-full p-3 mx-auto w-16 h-16 flex items-center justify-center mb-4">
              <FileText className="h-8 w-8 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Analysis Error
            </h2>
            <p className="text-red-600 mb-6 max-w-md mx-auto">
              {error}
            </p>
            
            {/* ISRC Input for Retry */}
            <div className="max-w-md mx-auto mb-6">
              <label htmlFor="retry-isrc" className="block text-sm font-medium text-gray-700 mb-2">
                Try Different ISRC
              </label>
              <div className="flex">
                <input
                  type="text"
                  id="retry-isrc"
                  value={inputIsrc}
                  onChange={(e) => setInputIsrc(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g., USRC17607839"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 font-mono"
                />
                <button
                  onClick={handleAnalyzeIsrc}
                  disabled={!validateISRC(formatISRC(inputIsrc))}
                  className="px-4 py-2 bg-red-600 text-white rounded-r-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Search className="h-4 w-4" />
                </button>
              </div>
              {inputIsrc && !validateISRC(formatISRC(inputIsrc)) && (
                <p className="text-sm text-red-600 mt-1">
                  Invalid ISRC format. Expected: CC-XXX-YY-NNNNN
                </p>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button 
                onClick={() => isrc && fetchEnhancedTrackData(isrc)}
                className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Retry Analysis
              </button>
              <button
                onClick={() => navigate('/analyze')}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Back to Analyzer
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No ISRC provided state
  if (!isrc && !trackData) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-wide">
              ENHANCED TRACK ANALYSIS
            </h1>
            <p className="text-gray-600 mt-2">
              Comprehensive track metadata for distribution teams
            </p>
          </div>
          <button
            onClick={() => navigate('/analyze')}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analyzer
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center max-w-md mx-auto">
            <div className="bg-purple-100 rounded-full p-4 mx-auto w-20 h-20 flex items-center justify-center mb-6">
              <Search className="h-10 w-10 text-purple-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Enter ISRC for Enhanced Analysis
            </h2>
            <p className="text-gray-600 mb-6">
              Provide an ISRC code to get comprehensive track metadata including credits, lyrics, technical details, and rights information.
            </p>
            
            <div className="mb-6">
              <label htmlFor="isrc-input" className="block text-sm font-medium text-gray-700 mb-2">
                ISRC Code
              </label>
              <div className="flex">
                <input
                  type="text"
                  id="isrc-input"
                  value={inputIsrc}
                  onChange={(e) => setInputIsrc(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g., USRC17607839 or US-RC1-76-07839"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 font-mono"
                />
                <button
                  onClick={handleAnalyzeIsrc}
                  disabled={!validateISRC(formatISRC(inputIsrc))}
                  className="px-4 py-2 bg-purple-600 text-white rounded-r-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Search className="h-4 w-4" />
                </button>
              </div>
              {inputIsrc && !validateISRC(formatISRC(inputIsrc)) && (
                <p className="text-sm text-red-600 mt-1">
                  Invalid ISRC format. Expected format: CC-XXX-YY-NNNNN
                </p>
              )}
            </div>

            <div className="bg-gray-50 rounded-lg p-4 text-left">
              <h3 className="font-medium text-gray-900 mb-2">Enhanced Analysis Includes:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Comprehensive track credits & personnel</li>
                <li>• Full lyrics with copyright information</li>
                <li>• Technical audio analysis & metrics</li>
                <li>• Publishing rights & splits breakdown</li>
                <li>• Platform availability & IDs</li>
                <li>• Recording location & production details</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success state with track data
  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-wide">
            ENHANCED TRACK ANALYSIS
          </h1>
          <p className="text-gray-600 mt-2">
            Comprehensive track metadata for distribution teams
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Quick ISRC Input */}
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inputIsrc}
              onChange={(e) => setInputIsrc(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter different ISRC..."
              className="px-3 py-1 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 font-mono w-40"
            />
            <button
              onClick={handleAnalyzeIsrc}
              disabled={!validateISRC(formatISRC(inputIsrc)) || inputIsrc === isrc}
              className="px-2 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              <Search className="h-3 w-3" />
            </button>
          </div>
          <button
            onClick={() => navigate('/analyze')}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analyzer
          </button>
        </div>
      </div>
      
      {trackData && <EnhancedTrackViewer trackData={trackData} />}
    </div>
  );
};

export default TrackAnalysisPage;