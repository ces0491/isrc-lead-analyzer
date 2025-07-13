# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
No authentication required for the current version.

## Rate Limits
The API respects external API rate limits:
- MusicBrainz: 1 request/second
- Spotify: 100 requests/minute  
- Last.fm: 5 requests/second
- **YouTube: 100 requests/minute, 10,000 requests/day** (NEW)

## Endpoints

### Health Check
Check if the API is running including YouTube integration status.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-13T10:30:00Z",
  "version": "1.1.0",
  "youtube_integration": "enabled"
}
```

### System Status
Get system status and rate limit information including YouTube quotas.

```http
GET /api/status
```

**Response:**
```json
{
  "rate_limits": {
    "spotify": {
      "requests_this_minute": 5,
      "minute_limit": 100,
      "minute_remaining": 95
    },
    "youtube": {
      "requests_this_minute": 2,
      "minute_limit": 100,
      "minute_remaining": 98,
      "requests_today": 150,
      "daily_limit": 10000,
      "daily_remaining": 9850
    }
  },
  "processing_stats": {
    "processed": 0,
    "successful": 0,
    "failed": 0
  },
  "youtube_integration": {
    "status": "available",
    "api_key_configured": true,
    "daily_quota_used": 150,
    "daily_quota_limit": 10000
  }
}
```

### Analyze Single ISRC
Analyze a single ISRC and return lead scoring information with YouTube integration.

```http
POST /api/analyze-isrc
```

**Request Body:**
```json
{
  "isrc": "USRC17607839",
  "save_to_db": true,
  "force_refresh": false,
  "include_youtube": true
}
```

**Response:**
```json
{
  "isrc": "USRC17607839",
  "status": "completed",
  "artist_data": {
    "name": "Artist Name",
    "country": "NZ",
    "monthly_listeners": 25000
  },
  "track_data": {
    "title": "Track Title",
    "label": "Label Name",
    "release_date": "2024-01-01"
  },
  "scores": {
    "total_score": 85.5,
    "independence_score": 40,
    "opportunity_score": 35,
    "geographic_score": 30,
    "tier": "A",
    "confidence": 88
  },
  "contacts": [
    {
      "type": "email",
      "value": "contact@artist.com",
      "confidence": 80,
      "source": "website"
    },
    {
      "type": "platform_profile",
      "platform": "youtube",
      "value": "https://youtube.com/channel/UC123456789",
      "confidence": 95,
      "source": "youtube_api",
      "metadata": {
        "channel_title": "Artist Name Official",
        "subscriber_count": 15000
      }
    }
  ],
  "youtube_data": {
    "channel": {
      "channel_id": "UC123456789",
      "title": "Artist Name Official",
      "statistics": {
        "subscriber_count": 15000,
        "view_count": 500000,
        "video_count": 25
      }
    },
    "analytics": {
      "recent_activity": {
        "upload_frequency": "active",
        "videos_last_30_days": 3
      },
      "growth_potential": "high_potential"
    }
  },
  "youtube_integration": {
    "enabled": true,
    "data_found": true,
    "api_status": "available"
  },
  "processing_time": 4.2
}
```

### Bulk Analysis
Analyze multiple ISRCs in batch with YouTube integration.

```http
POST /api/analyze-bulk
```

**Request Body:**
```json
{
  "isrcs": ["USRC17607839", "GBUM71505078"],
  "batch_size": 10,
  "include_youtube": true
}
```

**Response:**
```json
{
  "total_processed": 2,
  "successful": 2,
  "failed": 0,
  "success_rate": 100.0,
  "total_time": 8.4,
  "youtube_statistics": {
    "artists_with_youtube": 1,
    "youtube_data_collected": 1,
    "total_youtube_subscribers": 15000
  },
  "results": [...]
}
```

### Upload ISRCs File
Upload a CSV or TXT file containing ISRCs.

```http
POST /api/upload-isrcs
```

**Request:** `multipart/form-data` with file field

**Response:**
```json
{
  "isrcs": ["USRC17607839", "GBUM71505078"],
  "count": 2,
  "filename": "isrcs.csv",
  "message": "Successfully parsed 2 unique ISRCs"
}
```

### Get Leads
Retrieve filtered list of leads with YouTube filtering options.

```http
GET /api/leads?tier=A&region=new_zealand&youtube_filter=no_channel&limit=20&offset=0
```

**Query Parameters:**
- `tier` (optional): Filter by lead tier (A, B, C, D)
- `region` (optional): Filter by region
- `min_score` (optional): Minimum score threshold
- `max_score` (optional): Maximum score threshold
- **`youtube_filter` (optional): YouTube filter options** (NEW)
  - `has_channel`: Artists with YouTube channels
  - `no_channel`: Artists without YouTube presence
  - `high_potential`: Artists with high YouTube growth potential
  - `underperforming`: YouTube subscribers < 30% of Spotify followers
  - `active_uploaders`: Artists with frequent YouTube uploads
- `limit` (optional): Number of results (default: 50, max: 1000)
- `offset` (optional): Pagination offset (default: 0)
- `sort_by` (optional): Sort field (total_score, name, created_at, youtube_subscribers)
- `sort_order` (optional): Sort direction (asc, desc)

**Response:**
```json
{
  "leads": [
    {
      "id": 1,
      "name": "Artist Name",
      "country": "NZ",
      "region": "new_zealand",
      "total_score": 85.5,
      "lead_tier": "A",
      "monthly_listeners": 50000,
      "outreach_status": "not_contacted",
      "contact_email": "artist@example.com",
      "youtube_summary": {
        "has_channel": true,
        "channel_url": "https://youtube.com/channel/UC123456789",
        "subscribers": 15000,
        "total_views": 500000,
        "video_count": 25,
        "upload_frequency": "active",
        "growth_potential": "high_potential",
        "engagement_rate": 2.5
      }
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_more": false
  },
  "filters_applied": {
    "tier": "A",
    "region": "new_zealand",
    "youtube_filter": "no_channel"
  }
}
```

### Export Leads
Export filtered leads to CSV format with YouTube metrics.

```http
POST /api/export
```

**Request Body:**
```json
{
  "filters": {
    "tier": "A",
    "region": "new_zealand",
    "min_score": 70,
    "youtube_filter": "high_potential"
  }
}
```

**Response:**
```json
{
  "csv_data": "Artist Name,Country,Score,YouTube Channel,YouTube Subscribers...",
  "filename": "precise_digital_leads_20250713.csv",
  "count": 25,
  "generated_at": "2025-07-13T10:30:00Z"
}
```

### Get Artist Details
Get detailed information for a specific artist including YouTube metrics.

```http
GET /api/artist/{artist_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Artist Name",
  "scores": {
    "total_score": 85.5,
    "tier": "A"
  },
  "youtube_metrics": {
    "channel_id": "UC123456789",
    "channel_url": "https://youtube.com/channel/UC123456789",
    "subscribers": 15000,
    "total_views": 500000,
    "video_count": 25,
    "upload_frequency": "active",
    "engagement_rate": 2.5,
    "growth_potential": "high_potential",
    "last_upload": "2025-07-01T00:00:00Z",
    "has_channel": true
  },
  "tracks": [...],
  "contact_attempts": [...]
}
```

### Update Outreach Status
Update the outreach status for an artist.

```http
PUT /api/artist/{artist_id}/outreach
```

**Request Body:**
```json
{
  "status": "contacted",
  "method": "email",
  "notes": "Sent initial inquiry email with YouTube optimization proposal"
}
```

### Dashboard Statistics
Get dashboard statistics and metrics including YouTube data.

```http
GET /api/dashboard/stats
```

**Response:**
```json
{
  "totals": {
    "artists": 150,
    "recent_leads": 25
  },
  "distributions": {
    "tiers": {
      "A": 30,
      "B": 45,
      "C": 60,
      "D": 15
    },
    "regions": {
      "new_zealand": 45,
      "australia": 35,
      "other": 70
    }
  },
  "youtube_statistics": {
    "artists_with_youtube": 85,
    "total_youtube_subscribers": 2500000,
    "avg_youtube_subscribers": 29411,
    "high_potential_channels": 12
  }
}
```

## NEW: YouTube Integration Endpoints

### Test YouTube Integration
Test YouTube API integration for a specific artist.

```http
POST /api/youtube/test
```

**Request Body:**
```json
{
  "artist_name": "Artist Name"
}
```

**Response:**
```json
{
  "status": "success",
  "artist_name": "Artist Name",
  "channel_data": {
    "channel_id": "UC123456789",
    "title": "Artist Name Official",
    "statistics": {
      "subscriber_count": 15000,
      "view_count": 500000,
      "video_count": 25
    }
  },
  "analytics": {
    "recent_activity": {
      "upload_frequency": "active"
    },
    "growth_potential": "high_potential"
  },
  "recent_videos": [...],
  "integration_status": "YouTube API working correctly"
}
```

### Get YouTube Opportunities
Get artists with YouTube opportunities for targeted outreach.

```http
GET /api/youtube/opportunities?limit=20
```

**Response:**
```json
{
  "youtube_opportunities": {
    "no_youtube_presence": [
      {
        "id": 1,
        "name": "Artist Name",
        "monthly_listeners": 50000,
        "lead_tier": "A"
      }
    ],
    "underperforming_youtube": [
      {
        "id": 2,
        "name": "Another Artist",
        "monthly_listeners": 100000,
        "youtube_subscribers": 5000,
        "lead_tier": "B"
      }
    ]
  },
  "generated_at": "2025-07-13T10:30:00Z"
}
```

### Refresh Artist YouTube Data
Refresh YouTube data for a specific artist.

```http
POST /api/artist/{artist_id}/youtube/refresh
```

**Response:**
```json
{
  "status": "success",
  "message": "YouTube data refreshed successfully",
  "updated_data": {
    "channel_id": "UC123456789",
    "subscribers": 15500,
    "total_views": 520000,
    "video_count": 26,
    "upload_frequency": "active",
    "growth_potential": "high_potential"
  }
}
```

### YouTube Statistics
Get overall YouTube integration statistics.

```http
GET /api/youtube/stats
```

**Response:**
```json
{
  "total_artists": 150,
  "artists_with_youtube_channels": 85,
  "youtube_coverage_percentage": 56.7,
  "total_youtube_subscribers": 2500000,
  "average_youtube_subscribers": 29411,
  "high_potential_channels": 12,
  "api_status": "available",
  "generated_at": "2025-07-13T10:30:00Z"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `413` - Payload Too Large
- `429` - Rate Limit Exceeded (especially for YouTube API)
- `500` - Internal Server Error

Error response format:
```json
{
  "error": "Description of the error",
  "error_code": "YOUTUBE_QUOTA_EXCEEDED",
  "details": {
    "api": "youtube",
    "quota_remaining": 0,
    "reset_time": "2025-07-14T00:00:00Z"
  }
}
```

## YouTube-Specific Error Codes

- `YOUTUBE_API_KEY_MISSING` - YouTube API key not configured
- `YOUTUBE_QUOTA_EXCEEDED` - Daily quota limit reached
- `YOUTUBE_RATE_LIMIT` - Per-minute rate limit exceeded
- `YOUTUBE_CHANNEL_NOT_FOUND` - No YouTube channel found for artist
- `YOUTUBE_API_ERROR` - General YouTube API error

## Rate Limiting Headers

Responses include rate limiting information in headers:

```
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 95
X-RateLimit-Reset-Minute: 1625731200
X-RateLimit-Limit-Day: 10000
X-RateLimit-Remaining-Day: 9850
```

## Changelog

### Version 1.1.0 (July 2025)
- Added YouTube Data API integration
- New YouTube-specific endpoints
- Enhanced lead scoring with YouTube opportunities
- YouTube filtering options for leads
- YouTube metrics in exports and artist details
- Contact discovery includes YouTube channels

### Version 1.0.0 (January 2025)
- Initial release with MusicBrainz, Spotify, and Last.fm integration