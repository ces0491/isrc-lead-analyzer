// src/components/EnhancedTrackViewer.js

import React, { useState } from 'react';
import { 
  Music, 
  User, 
  Disc, 
  Clock, 
  Calendar,
  Award,
  FileText,
  Globe,
  Play,
  Volume2,
  Mic,
  Piano,
  Settings,
  Copyright,
  Eye,
  Download,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const EnhancedTrackViewer = ({ trackData, onClose }) => {
  const [expandedSections, setExpandedSections] = useState({
    credits: true,
    lyrics: false,
    technical: false,
    rights: false,
    platforms: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatDuration = (ms) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      spotify: "🎵",
      apple_music: "🍎",
      youtube_music: "📺",
      amazon_music: "📦",
      deezer: "🎧",
      tidal: "🌊"
    };
    return icons[platform] || "🎶";
  };

  const getConfidenceColor = (score) => {
    if (score >= 90) return "text-green-600";
    if (score >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  if (!trackData) {
    return (
      <div className="text-center py-12">
        <Music className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No track data available</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-4">
              <div className="h-16 w-16 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                <Music className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{trackData.track_data?.title || 'Unknown Track'}</h1>
                <p className="text-lg text-gray-600">by {trackData.track_data?.artist || 'Unknown Artist'}</p>
                <p className="text-sm text-gray-500">from "{trackData.track_data?.album || 'Unknown Album'}"</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <Disc className="h-4 w-4 text-gray-500" />
                <span className="font-mono">{trackData.isrc}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span>{formatDuration(trackData.track_data?.duration_ms || 0)}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span>{trackData.track_data?.release_date ? new Date(trackData.track_data.release_date).toLocaleDateString() : 'Unknown'}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="h-4 w-4 text-gray-500" />
                <span className={`font-medium ${getConfidenceColor(trackData.confidence_score || 0)}`}>
                  {trackData.confidence_score || 0}% Complete
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <button 
              onClick={() => window.print()}
              className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium tracking-wide"
            >
              <Download className="h-4 w-4 mr-2" />
              EXPORT REPORT
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm font-medium tracking-wide"
              >
                Close
              </button>
            )}
          </div>
        </div>

        {/* Genre and Tags */}
        <div className="mt-4 flex flex-wrap gap-2">
          {trackData.track_data?.genre?.map((genre, index) => (
            <span key={index} className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
              {genre}
            </span>
          ))}
          {trackData.track_data?.tags?.map((tag, index) => (
            <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
              #{tag}
            </span>
          ))}
        </div>
      </div>

      {/* Credits Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('credits')}
          className="w-full flex items-center justify-between p-6 hover:bg-gray-50"
        >
          <div className="flex items-center space-x-2">
            <User className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900 tracking-wide">CREDITS & PERSONNEL</h2>
          </div>
          {expandedSections.credits ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
        </button>
        
        {expandedSections.credits && (
          <div className="px-6 pb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Composers */}
              {trackData.credits?.composers?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Piano className="h-4 w-4 mr-2 text-blue-500" />
                    COMPOSERS
                  </h3>
                  <div className="space-y-2">
                    {trackData.credits.composers.map((composer, index) => (
                      <div key={index} className="p-3 bg-blue-50 rounded-lg">
                        <div className="font-medium text-blue-900">{composer.name}</div>
                        <div className="text-sm text-blue-700">{composer.role}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Lyricists */}
              {trackData.credits?.lyricists?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <FileText className="h-4 w-4 mr-2 text-green-500" />
                    LYRICISTS
                  </h3>
                  <div className="space-y-2">
                    {trackData.credits.lyricists.map((lyricist, index) => (
                      <div key={index} className="p-3 bg-green-50 rounded-lg">
                        <div className="font-medium text-green-900">{lyricist.name}</div>
                        <div className="text-sm text-green-700">{lyricist.role}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Producers */}
              {trackData.credits?.producers?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Settings className="h-4 w-4 mr-2 text-red-500" />
                    PRODUCERS
                  </h3>
                  <div className="space-y-2">
                    {trackData.credits.producers.map((producer, index) => (
                      <div key={index} className="p-3 bg-red-50 rounded-lg">
                        <div className="font-medium text-red-900">{producer.name}</div>
                        <div className="text-sm text-red-700">{producer.role}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Performers */}
              {trackData.credits?.performers?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Mic className="h-4 w-4 mr-2 text-purple-500" />
                    PERFORMERS
                  </h3>
                  <div className="space-y-2">
                    {trackData.credits.performers.map((performer, index) => (
                      <div key={index} className="p-3 bg-purple-50 rounded-lg">
                        <div className="font-medium text-purple-900">{performer.name}</div>
                        <div className="text-sm text-purple-700">{performer.role}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Engineers */}
              {trackData.credits?.engineers?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Volume2 className="h-4 w-4 mr-2 text-orange-500" />
                    ENGINEERS
                  </h3>
                  <div className="space-y-2">
                    {trackData.credits.engineers.map((engineer, index) => (
                      <div key={index} className="p-3 bg-orange-50 rounded-lg">
                        <div className="font-medium text-orange-900">{engineer.name}</div>
                        <div className="text-sm text-orange-700">{engineer.role}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Other Credits */}
              {trackData.credits?.other_credits?.length > 0 && (
                <div className="md:col-span-2">
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center tracking-wide">
                    <Award className="h-4 w-4 mr-2 text-gray-500" />
                    ADDITIONAL CREDITS
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {trackData.credits.other_credits.map((credit, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900">{credit.name}</div>
                        <div className="text-sm text-gray-600">{credit.role}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Lyrics Section */}
      {trackData.lyrics?.content && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <button
            onClick={() => toggleSection('lyrics')}
            className="w-full flex items-center justify-between p-6 hover:bg-gray-50"
          >
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-gray-500" />
              <h2 className="text-lg font-semibold text-gray-900 tracking-wide">LYRICS & CONTENT</h2>
              {trackData.lyrics?.source && (
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                  {trackData.lyrics.source}
                </span>
              )}
            </div>
            {expandedSections.lyrics ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
          
          {expandedSections.lyrics && (
            <div className="px-6 pb-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed">
                      {trackData.lyrics.content}
                    </pre>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 tracking-wide">LYRICS INFORMATION</h4>
                    <div className="space-y-2 text-sm">
                      {trackData.lyrics.language && (
                        <div>
                          <span className="text-gray-600">Language:</span>
                          <span className="ml-2 font-medium">{trackData.lyrics.language.toUpperCase()}</span>
                        </div>
                      )}
                      {trackData.lyrics.source && (
                        <div>
                          <span className="text-gray-600">Source:</span>
                          <span className="ml-2 font-medium capitalize">{trackData.lyrics.source}</span>
                        </div>
                      )}
                      {trackData.lyrics.copyright && (
                        <div>
                          <span className="text-gray-600">Copyright:</span>
                          <span className="ml-2 font-medium text-xs">{trackData.lyrics.copyright}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Technical Details Section */}
      {trackData.technical && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <button
            onClick={() => toggleSection('technical')}
            className="w-full flex items-center justify-between p-6 hover:bg-gray-50"
          >
            <div className="flex items-center space-x-2">
              <Settings className="h-5 w-5 text-gray-500" />
              <h2 className="text-lg font-semibold text-gray-900 tracking-wide">TECHNICAL DETAILS</h2>
            </div>
            {expandedSections.technical ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
          
          {expandedSections.technical && (
            <div className="px-6 pb-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {trackData.technical.key && (
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-900">{trackData.technical.key}</div>
                    <div className="text-sm text-blue-700">Key Signature</div>
                  </div>
                )}
                {trackData.technical.tempo_bpm && (
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-900">{trackData.technical.tempo_bpm}</div>
                    <div className="text-sm text-green-700">BPM</div>
                  </div>
                )}
                {trackData.technical.time_signature && (
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-900">{trackData.technical.time_signature}</div>
                    <div className="text-sm text-purple-700">Time Signature</div>
                  </div>
                )}
                {trackData.technical.loudness && (
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-900">{trackData.technical.loudness}</div>
                    <div className="text-sm text-orange-700">Loudness (dB)</div>
                  </div>
                )}
              </div>
              
              {/* Audio Analysis Metrics */}
              {(trackData.technical.energy || trackData.technical.danceability || trackData.technical.valence || trackData.technical.acousticness) && (
                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: "Energy", value: trackData.technical.energy, color: "bg-red-200" },
                    { label: "Danceability", value: trackData.technical.danceability, color: "bg-yellow-200" },
                    { label: "Valence", value: trackData.technical.valence, color: "bg-green-200" },
                    { label: "Acousticness", value: trackData.technical.acousticness, color: "bg-blue-200" }
                  ].filter(metric => metric.value !== null && metric.value !== undefined).map((metric, index) => (
                    <div key={index} className="p-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium">{metric.label}</span>
                        <span>{Math.round(metric.value * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${metric.color}`}
                          style={{ width: `${metric.value * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Recording Information */}
              {(trackData.recording_info?.location || trackData.recording_info?.date) && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2 tracking-wide">RECORDING INFORMATION</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {trackData.recording_info.date && (
                      <div>
                        <span className="text-gray-600">Recording Date:</span>
                        <span className="ml-2 font-medium">{new Date(trackData.recording_info.date).toLocaleDateString()}</span>
                      </div>
                    )}
                    {trackData.recording_info.location && (
                      <div>
                        <span className="text-gray-600">Recording Location:</span>
                        <span className="ml-2 font-medium">{trackData.recording_info.location}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Rights & Publishing Section */}
      {trackData.rights && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <button
            onClick={() => toggleSection('rights')}
            className="w-full flex items-center justify-between p-6 hover:bg-gray-50"
          >
            <div className="flex items-center space-x-2">
              <Copyright className="h-5 w-5 text-gray-500" />
              <h2 className="text-lg font-semibold text-gray-900 tracking-wide">RIGHTS & PUBLISHING</h2>
            </div>
            {expandedSections.rights ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
          
          {expandedSections.rights && (
            <div className="px-6 pb-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3 tracking-wide">COPYRIGHT INFORMATION</h4>
                  <div className="space-y-3">
                    {trackData.rights.copyright_info && Object.entries(trackData.rights.copyright_info).map(([type, info], index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900 capitalize">{type.replace('_', ' ')}</div>
                        <div className="text-sm text-gray-600 font-mono">{info}</div>
                      </div>
                    ))}
                  </div>
                  
                  {trackData.rights.publisher && (
                    <div className="mt-4">
                      <div className="text-sm text-gray-600">Publisher:</div>
                      <div className="font-medium text-gray-900">{trackData.rights.publisher}</div>
                    </div>
                  )}
                  {trackData.rights.record_label && (
                    <div className="mt-2">
                      <div className="text-sm text-gray-600">Record Label:</div>
                      <div className="font-medium text-gray-900">{trackData.rights.record_label}</div>
                    </div>
                  )}
                </div>
                
                {trackData.rights.publishing_splits?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 tracking-wide">PUBLISHING SPLITS</h4>
                    <div className="space-y-2">
                      {trackData.rights.publishing_splits.map((split, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                          <div>
                            <div className="font-medium text-green-900">{split.entity}</div>
                            <div className="text-sm text-green-700">{split.role}</div>
                          </div>
                          <div className="text-lg font-bold text-green-900">{split.percentage}%</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Platform Availability Section */}
      {trackData.platform_availability && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <button
            onClick={() => toggleSection('platforms')}
            className="w-full flex items-center justify-between p-6 hover:bg-gray-50"
          >
            <div className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-gray-500" />
              <h2 className="text-lg font-semibold text-gray-900 tracking-wide">PLATFORM AVAILABILITY</h2>
            </div>
            {expandedSections.platforms ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
          
          {expandedSections.platforms && (
            <div className="px-6 pb-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(trackData.platform_availability).map(([platform, available], index) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${
                    available 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-gray-200 bg-gray-50'
                  }`}>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{getPlatformIcon(platform)}</span>
                      <div>
                        <div className="font-medium text-gray-900 capitalize">
                          {platform.replace('_', ' ')}
                        </div>
                        <div className={`text-sm ${
                          available ? 'text-green-600' : 'text-gray-500'
                        }`}>
                          {available ? 'Available' : 'Not Available'}
                        </div>
                        {available && trackData.platform_ids?.[platform] && (
                          <div className="text-xs text-gray-500 font-mono">
                            ID: {trackData.platform_ids[platform]}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Data Sources Footer */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Data Sources:</span>
            <div className="flex space-x-2">
              {trackData.data_sources_used?.map((source, index) => (
                <span key={index} className="px-2 py-1 bg-white text-gray-700 rounded text-xs font-medium">
                  {source}
                </span>
              ))}
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Generated: {trackData.timestamp ? new Date(trackData.timestamp).toLocaleString() : 'Unknown'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedTrackViewer;