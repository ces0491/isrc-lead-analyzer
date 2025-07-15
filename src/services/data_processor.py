"""
Data Processing Service for Precise Digital Lead Generation Tool
Handles data transformation, normalization, and aggregation for the Prism Analytics Engine
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict, Counter
import pandas as pd
from urllib.parse import urlparse

class DataProcessor:
    """
    Core data processing service for the Prism Analytics Engine
    Handles data transformation, normalization, and aggregation
    """
    
    def __init__(self):
        # Common patterns for data cleaning
        self.country_mappings = {
            'NEW ZEALAND': 'NZ',
            'AUSTRALIA': 'AU', 
            'UNITED STATES': 'US',
            'UNITED KINGDOM': 'GB',
            'CANADA': 'CA',
            'DEUTSCHLAND': 'DE',
            'FRANCE': 'FR',
            'ESPAÑA': 'ES',
            'ITALIA': 'IT',
            'JAPAN': 'JP',
            'BRASIL': 'BR',
            'MEXICO': 'MX'
        }
        
        # Genre mappings for normalization
        self.genre_mappings = {
            'alternative rock': 'alternative',
            'alt rock': 'alternative',
            'indie rock': 'indie',
            'indie pop': 'indie',
            'electronic dance music': 'electronic',
            'edm': 'electronic',
            'hip hop': 'hip-hop',
            'rhythm and blues': 'r&b',
            'rnb': 'r&b',
            'country music': 'country',
            'folk music': 'folk',
            'classical music': 'classical'
        }
        
        # Social platform patterns
        self.social_patterns = {
            'instagram': r'(?:instagram\.com/|@)([a-zA-Z0-9_.]+)',
            'twitter': r'(?:twitter\.com/|@)([a-zA-Z0-9_]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
            'youtube': r'youtube\.com/(?:c/|channel/|user/|@)([a-zA-Z0-9_.-]+)',
            'tiktok': r'tiktok\.com/@([a-zA-Z0-9_.]+)',
            'soundcloud': r'soundcloud\.com/([a-zA-Z0-9_-]+)',
            'bandcamp': r'([a-zA-Z0-9_-]+)\.bandcamp\.com'
        }
        
        # YouTube upload frequency scoring
        self.youtube_frequency_scores = {
            'very_active': 10,   # 4+ uploads per month
            'active': 8,         # 2-3 uploads per month
            'moderate': 5,       # 1 upload per month
            'low': 2,           # Quarterly uploads
            'inactive': 0        # No recent uploads
        }
    
    def normalize_artist_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize artist data from multiple sources into consistent format
        Handles data from MusicBrainz, Spotify, Last.fm, and YouTube
        """
        normalized = {
            'basic_info': {},
            'metrics': {},
            'geographic': {},
            'genres': [],
            'platforms': {},
            'youtube_data': {},
            'social_media': {},
            'contact_info': {},
            'metadata': {}
        }
        
        # Process basic information
        normalized['basic_info'] = self._normalize_basic_info(raw_data)
        
        # Process metrics (followers, listeners, etc.)
        normalized['metrics'] = self._normalize_metrics(raw_data)
        
        # Process geographic information
        normalized['geographic'] = self._normalize_geographic_data(raw_data)
        
        # Process genres
        normalized['genres'] = self._normalize_genres(raw_data)
        
        # Process platform presence
        normalized['platforms'] = self._extract_platform_presence(raw_data)
        
        # Process YouTube data specifically
        normalized['youtube_data'] = self._normalize_youtube_data(raw_data)
        
        # Process social media
        normalized['social_media'] = self._extract_social_media(raw_data)
        
        # Process contact information
        normalized['contact_info'] = self._extract_contact_info(raw_data)
        
        # Add metadata
        normalized['metadata'] = {
            'processed_at': datetime.utcnow().isoformat(),
            'data_sources': list(raw_data.keys()),
            'completeness_score': self._calculate_completeness_score(normalized)
        }
        
        return normalized
    
    def _normalize_basic_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize basic artist information"""
        basic_info = {}
        
        # Artist name (prioritize Spotify, then MusicBrainz, then Last.fm)
        name_sources = [
            raw_data.get('spotify_data', {}).get('name'),
            raw_data.get('musicbrainz_data', {}).get('artist', {}).get('name'),
            raw_data.get('lastfm_data', {}).get('artist', {}).get('name')
        ]
        basic_info['name'] = self._get_best_value(name_sources)
        
        # Artist IDs
        basic_info['musicbrainz_id'] = raw_data.get('musicbrainz_data', {}).get('artist', {}).get('musicbrainz_artist_id')
        basic_info['spotify_id'] = raw_data.get('spotify_data', {}).get('spotify_id')
        
        # Disambiguation and type
        basic_info['disambiguation'] = raw_data.get('musicbrainz_data', {}).get('artist', {}).get('disambiguation')
        basic_info['artist_type'] = raw_data.get('musicbrainz_data', {}).get('artist', {}).get('type')
        
        return basic_info
    
    def _normalize_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize engagement metrics"""
        metrics = {}
        
        # Spotify metrics
        spotify_data = raw_data.get('spotify_data', {})
        metrics['spotify_followers'] = self._safe_int(spotify_data.get('followers', 0))
        metrics['spotify_popularity'] = self._safe_int(spotify_data.get('popularity', 0))
        
        # Last.fm metrics
        lastfm_data = raw_data.get('lastfm_data', {}).get('artist', {})
        metrics['lastfm_listeners'] = self._safe_int(lastfm_data.get('listeners', 0))
        metrics['lastfm_playcount'] = self._safe_int(lastfm_data.get('playcount', 0))
        
        # YouTube metrics
        youtube_data = raw_data.get('youtube_data', {}).get('channel', {})
        if youtube_data:
            stats = youtube_data.get('statistics', {})
            metrics['youtube_subscribers'] = self._safe_int(stats.get('subscriber_count', 0))
            metrics['youtube_views'] = self._safe_int(stats.get('view_count', 0))
            metrics['youtube_videos'] = self._safe_int(stats.get('video_count', 0))
        
        # Calculate derived metrics
        metrics['total_social_reach'] = (
            metrics.get('spotify_followers', 0) +
            metrics.get('lastfm_listeners', 0) +
            metrics.get('youtube_subscribers', 0)
        )
        
        # Engagement ratios
        if metrics.get('spotify_followers', 0) > 0 and metrics.get('youtube_subscribers', 0) > 0:
            metrics['youtube_spotify_ratio'] = metrics['youtube_subscribers'] / metrics['spotify_followers']
        
        return metrics
    
    def _normalize_geographic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize geographic information"""
        geographic = {}
        
        # Get country from various sources
        country_sources = [
            raw_data.get('musicbrainz_data', {}).get('artist', {}).get('country'),
            raw_data.get('musicbrainz_data', {}).get('release', {}).get('country')
        ]
        
        raw_country = self._get_best_value(country_sources)
        if raw_country:
            geographic['country_raw'] = raw_country
            geographic['country_code'] = self._normalize_country_code(raw_country)
            geographic['region'] = self._determine_region(geographic['country_code'])
        
        return geographic
    
    def _normalize_genres(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract and normalize genre information"""
        all_genres = []
        
        # Spotify genres
        spotify_genres = raw_data.get('spotify_data', {}).get('genres', [])
        if isinstance(spotify_genres, list):
            all_genres.extend(spotify_genres)
        
        # Last.fm tags
        lastfm_tags = raw_data.get('lastfm_data', {}).get('artist', {}).get('tags', [])
        if isinstance(lastfm_tags, list):
            all_genres.extend(lastfm_tags)
        
        # MusicBrainz tags/genres
        mb_tags = raw_data.get('musicbrainz_data', {}).get('artist', {}).get('tags', [])
        if isinstance(mb_tags, list):
            all_genres.extend(mb_tags)
        
        # Normalize and deduplicate
        normalized_genres = []
        seen = set()
        
        for genre in all_genres:
            if isinstance(genre, str):
                normalized_genre = self._normalize_genre(genre)
                if normalized_genre and normalized_genre not in seen:
                    normalized_genres.append(normalized_genre)
                    seen.add(normalized_genre)
        
        return normalized_genres[:5]  # Return top 5 genres
    
    def _normalize_youtube_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize YouTube-specific data"""
        youtube_data = {}
        
        raw_youtube = raw_data.get('youtube_data', {})
        if not raw_youtube:
            return youtube_data
        
        # Channel information
        channel = raw_youtube.get('channel', {})
        if channel:
            youtube_data['channel_id'] = channel.get('channel_id')
            youtube_data['channel_title'] = channel.get('title')
            youtube_data['channel_description'] = channel.get('description', '')[:500]  # Limit length
            youtube_data['channel_published_at'] = channel.get('published_at')
            
            # Statistics
            stats = channel.get('statistics', {})
            youtube_data['subscriber_count'] = self._safe_int(stats.get('subscriber_count', 0))
            youtube_data['view_count'] = self._safe_int(stats.get('view_count', 0))
            youtube_data['video_count'] = self._safe_int(stats.get('video_count', 0))
        
        # Analytics data
        analytics = raw_youtube.get('analytics', {})
        if analytics:
            recent_activity = analytics.get('recent_activity', {})
            youtube_data['upload_frequency'] = recent_activity.get('upload_frequency', 'unknown')
            youtube_data['videos_last_30_days'] = recent_activity.get('videos_last_30_days', 0)
            youtube_data['average_views'] = recent_activity.get('average_views', 0)
            
            # Engagement indicators
            engagement = analytics.get('engagement_indicators', {})
            youtube_data['subscriber_to_view_ratio'] = engagement.get('subscriber_to_view_ratio', 0)
            youtube_data['engagement_rate'] = engagement.get('subscriber_to_view_ratio', 0)
            
            # Growth potential
            youtube_data['growth_potential'] = analytics.get('growth_potential', 'unknown')
        
        # Video metrics
        videos = raw_youtube.get('videos', [])
        if videos:
            youtube_data['recent_video_count'] = len(videos)
            youtube_data['video_performance'] = self._analyze_video_performance(videos)
        
        # Calculate YouTube opportunity score
        youtube_data['opportunity_score'] = self._calculate_youtube_opportunity_score(youtube_data)
        
        return youtube_data
    
    def _extract_platform_presence(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract platform presence information"""
        platforms = {
            'confirmed': [],
            'likely': [],
            'missing': []
        }
        
        # Confirmed platforms (we have direct data)
        if raw_data.get('spotify_data'):
            platforms['confirmed'].append('spotify')
        
        if raw_data.get('lastfm_data'):
            platforms['confirmed'].append('last.fm')
        
        if raw_data.get('youtube_data', {}).get('channel'):
            platforms['confirmed'].append('youtube')
        
        # Check track data for platform availability
        track_data = raw_data.get('track_data', {})
        if track_data and track_data.get('platforms_available'):
            platforms['confirmed'].extend(track_data['platforms_available'])
        
        # Remove duplicates
        platforms['confirmed'] = list(set(platforms['confirmed']))
        
        # Major platforms that might be missing
        major_platforms = [
            'spotify', 'apple_music', 'youtube_music', 'amazon_music',
            'deezer', 'tidal', 'bandcamp', 'soundcloud'
        ]
        
        platforms['missing'] = [p for p in major_platforms if p not in platforms['confirmed']]
        
        return platforms
    
    def _extract_social_media(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract social media handles and URLs"""
        social_media = {}
        
        # From MusicBrainz URLs
        mb_urls = raw_data.get('musicbrainz_data', {}).get('artist', {}).get('urls', {})
        for platform, url in mb_urls.items():
            if platform in ['twitter', 'instagram', 'facebook', 'youtube']:
                social_media[platform] = {
                    'url': url,
                    'handle': self._extract_handle_from_url(url, platform),
                    'source': 'musicbrainz'
                }
        
        # From Spotify external URLs
        spotify_urls = raw_data.get('spotify_data', {}).get('external_urls', {})
        if spotify_urls:
            for platform, url in spotify_urls.items():
                if platform not in social_media:
                    social_media[platform] = {
                        'url': url,
                        'handle': self._extract_handle_from_url(url, platform),
                        'source': 'spotify'
                    }
        
        # From YouTube channel
        youtube_data = raw_data.get('youtube_data', {}).get('channel', {})
        if youtube_data:
            channel_id = youtube_data.get('channel_id')
            if channel_id:
                social_media['youtube'] = {
                    'url': f"https://youtube.com/channel/{channel_id}",
                    'handle': youtube_data.get('title', ''),
                    'source': 'youtube_api',
                    'subscriber_count': youtube_data.get('statistics', {}).get('subscriber_count', 0)
                }
        
        return social_media
    
    def _extract_contact_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contact information"""
        contact_info = {}
        
        # Website from MusicBrainz
        mb_urls = raw_data.get('musicbrainz_data', {}).get('artist', {}).get('urls', {})
        if 'website' in mb_urls:
            contact_info['website'] = mb_urls['website']
        
        # Extract from various sources (this would integrate with ContactDiscoveryService)
        # For now, just basic extraction
        
        return contact_info
    
    def _analyze_video_performance(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze performance of YouTube videos"""
        if not videos:
            return {}
        
        view_counts = []
        like_counts = []
        comment_counts = []
        
        for video in videos:
            stats = video.get('statistics', {})
            view_counts.append(self._safe_int(stats.get('view_count', 0)))
            like_counts.append(self._safe_int(stats.get('like_count', 0)))
            comment_counts.append(self._safe_int(stats.get('comment_count', 0)))
        
        return {
            'total_videos': len(videos),
            'total_views': sum(view_counts),
            'average_views': sum(view_counts) // len(view_counts) if view_counts else 0,
            'max_views': max(view_counts) if view_counts else 0,
            'total_likes': sum(like_counts),
            'total_comments': sum(comment_counts),
            'engagement_rate': self._calculate_video_engagement_rate(view_counts, like_counts, comment_counts)
        }
    
    def _calculate_video_engagement_rate(self, views: List[int], likes: List[int], comments: List[int]) -> float:
        """Calculate engagement rate for videos"""
        total_views = sum(views) if views else 0
        total_engagements = sum(likes) + sum(comments) if likes and comments else 0
        
        if total_views == 0:
            return 0.0
        
        return round((total_engagements / total_views) * 100, 2)
    
    def _calculate_youtube_opportunity_score(self, youtube_data: Dict[str, Any]) -> int:
        """Calculate YouTube opportunity score based on various factors"""
        if not youtube_data:
            return 100  # No YouTube presence = maximum opportunity
        
        score = 0
        
        # Channel size scoring
        subscriber_count = youtube_data.get('subscriber_count', 0)
        if subscriber_count == 0:
            score += 50  # No subscribers = high opportunity
        elif subscriber_count < 1000:
            score += 40  # Small channel
        elif subscriber_count < 10000:
            score += 20  # Growing channel
        else:
            score += 5   # Established channel
        
        # Upload frequency scoring
        upload_freq = youtube_data.get('upload_frequency', 'inactive')
        freq_scores = {
            'inactive': 30,
            'low': 20,
            'moderate': 10,
            'active': 5,
            'very_active': 0
        }
        score += freq_scores.get(upload_freq, 15)
        
        # Growth potential
        growth_potential = youtube_data.get('growth_potential', 'unknown')
        if growth_potential == 'high_potential':
            score += 20
        elif growth_potential == 'moderate_potential':
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _normalize_country_code(self, country: str) -> str:
        """Normalize country name to ISO code"""
        if not country:
            return ''
        
        country_upper = country.upper().strip()
        
        # Direct mapping
        if country_upper in self.country_mappings:
            return self.country_mappings[country_upper]
        
        # Already a 2-letter code
        if len(country_upper) == 2 and country_upper.isalpha():
            return country_upper
        
        return country_upper
    
    def _determine_region(self, country_code: str) -> str:
        """Determine target region from country code"""
        if not country_code:
            return 'unknown'
        
        region_mappings = {
            'new_zealand': ['NZ'],
            'australia': ['AU'],
            'pacific_islands': ['FJ', 'PG', 'SB', 'VU', 'NC', 'PF', 'WS', 'TO', 'TV', 'KI', 'NR', 'PW', 'MH', 'FM'],
            'north_america': ['US', 'CA', 'MX'],
            'europe': ['GB', 'DE', 'FR', 'ES', 'IT', 'NL', 'SE', 'NO', 'DK'],
            'asia': ['JP', 'KR', 'CN', 'IN', 'TH', 'SG']
        }
        
        for region, countries in region_mappings.items():
            if country_code in countries:
                return region
        
        return 'other'
    
    def _normalize_genre(self, genre: str) -> str:
        """Normalize genre string"""
        if not genre:
            return ''
        
        genre_lower = genre.lower().strip()
        
        # Direct mapping
        if genre_lower in self.genre_mappings:
            return self.genre_mappings[genre_lower]
        
        # Clean up common variations
        genre_clean = re.sub(r'[^\w\s-]', '', genre_lower)
        genre_clean = re.sub(r'\s+', ' ', genre_clean).strip()
        
        return genre_clean
    
    def _extract_handle_from_url(self, url: str, platform: str) -> str:
        """Extract handle/username from social media URL"""
        if not url:
            return ''
        
        if platform in self.social_patterns:
            pattern = self.social_patterns[platform]
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ''
    
    def _get_best_value(self, values: List[Any]) -> Any:
        """Get the best non-empty value from a list"""
        for value in values:
            if value is not None and str(value).strip():
                return value
        return None
    
    def _safe_int(self, value: Any) -> int:
        """Safely convert value to integer"""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def _calculate_completeness_score(self, normalized_data: Dict[str, Any]) -> int:
        """Calculate data completeness score (0-100)"""
        total_fields = 0
        complete_fields = 0
        
        # Basic info fields
        basic_info = normalized_data.get('basic_info', {})
        basic_fields = ['name', 'musicbrainz_id', 'spotify_id']
        for field in basic_fields:
            total_fields += 1
            if basic_info.get(field):
                complete_fields += 1
        
        # Metrics fields
        metrics = normalized_data.get('metrics', {})
        metric_fields = ['spotify_followers', 'youtube_subscribers']
        for field in metric_fields:
            total_fields += 1
            if metrics.get(field, 0) > 0:
                complete_fields += 1
        
        # Geographic fields
        geographic = normalized_data.get('geographic', {})
        geo_fields = ['country_code', 'region']
        for field in geo_fields:
            total_fields += 1
            if geographic.get(field):
                complete_fields += 1
        
        # Genre data
        total_fields += 1
        if normalized_data.get('genres'):
            complete_fields += 1
        
        # Platform presence
        total_fields += 1
        if normalized_data.get('platforms', {}).get('confirmed'):
            complete_fields += 1
        
        # YouTube data
        total_fields += 1
        if normalized_data.get('youtube_data'):
            complete_fields += 1
        
        # Social media
        total_fields += 1
        if normalized_data.get('social_media'):
            complete_fields += 1
        
        return round((complete_fields / total_fields) * 100) if total_fields > 0 else 0

class BatchProcessor:
    """
    Batch processing capabilities for handling multiple artists efficiently
    """
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def process_artist_batch(self, raw_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of artists and return aggregated results"""
        self.processing_stats['start_time'] = datetime.utcnow()
        self.processing_stats['total_processed'] = len(raw_data_list)
        
        processed_artists = []
        errors = []
        
        for i, raw_data in enumerate(raw_data_list):
            try:
                normalized = self.data_processor.normalize_artist_data(raw_data)
                processed_artists.append(normalized)
                self.processing_stats['successful'] += 1
            except Exception as e:
                self.processing_stats['failed'] += 1
                errors.append({
                    'index': i,
                    'error': str(e),
                    'artist_name': raw_data.get('name', 'Unknown')
                })
        
        self.processing_stats['end_time'] = datetime.utcnow()
        processing_time = (self.processing_stats['end_time'] - self.processing_stats['start_time']).total_seconds()
        
        # Generate batch analytics
        batch_analytics = self._generate_batch_analytics(processed_artists)
        
        return {
            'processed_artists': processed_artists,
            'batch_analytics': batch_analytics,
            'processing_stats': {
                **self.processing_stats,
                'processing_time_seconds': processing_time,
                'average_time_per_artist': processing_time / len(raw_data_list) if raw_data_list else 0
            },
            'errors': errors
        }
    
    def _generate_batch_analytics(self, processed_artists: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analytics for a batch of processed artists"""
        if not processed_artists:
            return {}
        
        analytics = {
            'total_artists': len(processed_artists),
            'geographic_distribution': defaultdict(int),
            'genre_distribution': Counter(),
            'platform_coverage': defaultdict(int),
            'youtube_statistics': {
                'artists_with_youtube': 0,
                'total_subscribers': 0,
                'upload_frequency_distribution': defaultdict(int)
            },
            'completeness_distribution': defaultdict(int),
            'opportunity_scores': []
        }
        
        for artist in processed_artists:
            # Geographic distribution
            region = artist.get('geographic', {}).get('region', 'unknown')
            analytics['geographic_distribution'][region] += 1
            
            # Genre distribution
            genres = artist.get('genres', [])
            for genre in genres[:3]:  # Top 3 genres per artist
                analytics['genre_distribution'][genre] += 1
            
            # Platform coverage
            confirmed_platforms = artist.get('platforms', {}).get('confirmed', [])
            for platform in confirmed_platforms:
                analytics['platform_coverage'][platform] += 1
            
            # YouTube statistics
            youtube_data = artist.get('youtube_data', {})
            if youtube_data:
                analytics['youtube_statistics']['artists_with_youtube'] += 1
                analytics['youtube_statistics']['total_subscribers'] += youtube_data.get('subscriber_count', 0)
                
                upload_freq = youtube_data.get('upload_frequency', 'unknown')
                analytics['youtube_statistics']['upload_frequency_distribution'][upload_freq] += 1
                
                # Opportunity scores
                opportunity_score = youtube_data.get('opportunity_score', 0)
                analytics['opportunity_scores'].append(opportunity_score)
            
            # Completeness distribution
            completeness = artist.get('metadata', {}).get('completeness_score', 0)
            if completeness >= 80:
                analytics['completeness_distribution']['high'] += 1
            elif completeness >= 60:
                analytics['completeness_distribution']['medium'] += 1
            else:
                analytics['completeness_distribution']['low'] += 1
        
        # Calculate averages and insights
        if analytics['opportunity_scores']:
            analytics['youtube_statistics']['average_opportunity_score'] = sum(analytics['opportunity_scores']) / len(analytics['opportunity_scores'])
        
        # Convert defaultdicts to regular dicts for JSON serialization
        analytics['geographic_distribution'] = dict(analytics['geographic_distribution'])
        analytics['platform_coverage'] = dict(analytics['platform_coverage'])
        analytics['youtube_statistics']['upload_frequency_distribution'] = dict(analytics['youtube_statistics']['upload_frequency_distribution'])
        analytics['completeness_distribution'] = dict(analytics['completeness_distribution'])
        analytics['genre_distribution'] = dict(analytics['genre_distribution'].most_common(10))  # Top 10 genres
        
        return analytics

# Utility functions for data processing
def process_isrc_batch(isrc_list: List[str]) -> Dict[str, Any]:
    """
    Process a batch of ISRCs and return normalized data
    This would integrate with the main pipeline
    """
    # This is a placeholder - in practice this would use the LeadAggregationPipeline
    from src.core.pipeline import LeadAggregationPipeline
    from src.core.rate_limiter import RateLimitManager
    
    rate_limiter = RateLimitManager()
    pipeline = LeadAggregationPipeline(rate_limiter)
    processor = BatchProcessor()
    
    raw_data_list = []
    
    for isrc in isrc_list:
        try:
            result = pipeline.process_isrc(isrc, save_to_db=False)
            if result['status'] == 'completed':
                raw_data_list.append(result)
        except Exception as e:
            print(f"Failed to process ISRC {isrc}: {e}")
    
    return processor.process_artist_batch(raw_data_list)

def export_processed_data(processed_data: Dict[str, Any], format: str = 'json') -> str:
    """
    Export processed data in various formats
    """
    if format == 'json':
        return json.dumps(processed_data, indent=2, default=str)
    elif format == 'csv':
        # Convert to pandas DataFrame and export as CSV
        artists = processed_data.get('processed_artists', [])
        if not artists:
            return ''
        
        # Flatten the data for CSV export
        flattened_data = []
        for artist in artists:
            flat_artist = {
                'name': artist.get('basic_info', {}).get('name', ''),
                'country': artist.get('geographic', {}).get('country_code', ''),
                'region': artist.get('geographic', {}).get('region', ''),
                'spotify_followers': artist.get('metrics', {}).get('spotify_followers', 0),
                'youtube_subscribers': artist.get('metrics', {}).get('youtube_subscribers', 0),
                'total_social_reach': artist.get('metrics', {}).get('total_social_reach', 0),
                'primary_genre': artist.get('genres', [''])[0] if artist.get('genres') else '',
                'platform_count': len(artist.get('platforms', {}).get('confirmed', [])),
                'youtube_opportunity_score': artist.get('youtube_data', {}).get('opportunity_score', 0),
                'completeness_score': artist.get('metadata', {}).get('completeness_score', 0)
            }
            flattened_data.append(flat_artist)
        
        df = pd.DataFrame(flattened_data)
        return df.to_csv(index=False)
    
    return str(processed_data)

# Test function
def test_data_processor():
    """Test the data processor with sample data"""
    processor = DataProcessor()
    
    sample_data = {
        'spotify_data': {
            'name': 'Test Artist',
            'spotify_id': 'test123',
            'followers': 25000,
            'popularity': 65,
            'genres': ['indie rock', 'alternative']
        },
        'musicbrainz_data': {
            'artist': {
                'name': 'Test Artist',
                'musicbrainz_artist_id': 'test-mb-id',
                'country': 'NZ',
                'tags': ['rock', 'indie']
            }
        },
        'youtube_data': {
            'channel': {
                'channel_id': 'test-yt-id',
                'title': 'Test Artist Official',
                'statistics': {
                    'subscriber_count': 5000,
                    'view_count': 500000,
                    'video_count': 25
                }
            },
            'analytics': {
                'recent_activity': {
                    'upload_frequency': 'moderate',
                    'videos_last_30_days': 2
                },
                'growth_potential': 'high_potential'
            }
        }
    }
    
    normalized = processor.normalize_artist_data(sample_data)
    
    print("🧪 Data Processor Test Results:")
    print(f"Artist Name: {normalized['basic_info']['name']}")
    print(f"Country/Region: {normalized['geographic']['country_code']}/{normalized['geographic']['region']}")
    print(f"Genres: {', '.join(normalized['genres'])}")
    print(f"Total Social Reach: {normalized['metrics']['total_social_reach']:,}")
    print(f"YouTube Opportunity Score: {normalized['youtube_data']['opportunity_score']}")
    print(f"Completeness Score: {normalized['metadata']['completeness_score']}%")

if __name__ == "__main__":
    test_data_processor()