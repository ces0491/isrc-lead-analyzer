"""
YouTube Data API client for music video data and channel analytics.
Precise Digital - Music Services Lead Generation Tool

YouTube provides valuable data for artists including:
- Channel subscriber counts and engagement
- Music video view counts and popularity
- Upload frequency and content strategy
- Audience engagement metrics
"""

import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote

from .base_client import BaseAPIClient
from config.settings import settings

logger = logging.getLogger(__name__)


class YouTubeClient(BaseAPIClient):
    """
    Client for interacting with the YouTube Data API v3.
    
    Provides access to:
    - Artist channel information and statistics
    - Music video search and analytics
    - Upload frequency and engagement metrics
    - Subscriber counts and growth indicators
    """
    
    def __init__(self):
        """Initialize the YouTube client."""
        super().__init__('youtube')
        self.api_key = settings.apis['youtube'].api_key
        
        if not self.api_key:
            logger.warning("YouTube API key not configured")
    
    def search_artist_channel(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for an artist's YouTube channel.
        
        Args:
            artist_name: Name of the artist to search for
            
        Returns:
            Channel data with statistics or None if not found
        """
        if not self.api_key or not artist_name:
            return None
        
        # Search for channels by artist name
        search_params = {
            'part': 'snippet',
            'type': 'channel',
            'q': artist_name,
            'maxResults': 5,
            'key': self.api_key
        }
        
        response = self.rate_limiter.make_request('youtube', 'search', params=search_params)
        if not response or 'items' not in response:
            return None
        
        # Find the most relevant channel (usually first result)
        channels = response['items']
        if not channels:
            return None
        
        best_channel = channels[0]
        channel_id = best_channel['snippet']['channelId']
        
        # Get detailed channel statistics
        channel_details = self._get_channel_details(channel_id)
        
        if channel_details:
            # Combine search result with detailed stats
            result = {
                'channel_id': channel_id,
                'title': best_channel['snippet']['title'],
                'description': best_channel['snippet']['description'],
                'thumbnail': best_channel['snippet']['thumbnails'].get('high', {}).get('url'),
                'published_at': best_channel['snippet']['publishedAt'],
                'statistics': channel_details.get('statistics', {}),
                'content_details': channel_details.get('contentDetails', {}),
                'relevance_score': self._calculate_relevance_score(best_channel, artist_name)
            }
            return result
        
        return None
    
    def _get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a specific channel."""
        if not channel_id:
            return None
        
        params = {
            'part': 'statistics,contentDetails,snippet',
            'id': channel_id,
            'key': self.api_key
        }
        
        response = self.rate_limiter.make_request('youtube', 'channels', params=params)
        if not response or 'items' not in response or not response['items']:
            return None
        
        return response['items'][0]
    
    def search_artist_videos(self, artist_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for music videos by an artist.
        
        Args:
            artist_name: Name of the artist
            max_results: Maximum number of videos to return
            
        Returns:
            List of video data with view counts and metrics
        """
        if not self.api_key or not artist_name:
            return []
        
        # Search for videos by artist
        search_params = {
            'part': 'snippet',
            'type': 'video',
            'q': f"{artist_name} music",
            'videoCategoryId': '10',  # Music category
            'maxResults': max_results,
            'order': 'relevance',
            'key': self.api_key
        }
        
        response = self.rate_limiter.make_request('youtube', 'search', params=search_params)
        if not response or 'items' not in response:
            return []
        
        videos = []
        video_ids = []
        
        # Collect video IDs for batch statistics request
        for item in response['items']:
            video_ids.append(item['id']['videoId'])
        
        # Get detailed video statistics
        video_stats = self._get_video_statistics(video_ids)
        
        # Combine search results with statistics
        for i, item in enumerate(response['items']):
            video_id = item['id']['videoId']
            
            video_data = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url'),
                'statistics': video_stats.get(video_id, {}),
                'relevance_score': self._calculate_video_relevance_score(item, artist_name)
            }
            videos.append(video_data)
        
        # Sort by relevance score
        videos.sort(key=lambda x: x['relevance_score'], reverse=True)
        return videos
    
    def _get_video_statistics(self, video_ids: List[str]) -> Dict[str, Dict]:
        """Get statistics for multiple videos in batch."""
        if not video_ids:
            return {}
        
        params = {
            'part': 'statistics,contentDetails',
            'id': ','.join(video_ids),
            'key': self.api_key
        }
        
        response = self.rate_limiter.make_request('youtube', 'videos', params=params)
        if not response or 'items' not in response:
            return {}
        
        stats = {}
        for item in response['items']:
            video_id = item['id']
            stats[video_id] = {
                'view_count': self._safe_int(item.get('statistics', {}).get('viewCount', 0)),
                'like_count': self._safe_int(item.get('statistics', {}).get('likeCount', 0)),
                'comment_count': self._safe_int(item.get('statistics', {}).get('commentCount', 0)),
                'duration': item.get('contentDetails', {}).get('duration'),
                'definition': item.get('contentDetails', {}).get('definition')
            }
        
        return stats
    
    def get_channel_analytics(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive analytics for an artist's channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel analytics including growth indicators
        """
        channel_details = self._get_channel_details(channel_id)
        if not channel_details:
            return None
        
        stats = channel_details.get('statistics', {})
        
        # Get recent uploads for activity analysis
        recent_videos = self._get_recent_uploads(channel_id)
        
        analytics = {
            'channel_id': channel_id,
            'subscriber_count': self._safe_int(stats.get('subscriberCount', 0)),
            'view_count': self._safe_int(stats.get('viewCount', 0)),
            'video_count': self._safe_int(stats.get('videoCount', 0)),
            'recent_activity': {
                'videos_last_30_days': len([v for v in recent_videos if self._is_recent_upload(v, 30)]),
                'videos_last_90_days': len([v for v in recent_videos if self._is_recent_upload(v, 90)]),
                'upload_frequency': self._calculate_upload_frequency(recent_videos),
                'average_views': self._calculate_average_views(recent_videos)
            },
            'engagement_indicators': self._calculate_engagement_indicators(stats, recent_videos),
            'growth_potential': self._assess_growth_potential(stats, recent_videos)
        }
        
        return analytics
    
    def _get_recent_uploads(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Get recent uploads from a channel."""
        # First get the uploads playlist ID
        channel_details = self._get_channel_details(channel_id)
        if not channel_details:
            return []
        
        uploads_playlist_id = channel_details.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        if not uploads_playlist_id:
            return []
        
        # Get recent videos from uploads playlist
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': uploads_playlist_id,
            'maxResults': max_results,
            'order': 'date',
            'key': self.api_key
        }
        
        response = self.rate_limiter.make_request('youtube', 'playlistItems', params=params)
        if not response or 'items' not in response:
            return []
        
        return response['items']
    
    def _calculate_relevance_score(self, channel: Dict, artist_name: str) -> int:
        """Calculate how relevant a channel is to the artist search."""
        score = 0
        
        title = channel['snippet']['title'].lower()
        description = channel['snippet']['description'].lower()
        artist_lower = artist_name.lower()
        
        # Exact name match
        if artist_lower in title:
            score += 50
        
        # Partial name match
        artist_words = artist_lower.split()
        if len(artist_words) > 1:
            for word in artist_words:
                if word in title:
                    score += 20
        
        # Music-related keywords in description
        music_keywords = ['music', 'artist', 'band', 'singer', 'musician', 'official']
        for keyword in music_keywords:
            if keyword in description:
                score += 10
        
        return min(score, 100)
    
    def _calculate_video_relevance_score(self, video: Dict, artist_name: str) -> int:
        """Calculate how relevant a video is to the artist."""
        score = 0
        
        title = video['snippet']['title'].lower()
        channel_title = video['snippet']['channelTitle'].lower()
        artist_lower = artist_name.lower()
        
        # Artist name in video title
        if artist_lower in title:
            score += 40
        
        # Artist name in channel title
        if artist_lower in channel_title:
            score += 30
        
        # Music video indicators
        music_indicators = ['official', 'music video', 'mv', 'audio', 'lyrics']
        for indicator in music_indicators:
            if indicator in title:
                score += 15
        
        return min(score, 100)
    
    def _is_recent_upload(self, video: Dict, days: int) -> bool:
        """Check if video was uploaded within specified days."""
        from datetime import datetime, timedelta
        
        published_str = video.get('snippet', {}).get('publishedAt')
        if not published_str:
            return False
        
        try:
            published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            cutoff_date = datetime.now().replace(tzinfo=published_date.tzinfo) - timedelta(days=days)
            return published_date >= cutoff_date
        except:
            return False
    
    def _calculate_upload_frequency(self, videos: List[Dict]) -> str:
        """Calculate upload frequency based on recent videos."""
        if not videos:
            return 'inactive'
        
        recent_30 = len([v for v in videos if self._is_recent_upload(v, 30)])
        recent_90 = len([v for v in videos if self._is_recent_upload(v, 90)])
        
        if recent_30 >= 4:
            return 'very_active'  # 1+ per week
        elif recent_30 >= 2:
            return 'active'       # 2-3 per month
        elif recent_90 >= 3:
            return 'moderate'     # 1 per month
        elif recent_90 >= 1:
            return 'low'          # Quarterly
        else:
            return 'inactive'
    
    def _calculate_average_views(self, videos: List[Dict]) -> int:
        """Calculate average view count for recent videos."""
        if not videos:
            return 0
        
        # Get video IDs for recent uploads
        video_ids = [v['contentDetails']['videoId'] for v in videos[:10] if 'contentDetails' in v]
        if not video_ids:
            return 0
        
        # Get view statistics
        video_stats = self._get_video_statistics(video_ids)
        view_counts = [stats['view_count'] for stats in video_stats.values() if stats.get('view_count')]
        
        if not view_counts:
            return 0
        
        return sum(view_counts) // len(view_counts)
    
    def _calculate_engagement_indicators(self, channel_stats: Dict, recent_videos: List[Dict]) -> Dict:
        """Calculate engagement indicators for the channel."""
        subscriber_count = self._safe_int(channel_stats.get('subscriberCount', 0))
        total_views = self._safe_int(channel_stats.get('viewCount', 0))
        video_count = self._safe_int(channel_stats.get('videoCount', 0))
        
        indicators = {
            'subscriber_to_view_ratio': round(total_views / max(subscriber_count, 1), 2),
            'videos_per_subscriber': round(video_count / max(subscriber_count, 1) * 1000, 2),  # Per 1000 subs
            'average_views_per_video': round(total_views / max(video_count, 1)),
            'recent_upload_frequency': self._calculate_upload_frequency(recent_videos)
        }
        
        return indicators
    
    def _assess_growth_potential(self, channel_stats: Dict, recent_videos: List[Dict]) -> str:
        """Assess the growth potential of the channel."""
        subscriber_count = self._safe_int(channel_stats.get('subscriberCount', 0))
        video_count = self._safe_int(channel_stats.get('videoCount', 0))
        upload_frequency = self._calculate_upload_frequency(recent_videos)
        
        # Growth potential scoring
        if subscriber_count < 1000:
            size_score = 'emerging'
        elif subscriber_count < 10000:
            size_score = 'growing'
        elif subscriber_count < 100000:
            size_score = 'established'
        else:
            size_score = 'major'
        
        # Activity scoring
        activity_score = {
            'very_active': 3,
            'active': 2,
            'moderate': 1,
            'low': 0,
            'inactive': -1
        }.get(upload_frequency, 0)
        
        # Combined assessment
        if size_score == 'emerging' and activity_score >= 2:
            return 'high_potential'
        elif size_score == 'growing' and activity_score >= 1:
            return 'moderate_potential'
        elif size_score in ['established', 'major']:
            return 'established_presence'
        else:
            return 'low_potential'
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to integer."""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default


# Create global instance for easy access
youtube_client = YouTubeClient()