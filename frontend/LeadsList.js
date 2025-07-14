import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Search, 
  Filter, 
  Download, 
  ExternalLink,
  Youtube,
  Mail,
  Globe,
  Music,
  TrendingUp,
  Users,
  Eye,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

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

export default LeadsList;