# tests/test_scoring.py
"""
Test lead scoring algorithm
"""
import pytest
from datetime import datetime, timedelta

from src.core.scoring import LeadScoringEngine

@pytest.fixture
def scoring_engine():
    """Scoring engine instance"""
    return LeadScoringEngine()

def test_independence_scoring_self_released(scoring_engine):
    """Test independence scoring for self-released artists"""
    artist_data = {
        'track_data': {
            'label': 'Self-Released',
            'artist_name': 'Test Artist'
        },
        'spotify_data': {'name': 'Test Artist'},
        'musicbrainz_data': {}
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    assert scores['independence_score'] == 40  # Self-released should get 40 points

def test_independence_scoring_major_label(scoring_engine):
    """Test independence scoring for major label artists"""
    artist_data = {
        'track_data': {
            'label': 'Universal Music Group',
            'artist_name': 'Test Artist'
        },
        'spotify_data': {'name': 'Test Artist'},
        'musicbrainz_data': {}
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    assert scores['independence_score'] == 0  # Major label should get 0 points

def test_geographic_scoring_new_zealand(scoring_engine):
    """Test geographic scoring for New Zealand artists"""
    artist_data = {
        'track_data': {},
        'spotify_data': {},
        'musicbrainz_data': {
            'artist': {'country': 'NZ'}
        }
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    assert scores['geographic_score'] == 30  # NZ should get 30 points

def test_geographic_scoring_australia(scoring_engine):
    """Test geographic scoring for Australian artists"""
    artist_data = {
        'track_data': {},
        'spotify_data': {},
        'musicbrainz_data': {
            'artist': {'country': 'AU'}
        }
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    assert scores['geographic_score'] == 25  # AU should get 25 points

def test_opportunity_scoring_missing_platforms(scoring_engine):
    """Test opportunity scoring for missing platforms"""
    artist_data = {
        'track_data': {
            'platforms_available': ['spotify'],  # Missing other major platforms
        },
        'spotify_data': {'followers': 50000, 'popularity': 40},
        'musicbrainz_data': {}
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    # Should get points for missing platforms and growing streams
    assert scores['opportunity_score'] > 0

def test_opportunity_scoring_growing_artist(scoring_engine):
    """Test opportunity scoring for growing artists"""
    artist_data = {
        'track_data': {
            'platforms_available': ['spotify', 'apple_music', 'youtube_music'],
            'release_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        },
        'spotify_data': {
            'followers': 25000,  # In the sweet spot
            'popularity': 35,
            'last_release_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        },
        'musicbrainz_data': {}
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    # Should get points for growing streams and recent activity
    assert scores['opportunity_score'] >= 25

def test_lead_tier_calculation(scoring_engine):
    """Test lead tier assignment based on total score"""
    # High scoring artist (Tier A)
    high_score_data = {
        'track_data': {'label': 'Self-Released'},
        'spotify_data': {'followers': 50000, 'popularity': 40},
        'musicbrainz_data': {'artist': {'country': 'NZ'}}
    }
    
    scores = scoring_engine.calculate_scores(high_score_data)
    assert scores['tier'] in ['A', 'B']  # Should be high tier
    
    # Low scoring artist (Tier C/D)
    low_score_data = {
        'track_data': {'label': 'Universal Music'},
        'spotify_data': {'followers': 100, 'popularity': 5},
        'musicbrainz_data': {'artist': {'country': 'US'}}
    }
    
    scores = scoring_engine.calculate_scores(low_score_data)
    assert scores['tier'] in ['C', 'D']  # Should be low tier

def test_confidence_calculation(scoring_engine):
    """Test confidence score calculation"""
    # Complete data should have high confidence
    complete_data = {
        'track_data': {'label': 'Test Label', 'release_date': '2024-01-01'},
        'spotify_data': {'followers': 10000, 'popularity': 30},
        'musicbrainz_data': {'artist': {'country': 'NZ'}},
        'lastfm_data': {'artist': {'listeners': 5000}}
    }
    
    scores = scoring_engine.calculate_scores(complete_data)
    assert scores['confidence'] > 70
    
    # Incomplete data should have lower confidence
    incomplete_data = {
        'track_data': {},
        'spotify_data': {},
        'musicbrainz_data': {}
    }
    
    scores = scoring_engine.calculate_scores(incomplete_data)
    assert scores['confidence'] < 50

def test_scoring_breakdown(scoring_engine):
    """Test that scoring breakdown is provided"""
    artist_data = {
        'track_data': {'label': 'Indie Label'},
        'spotify_data': {'followers': 15000},
        'musicbrainz_data': {'artist': {'country': 'AU'}}
    }
    
    scores = scoring_engine.calculate_scores(artist_data)
    
    assert 'scoring_breakdown' in scores
    breakdown = scores['scoring_breakdown']
    
    assert 'independence' in breakdown
    assert 'opportunity' in breakdown
    assert 'geographic' in breakdown
    
    # Each section should have score, factors, and weight
    for section in breakdown.values():
        assert 'score' in section
        assert 'factors' in section
        assert 'weight' in section