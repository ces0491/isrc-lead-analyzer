# docs/API.md

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

## Endpoints

### Health Check
Check if the API is running.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### System Status
Get system status and rate limit information.

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
    }
  },
  "processing_stats": {
    "processed": 0,
    "successful": 0,
    "failed": 0
  }
}
```

### Analyze Single ISRC
Analyze a single ISRC and return lead scoring information.

```http
POST /api/analyze-isrc
```

**Request Body:**
```json
{
  "isrc": "USRC17607839",
  "save_to_db": true,
  "force_refresh": false
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
    "total_score": 75.5,
    "independence_score": 40,
    "opportunity_score": 25,
    "geographic_score": 30,
    "tier": "A",
    "confidence": 85
  },
  "contacts": [
    {
      "type": "email",
      "value": "contact@artist.com",
      "confidence": 80,
      "source": "website"
    }
  ],
  "processing_time": 3.2
}
```

### Bulk Analysis
Analyze multiple ISRCs in batch.

```http
POST /api/analyze-bulk
```

**Request Body:**
```json
{
  "isrcs": ["USRC17607839", "GBUM71505078"],
  "batch_size": 10
}
```

**Response:**
```json
{
  "total_processed": 2,
  "successful": 2,
  "failed": 0,
  "success_rate": 100.0,
  "total_time": 6.4,
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
Retrieve filtered list of leads.

```http
GET /api/leads?tier=A&region=new_zealand&limit=20&offset=0
```

**Query Parameters:**
- `tier` (optional): Filter by lead tier (A, B, C, D)
- `region` (optional): Filter by region
- `min_score` (optional): Minimum score threshold
- `max_score` (optional): Maximum score threshold
- `limit` (optional): Number of results (default: 50, max: 1000)
- `offset` (optional): Pagination offset (default: 0)
- `sort_by` (optional): Sort field (total_score, name, created_at)
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
      "contact_email": "artist@example.com"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

### Export Leads
Export filtered leads to CSV format.

```http
POST /api/export
```

**Request Body:**
```json
{
  "filters": {
    "tier": "A",
    "region": "new_zealand",
    "min_score": 70
  }
}
```

**Response:**
```json
{
  "csv_data": "Artist Name,Country,Score...",
  "filename": "precise_digital_leads_20240115.csv",
  "count": 25,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Get Artist Details
Get detailed information for a specific artist.

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
  "tracks": [
    {
      "isrc": "USRC17607839",
      "title": "Track Title"
    }
  ],
  "contact_attempts": [
    {
      "method": "email",
      "value": "artist@example.com",
      "confidence": 80
    }
  ]
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
  "notes": "Sent initial inquiry email"
}
```

**Valid Statuses:**
- `not_contacted`
- `contacted`
- `responded`
- `interested`
- `not_interested`
- `converted`

### Dashboard Statistics
Get dashboard statistics and metrics.

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
  }
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `413` - Payload Too Large
- `500` - Internal Server Error

Error response format:
```json
{
  "error": "Description of the error"
}
```
