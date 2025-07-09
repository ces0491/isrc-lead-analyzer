"""
Main processing pipeline for lead generation
Orchestrates API calls, data aggregation, and scoring
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import traceback

from src.core.rate_limiter import RateLimitManager
from src.core.scoring import LeadScoringEngine
from src.integrations.musicbrainz import musicbrainz_client
from src.integrations.spotify import spotify_client
from src.integrations.lastfm import lastfm_client
from src.models.database import DatabaseManager
from config.settings import settings

class LeadAggregationPipeline:
    """
    Main pipeline for processing ISRCs and generating lead data
    Coordinates all data sources and processing steps
    """
    
    def __init__(self, rate_manager: RateLimitManager):
        self.rate_manager = rate_manager
        self.scoring_engine = LeadScoringEngine()
        self.db_manager = DatabaseManager()
        
        # Processing statistics
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None
        }
    
    def process_isrc(self, isrc: str, save_to_db: bool = True) -> Dict:
        """
        Main processing function for a single ISRC
        Returns comprehensive artist and track data with scoring
        """
        self.stats['processed'] += 1
        if not self.stats['start_time']:
            self.stats['start_time'] = datetime.now()
        
        result = {
            'isrc': isrc,
            'status': 'processing',
            'artist_data': {},
            'track_data': {},
            'musicbrainz_data': {},
            'spotify_data': {},
            'lastfm_data': {},
            'contacts': [],
            'scores': {},
            'errors': [],
            'processing_time': None,
            'data_sources_used': []
        }
        
        start_time = datetime.now()
        
        try:
            # Step 1: Get basic track and artist info from MusicBrainz
            print(f"Processing ISRC: {isrc}")
            print("  1. Fetching MusicBrainz data...")
            
            mb_data = musicbrainz_client.lookup_by_isrc(isrc)
            if not mb_data:
                result['status'] = 'failed'
                result['errors'].append('ISRC not found in MusicBrainz')
                self.stats['failed'] += 1
                return result
            
            result['musicbrainz_data'] = mb_data
            result['data_sources_used'].append('musicbrainz')
            
            # Extract basic info
            artist_name = mb_data.get('artist', {}).get('name')
            track_title = mb_data.get('track', {}).get('title')
            
            if not artist_name:
                result['status'] = 'failed'
                result['errors'].append('No artist name found')
                self.stats['failed'] += 1
                return result
            
            # Step 2: Enrich with Spotify data
            print("  2. Fetching Spotify data...")
            spotify_data = self._get_spotify_data(artist_name, track_title)
            if spotify_data:
                result['spotify_data'] = spotify_data
                result['data_sources_used'].append('spotify')
            
            # Step 3: Get social listening data from Last.fm
            print("  3. Fetching Last.fm data...")
            lastfm_data = self._get_lastfm_data(artist_name, track_title)
            if lastfm_data:
                result['lastfm_data'] = lastfm_data
                result['data_sources_used'].append('lastfm')
            
            # Step 4: Aggregate and normalize data
            print("  4. Aggregating data...")
            aggregated_data = self._aggregate_data(result)
            result['artist_data'] = aggregated_data['artist']
            result['track_data'] = aggregated_data['track']
            
            # Step 5: Calculate lead scores
            print("  5. Calculating scores...")
            scores = self.scoring_engine.calculate_scores({
                'track_data': result['track_data'],
                'spotify_data': result['spotify_data'],
                'lastfm_data': result['lastfm_data'],
                'musicbrainz_data': result['musicbrainz_data']
            })
            result['scores'] = scores
            
            # Step 6: Discover contact information
            print("  6. Discovering contacts...")
            contacts = self._discover_contacts(result)
            result['contacts'] = contacts
            
            # Step 7: Save to database if requested
            if save_to_db:
                print("  7. Saving to database...")
                try:
                    artist_id = self.db_manager.save_artist_data({
                        'name': artist_name,
                        'musicbrainz_id': mb_data.get('artist', {}).get('musicbrainz_artist_id'),
                        'spotify_id': spotify_data.get('spotify_id') if spotify_data else None,
                        'country': mb_data.get('artist', {}).get('country'),
                        'genre': self._extract_primary_genre(result),
                        'monthly_listeners': spotify_data.get('followers', 0) if spotify_data else 0,
                        'scores': scores,
                        'track_data': result['track_data'],
                        'contacts': contacts
                    })
                    result['artist_id'] = artist_id
                except Exception as e:
                    result['errors'].append(f"Database save failed: {str(e)}")
            
            result['status'] = 'completed'
            self.stats['successful'] += 1
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(f"Pipeline error: {str(e)}")
            self.stats['failed'] += 1
            print(f"Error processing {isrc}: {str(e)}")
            traceback.print_exc()
        
        finally:
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = round(processing_time, 2)
            print(f"  Completed in {processing_time:.2f}s")
        
        return result
    
    def process_bulk(self, isrcs: List[str], batch_size: int = 10) -> Dict:
        """
        Process multiple ISRCs in batches with rate limiting
        Returns summary of all processing results
        """
        total_isrcs = len(isrcs)
        if total_isrcs > settings.max_bulk_isrcs:
            return {
                'error': f'Too many ISRCs. Maximum allowed: {settings.max_bulk_isrcs}',
                'provided': total_isrcs
            }
        
        print(f"Starting bulk processing of {total_isrcs} ISRCs...")
        
        # Reset stats for this batch
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now()
        }
        
        results = []
        batch_num = 1
        
        # Process in batches to manage memory and rate limits
        for i in range(0, total_isrcs, batch_size):
            batch = isrcs[i:i + batch_size]
            print(f"\nProcessing batch {batch_num} ({len(batch)} ISRCs)...")
            
            batch_results = []
            for isrc in batch:
                result = self.process_isrc(isrc, save_to_db=True)
                batch_results.append(result)
                
                # Rate limiting between requests
                if self.stats['processed'] % 5 == 0:
                    print(f"  Progress: {self.stats['processed']}/{total_isrcs} processed")
                    # Brief pause to respect rate limits
                    import time
                    time.sleep(1)
            
            results.extend(batch_results)
            batch_num += 1
        
        # Calculate final statistics
        processing_time = (datetime.now() - self.stats['start_time']).total_seconds()
        
        summary = {
            'total_processed': self.stats['processed'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'skipped': self.stats['skipped'],
            'success_rate': (self.stats['successful'] / max(self.stats['processed'], 1)) * 100,
            'total_time': round(processing_time, 2),
            'average_time_per_isrc': round(processing_time / max(self.stats['processed'], 1), 2),
            'results': results
        }
        
        print(f"\nBulk processing completed!")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total time: {summary['total_time']}s")
        
        return summary
    
    def _get_spotify_data(self, artist_name: str, track_title: str = None) -> Optional[Dict]:
        """Get comprehensive Spotify data for artist and track"""
        try:
            # Search for artist
            artist_data = spotify_client.search_artist(artist_name)
            if not artist_data:
                return None
            
            # Get detailed artist info
            spotify_id = artist_data.get('spotify_id')
            if spotify_id:
                detailed_data = spotify_client.get_artist_details(spotify_id)
                if detailed_data:
                    artist_data.update(detailed_data)
            
            # Search for specific track if provided
            if track_title:
                track_data = spotify_client.search_track(artist_name, track_title)
                if track_data:
                    artist_data['track_info'] = track_data
            
            return artist_data
            
        except Exception as e:
            print(f"Spotify API error: {str(e)}")
            return None
    
    def _get_lastfm_data(self, artist_name: str, track_title: str = None) -> Optional[Dict]:
        """Get Last.fm social listening data"""
        try:
            result = {}
            
            # Get artist info
            artist_info = lastfm_client.get_artist_info(artist_name)
            if artist_info:
                result['artist'] = artist_info
            
            # Get track info if provided
            if track_title:
                track_info = lastfm_client.get_track_info(artist_name, track_title)
                if track_info:
                    result['track'] = track_info
            
            return result if result else None
            
        except Exception as e:
            print(f"Last.fm API error: {str(e)}")
            return None
    
    def _aggregate_data(self, result: Dict) -> Dict:
        """
        Aggregate and normalize data from all sources
        Creates unified artist and track objects
        """
        mb_data = result.get('musicbrainz_data', {})
        spotify_data = result.get('spotify_data', {})
        lastfm_data = result.get('lastfm_data', {})
        
        # Aggregate artist data
        artist_data = {
            'name': self._get_best_value([
                spotify_data.get('name'),
                mb_data.get('artist', {}).get('name'),
                lastfm_data.get('artist', {}).get('name')
            ]),
            'musicbrainz_id': mb_data.get('artist', {}).get('musicbrainz_artist_id'),
            'spotify_id': spotify_data.get('spotify_id'),
            'country': mb_data.get('artist', {}).get('country'),
            'region': self._determine_region(mb_data.get('artist', {}).get('country')),
            'genres': self._merge_genres([
                spotify_data.get('genres', []),
                mb_data.get('artist', {}).get('genres', []),
                lastfm_data.get('artist', {}).get('tags', [])
            ]),
            'monthly_listeners': spotify_data.get('followers', 0),
            'popularity': spotify_data.get('popularity', 0),
            'lastfm_listeners': lastfm_data.get('artist', {}).get('listeners', 0),
            'lastfm_playcount': lastfm_data.get('artist', {}).get('playcount', 0),
            'release_count': spotify_data.get('release_count', 0),
            'last_release_date': self._parse_date(spotify_data.get('last_release_date')),
            'social_urls': mb_data.get('artist', {}).get('urls', {}),
            'website': mb_data.get('artist', {}).get('urls', {}).get('website')
        }
        
        # Aggregate track data
        track_data = {
            'isrc': result.get('isrc'),
            'title': self._get_best_value([
                mb_data.get('track', {}).get('title'),
                spotify_data.get('track_info', {}).get('name')
            ]),
            'musicbrainz_recording_id': mb_data.get('track', {}).get('musicbrainz_recording_id'),
            'spotify_track_id': spotify_data.get('track_info', {}).get('spotify_track_id'),
            'release_date': self._parse_date(self._get_best_value([
                mb_data.get('release', {}).get('release_date'),
                spotify_data.get('track_info', {}).get('album', {}).get('release_date')
            ])),
            'label': self._get_best_value([
                mb_data.get('release', {}).get('label'),
                spotify_data.get('track_info', {}).get('album', {}).get('label')
            ]),
            'duration_ms': self._get_best_value([
                spotify_data.get('track_info', {}).get('duration_ms'),
                mb_data.get('track', {}).get('length_ms')
            ]),
            'spotify_popularity': spotify_data.get('track_info', {}).get('popularity', 0),
            'lastfm_playcount': lastfm_data.get('track', {}).get('playcount', 0),
            'platforms_available': self._detect_platforms(result),
            'missing_platforms': []  # Will be calculated in scoring
        }
        
        return {
            'artist': artist_data,
            'track': track_data
        }
    
    def _discover_contacts(self, result: Dict) -> List[Dict]:
        """
        Discover contact information from various sources
        Returns list of potential contact methods with confidence scores
        """
        contacts = []
        
        # Extract from MusicBrainz URLs
        mb_urls = result.get('musicbrainz_data', {}).get('artist', {}).get('urls', {})
        for platform, url in mb_urls.items():
            if platform == 'website':
                contacts.append({
                    'type': 'website',
                    'value': url,
                    'source': 'musicbrainz',
                    'confidence': 90
                })
            elif platform in ['twitter', 'instagram', 'facebook']:
                contacts.append({
                    'type': 'social',
                    'platform': platform,
                    'value': url,
                    'source': 'musicbrainz',
                    'confidence': 85
                })
        
        # Extract potential emails from social media handles
        # This is a placeholder - in practice, you'd need to scrape or use additional APIs
        
        # Add Spotify profile as contact method
        spotify_id = result.get('spotify_data', {}).get('spotify_id')
        if spotify_id:
            contacts.append({
                'type': 'platform_profile',
                'platform': 'spotify',
                'value': f"https://open.spotify.com/artist/{spotify_id}",
                'source': 'spotify_api',
                'confidence': 95
            })
        
        return contacts
    
    def _get_best_value(self, values: List) -> str:
        """Get the best non-empty value from a list of options"""
        for value in values:
            if value and str(value).strip():
                return str(value).strip()
        return None
    
    def _merge_genres(self, genre_lists: List[List]) -> List[str]:
        """Merge and deduplicate genres from multiple sources"""
        all_genres = []
        for genre_list in genre_lists:
            if isinstance(genre_list, list):
                all_genres.extend([g.lower() for g in genre_list])
        
        # Remove duplicates while preserving order
        unique_genres = []
        seen = set()
        for genre in all_genres:
            if genre not in seen:
                unique_genres.append(genre)
                seen.add(genre)
        
        return unique_genres[:5]  # Return top 5 genres
    
    def _determine_region(self, country: str) -> str:
        """Determine geographic region from country code"""
        if not country:
            return 'unknown'
        
        country = country.upper()
        for region, countries in settings.target_regions.items():
            if country in countries:
                return region
        
        return 'other'
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse and normalize date strings"""
        if not date_str:
            return None
        
        # Just return the string for now - could add more sophisticated parsing
        return str(date_str).strip()
    
    def _extract_primary_genre(self, result: Dict) -> str:
        """Extract the primary genre from aggregated data"""
        # Try Spotify first (usually most accurate)
        spotify_genres = result.get('spotify_data', {}).get('genres', [])
        if spotify_genres:
            return spotify_genres[0]
        
        # Try Last.fm tags
        lastfm_tags = result.get('lastfm_data', {}).get('artist', {}).get('tags', [])
        if lastfm_tags:
            return lastfm_tags[0]
        
        # Try MusicBrainz tags
        mb_tags = result.get('musicbrainz_data', {}).get('artist', {}).get('tags', [])
        if mb_tags:
            return mb_tags[0]
        
        return 'unknown'
    
    def _detect_platforms(self, result: Dict) -> List[str]:
        """Detect which platforms the track is available on"""
        platforms = []
        
        # If we found it on Spotify, it's available there
        if result.get('spotify_data'):
            platforms.append('spotify')
        
        # If we found it on Last.fm, it's likely on major platforms
        if result.get('lastfm_data'):
            platforms.extend(['last_fm', 'youtube_music'])
        
        # MusicBrainz indicates it's been officially released
        if result.get('musicbrainz_data'):
            platforms.extend(['apple_music', 'amazon_music'])
        
        return list(set(platforms))  # Remove duplicates
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        if self.stats['start_time']:
            elapsed_time = (datetime.now() - self.stats['start_time']).total_seconds()
        else:
            elapsed_time = 0
        
        return {
            **self.stats,
            'elapsed_time': round(elapsed_time, 2),
            'rate_per_minute': round((self.stats['processed'] / max(elapsed_time / 60, 1)), 2) if elapsed_time > 0 else 0
        }

# Utility functions for testing
def test_pipeline():
    """Test the pipeline with sample ISRCs"""
    from src.core.rate_limiter import rate_limiter
    
    # Sample test ISRCs - replace with real ones for testing
    test_isrcs = [
        "USRC17607839",  # Example ISRC
        "GBUM71505078",  # Another example
    ]
    
    pipeline = LeadAggregationPipeline(rate_limiter)
    
    for isrc in test_isrcs:
        print(f"\n{'='*50}")
        print(f"Testing ISRC: {isrc}")
        print('='*50)
        
        result = pipeline.process_isrc(isrc, save_to_db=False)
        
        print(f"Status: {result['status']}")
        if result['status'] == 'completed':
            scores = result['scores']
            print(f"Lead Score: {scores['total_score']} (Tier {scores['tier']})")
            print(f"Independence: {scores['independence_score']}")
            print(f"Opportunity: {scores['opportunity_score']}")
            print(f"Geographic: {scores['geographic_score']}")
            print(f"Data Sources: {', '.join(result['data_sources_used'])}")
        else:
            print(f"Errors: {result['errors']}")

if __name__ == "__main__":
    test_pipeline()