"""
Lead Scoring Engine for Precise Digital
Evaluates artists based on independence, opportunity, and geographic factors
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from config.settings import settings

class LeadScoringEngine:
    """
    Main scoring engine that evaluates potential leads
    Scoring is based on three main factors:
    1. Independence Score (40% weight) - How independent the artist is
    2. Opportunity Score (40% weight) - Gaps in services and growth potential  
    3. Geographic Score (20% weight) - Priority based on location
    """
    
    def __init__(self):
        self.weights = settings.scoring_weights
        self.target_regions = settings.target_regions
        self.major_platforms = settings.major_platforms
        
        # Major label keywords for independence detection
        self.major_labels = [
            'universal', 'sony', 'warner', 'emi', 'capitol', 'columbia',
            'atlantic', 'def jam', 'interscope', 'virgin', 'rca'
        ]
        
        # Distributor keywords for independence detection
        self.distributors = [
            'distrokid', 'cdbaby', 'tunecore', 'amuse', 'ditto', 'stemcells',
            'landr', 'symphonic', 'imusician', 'onerpm'
        ]
    
    def calculate_scores(self, artist_data: Dict) -> Dict:
        """
        Main scoring function that combines all factors
        Returns comprehensive scoring breakdown
        """
        # Extract data components with safe defaults
        track_data = artist_data.get('track_data', {})
        spotify_data = artist_data.get('spotify_data', {})
        lastfm_data = artist_data.get('lastfm_data', {})
        musicbrainz_data = artist_data.get('musicbrainz_data', {})
        
        # Calculate individual scores
        independence_score = self._calculate_independence_score(
            track_data, spotify_data, musicbrainz_data
        )
        
        opportunity_score = self._calculate_opportunity_score(
            track_data, spotify_data, lastfm_data, artist_data
        )
        
        geographic_score = self._calculate_geographic_score(
            musicbrainz_data, artist_data
        )
        
        # Calculate weighted total
        total_score = (
            independence_score * 0.4 +
            opportunity_score * 0.4 +
            geographic_score * 0.2
        )
        
        # Determine lead tier
        tier = self._get_lead_tier(total_score)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(artist_data)
        
        return {
            'independence_score': independence_score,
            'opportunity_score': opportunity_score,
            'geographic_score': geographic_score,
            'total_score': round(total_score, 1),
            'tier': tier,
            'confidence': confidence,
            'scoring_breakdown': self._get_scoring_breakdown(
                independence_score, opportunity_score, geographic_score, artist_data
            )
        }
    
    def _calculate_independence_score(self, track_data: Dict, spotify_data: Dict, mb_data: Dict) -> int:
        """
        Score based on artist independence level
        Higher scores for more independent artists
        """
        score = 0
        
        # Analyze label information from multiple sources
        labels = []
        
        # From track/release data
        if track_data.get('label'):
            labels.append(self._safe_str(track_data['label']).lower())
        
        # From MusicBrainz release data
        if mb_data.get('release', {}).get('label'):
            labels.append(self._safe_str(mb_data['release']['label']).lower())
        
        # From Spotify album data
        if spotify_data.get('album', {}).get('label'):
            labels.append(self._safe_str(spotify_data['album']['label']).lower())
        
        # Get artist name safely
        artist_name = self._safe_str(
            spotify_data.get('name') or 
            mb_data.get('artist', {}).get('name') or 
            track_data.get('artist_name', '')
        ).lower()
        
        if not labels:
            # No label info - assume self-released
            score = self.weights['independence']['self_released']
        else:
            # Analyze all labels found
            is_major = any(
                any(major in label for major in self.major_labels)
                for label in labels if label
            )
            
            is_distributor = any(
                any(dist in label for dist in self.distributors)
                for label in labels if label
            )
            
            is_self_released = any(
                (artist_name and artist_name in label) or 
                'self-released' in label or 
                'independent' in label
                for label in labels if label
            )
            
            if is_major:
                score = self.weights['independence']['major_distributed']
            elif is_self_released:
                score = self.weights['independence']['self_released']
            elif is_distributor:
                score = self.weights['independence']['small_distributor']
            else:
                score = self.weights['independence']['indie_label']
        
        return min(score, 100)
    
    def _calculate_opportunity_score(self, track_data: Dict, spotify_data: Dict, 
                                   lastfm_data: Dict, artist_data: Dict) -> int:
        """
        Score based on service gaps and growth potential
        Higher scores indicate more opportunities for Precise Digital services
        """
        score = 0
        
        # 1. Check for missing major platforms (20 points max)
        platforms_available = track_data.get('platforms_available', [])
        if not isinstance(platforms_available, list):
            platforms_available = []
            
        missing_platforms = [p for p in self.major_platforms if p not in platforms_available]
        
        if len(missing_platforms) >= 3:
            score += self.weights['opportunity']['missing_platforms']
        elif len(missing_platforms) >= 1:
            score += self.weights['opportunity']['missing_platforms'] * 0.5
        
        # 2. Analyze distribution sophistication (15 points max)
        # Basic distribution = only on major streaming platforms
        if platforms_available and len(platforms_available) <= 4:
            score += self.weights['opportunity']['basic_distribution_only']
        
        # 3. Check for publishing admin gaps (10 points max)
        # Indicators: No PRO registration, no publishing credits
        if not artist_data.get('publishing_info'):
            score += self.weights['opportunity']['no_publishing_admin']
        
        # 4. Growth potential indicators (15 points max)
        monthly_listeners = self._safe_int(spotify_data.get('followers', 0))
        popularity = self._safe_int(spotify_data.get('popularity', 0))
        
        # Sweet spot: 10K-500K listeners with decent popularity
        if 10000 <= monthly_listeners <= 500000 and popularity >= 30:
            score += self.weights['opportunity']['growing_streams']
        elif 1000 <= monthly_listeners <= 50000 and popularity >= 20:
            score += self.weights['opportunity']['growing_streams'] * 0.7
        
        # 5. Recent activity (10 points max)
        last_release = self._get_most_recent_release_date(track_data, spotify_data)
        if last_release and self._is_recent_release(last_release):
            score += self.weights['opportunity']['recent_activity']
        
        # 6. Professional presence gaps (10 points max)
        professional_indicators = [
            artist_data.get('website'),
            artist_data.get('social_handles', {}).get('instagram'),
            artist_data.get('social_handles', {}).get('twitter'),
            artist_data.get('press_kit'),
            artist_data.get('management_contact')
        ]
        
        missing_professional_elements = sum(1 for indicator in professional_indicators if not indicator)
        if missing_professional_elements >= 3:
            score += self.weights['opportunity']['low_professional_presence']
        
        return min(score, 100)
    
    def _calculate_geographic_score(self, mb_data: Dict, artist_data: Dict) -> int:
        """
        Score based on geographic location priority
        Precise Digital focuses on NZ/Australia/Pacific region
        """
        # Get country from various sources
        country = (
            mb_data.get('artist', {}).get('country') or
            mb_data.get('release', {}).get('country') or
            artist_data.get('country')
        )
        
        if not country:
            return self.weights['geographic']['other']  # Default low score
        
        country_str = self._safe_str(country).upper()
        if not country_str:
            return self.weights['geographic']['other']
        
        # Check against target regions
        for region, score_value in self.weights['geographic'].items():
            region_countries = self.target_regions.get(region, [])
            if country_str in region_countries:
                return score_value
        
        # Default for unmatched countries
        return self.weights['geographic']['other']
    
    def _get_most_recent_release_date(self, track_data: Dict, spotify_data: Dict) -> Optional[datetime]:
        """Extract most recent release date from available data"""
        dates = []
        
        # From track data
        if track_data.get('release_date'):
            parsed_date = self._parse_date(track_data['release_date'])
            if parsed_date:
                dates.append(parsed_date)
        
        # From Spotify data
        if spotify_data.get('last_release_date'):
            parsed_date = self._parse_date(spotify_data['last_release_date'])
            if parsed_date:
                dates.append(parsed_date)
        
        return max(dates) if dates else None
    
    def _is_recent_release(self, release_date: datetime) -> bool:
        """Check if release is recent enough to indicate active artist"""
        if not release_date:
            return False
        
        # Consider releases within last 12 months as recent
        cutoff_date = datetime.now() - timedelta(days=365)
        return release_date >= cutoff_date
    
    def _parse_date(self, date_str) -> Optional[datetime]:
        """Parse date string in various formats"""
        if not date_str:
            return None
        
        date_clean = self._safe_str(date_str).strip()
        if not date_clean:
            return None
        
        formats = ['%Y-%m-%d', '%Y-%m', '%Y', '%d-%m-%Y', '%m/%d/%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_clean, fmt)
            except ValueError:
                continue
        
        return None
    
    def _get_lead_tier(self, total_score: float) -> str:
        """Categorize leads by score into tiers"""
        if total_score >= 70:
            return 'A'  # High priority
        elif total_score >= 50:
            return 'B'  # Medium priority  
        elif total_score >= 30:
            return 'C'  # Low priority
        else:
            return 'D'  # Very low priority
    
    def _calculate_confidence(self, artist_data: Dict) -> int:
        """
        Calculate confidence score based on data completeness
        Higher confidence = more complete data for scoring
        """
        confidence_factors = [
            bool(artist_data.get('musicbrainz_data')),
            bool(artist_data.get('spotify_data')),
            bool(artist_data.get('track_data', {}).get('label')),
            bool(artist_data.get('track_data', {}).get('release_date')),
            bool(artist_data.get('spotify_data', {}).get('followers')),
            bool(artist_data.get('musicbrainz_data', {}).get('artist', {}).get('country')),
            bool(artist_data.get('lastfm_data'))
        ]
        
        confidence = (sum(confidence_factors) / len(confidence_factors)) * 100
        return round(confidence)
    
    def _get_scoring_breakdown(self, independence: int, opportunity: int, 
                             geographic: int, artist_data: Dict) -> Dict:
        """Provide detailed breakdown of how scores were calculated"""
        breakdown = {
            'independence': {
                'score': independence,
                'factors': self._get_independence_factors(artist_data),
                'weight': '40%'
            },
            'opportunity': {
                'score': opportunity,
                'factors': self._get_opportunity_factors(artist_data),
                'weight': '40%'
            },
            'geographic': {
                'score': geographic,
                'factors': self._get_geographic_factors(artist_data),
                'weight': '20%'
            }
        }
        
        return breakdown
    
    def _get_independence_factors(self, artist_data: Dict) -> List[str]:
        """Get human-readable factors that influenced independence score"""
        factors = []
        track_data = artist_data.get('track_data', {})
        
        label = self._safe_str(track_data.get('label', '')).lower()
        if not label:
            factors.append("No label information found - assumed self-released")
        elif any(major in label for major in self.major_labels):
            factors.append(f"Major label detected: {label}")
        elif any(dist in label for dist in self.distributors):
            factors.append(f"Digital distributor detected: {label}")
        else:
            factors.append(f"Independent label: {label}")
        
        return factors
    
    def _get_opportunity_factors(self, artist_data: Dict) -> List[str]:
        """Get human-readable factors that influenced opportunity score"""
        factors = []
        track_data = artist_data.get('track_data', {})
        spotify_data = artist_data.get('spotify_data', {})
        
        # Platform availability
        platforms = track_data.get('platforms_available', [])
        if isinstance(platforms, list):
            missing = [p for p in self.major_platforms if p not in platforms]
            if missing:
                factors.append(f"Missing from platforms: {', '.join(missing[:3])}")
        
        # Growth indicators
        followers = self._safe_int(spotify_data.get('followers', 0))
        if 10000 <= followers <= 500000:
            factors.append(f"Growing audience: {followers:,} followers")
        
        # Recent activity
        last_release = self._get_most_recent_release_date(track_data, spotify_data)
        if last_release and self._is_recent_release(last_release):
            factors.append("Recently active (released within 12 months)")
        
        return factors
    
    def _get_geographic_factors(self, artist_data: Dict) -> List[str]:
        """Get human-readable factors that influenced geographic score"""
        factors = []
        mb_data = artist_data.get('musicbrainz_data', {})
        
        country = (
            mb_data.get('artist', {}).get('country') or
            mb_data.get('release', {}).get('country') or
            artist_data.get('country')
        )
        
        if country:
            # Find which region this country belongs to
            country_str = self._safe_str(country).upper()
            for region, countries in self.target_regions.items():
                if country_str in countries:
                    region_name = region.replace('_', ' ').title()
                    factors.append(f"Located in target region: {region_name} ({country_str})")
                    return factors
            
            factors.append(f"Outside target regions: {country_str}")
        else:
            factors.append("Location unknown")
        
        return factors
    
    def _safe_str(self, value) -> str:
        """Safely convert value to string"""
        if value is None:
            return ""
        return str(value).strip()
    
    def _safe_int(self, value) -> int:
        """Safely convert value to integer"""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

# Utility functions for testing and validation
def score_artist_from_isrc(isrc: str) -> Dict:
    """
    Complete scoring pipeline for a single ISRC
    Useful for testing and standalone scoring
    """
    from src.core.pipeline import LeadAggregationPipeline
    from src.core.rate_limiter import RateLimitManager
    
    rate_manager = RateLimitManager()
    pipeline = LeadAggregationPipeline(rate_manager)
    scoring_engine = LeadScoringEngine()
    
    # Process the ISRC
    artist_data = pipeline.process_isrc(isrc)
    
    # Calculate scores
    scores = scoring_engine.calculate_scores(artist_data)
    
    return {
        'isrc': isrc,
        'artist_data': artist_data,
        'scores': scores
    }

def bulk_score_validation(test_isrcs: List[str]) -> Dict:
    """
    Validate scoring algorithm with multiple test cases
    Returns summary statistics and outliers
    """
    results = []
    scoring_engine = LeadScoringEngine()
    
    for isrc in test_isrcs:
        try:
            result = score_artist_from_isrc(isrc)
            results.append(result)
        except Exception as e:
            print(f"Error processing {isrc}: {e}")
    
    if not results:
        return {'error': 'No valid results'}
    
    # Calculate summary stats
    scores = [r['scores']['total_score'] for r in results]
    tiers = [r['scores']['tier'] for r in results]
    
    summary = {
        'total_processed': len(results),
        'average_score': sum(scores) / len(scores),
        'score_range': (min(scores), max(scores)),
        'tier_distribution': {tier: tiers.count(tier) for tier in 'ABCD'},
        'results': results
    }
    
    return summary

if __name__ == "__main__":
    # Test the scoring engine with sample data
    sample_data = {
        'track_data': {
            'isrc': 'TEST123456789',
            'title': 'Test Track',
            'artist_name': 'Test Artist',
            'label': 'Self-Released',
            'release_date': '2024-01-15',
            'platforms_available': ['spotify', 'apple_music']
        },
        'spotify_data': {
            'name': 'Test Artist',
            'followers': 25000,
            'popularity': 45,
            'last_release_date': '2024-01-15'
        },
        'musicbrainz_data': {
            'artist': {
                'name': 'Test Artist',
                'country': 'NZ'
            }
        }
    }
    
    engine = LeadScoringEngine()
    scores = engine.calculate_scores(sample_data)
    
    print("Sample Scoring Result:")
    print(f"Total Score: {scores['total_score']} (Tier {scores['tier']})")
    print(f"Independence: {scores['independence_score']}")
    print(f"Opportunity: {scores['opportunity_score']}")
    print(f"Geographic: {scores['geographic_score']}")
    print(f"Confidence: {scores['confidence']}%")