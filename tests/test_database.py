# tests/test_database.py
"""
Test database operations
"""
import pytest
from datetime import datetime

from src.models.database import Artist, Track, ContactAttempt, DatabaseManager

def test_artist_creation(temp_db):
    """Test creating artist record"""
    artist = Artist(
        name='Test Artist',
        country='NZ',
        region='new_zealand',
        total_score=75.5,
        lead_tier='A'
    )
    
    temp_db.add(artist)
    temp_db.commit()
    
    retrieved = temp_db.query(Artist).filter_by(name='Test Artist').first()
    assert retrieved is not None
    assert retrieved.country == 'NZ'
    assert retrieved.total_score == 75.5

def test_track_creation(temp_db, sample_artist_data):
    """Test creating track record"""
    # Create artist first
    artist = Artist(**sample_artist_data)
    temp_db.add(artist)
    temp_db.commit()
    
    # Create track
    track = Track(
        isrc='TEST12345678',
        title='Test Track',
        artist_id=artist.id,
        release_date=datetime(2024, 1, 15),
        label='Test Label'
    )
    
    temp_db.add(track)
    temp_db.commit()
    
    retrieved = temp_db.query(Track).filter_by(isrc='TEST12345678').first()
    assert retrieved is not None
    assert retrieved.title == 'Test Track'
    assert retrieved.artist_id == artist.id

def test_database_manager_save_artist_data(temp_db):
    """Test DatabaseManager save functionality"""
    db_manager = DatabaseManager()
    db_manager.session = temp_db  # Use test session
    
    artist_data = {
        'name': 'Test Artist',
        'country': 'NZ',
        'region': 'new_zealand',
        'scores': {
            'total_score': 80,
            'independence_score': 40,
            'opportunity_score': 25,
            'geographic_score': 30,
            'tier': 'A'
        },
        'track_data': {
            'isrc': 'TEST12345678',
            'title': 'Test Track'
        },
        'contacts': [
            {
                'type': 'email',
                'value': 'test@example.com',
                'confidence': 85,
                'source': 'website'
            }
        ]
    }
    
    artist_id = db_manager.save_artist_data(artist_data)
    assert artist_id > 0
    
    # Verify artist was saved
    artist = temp_db.query(Artist).filter_by(id=artist_id).first()
    assert artist.name == 'Test Artist'
    assert artist.total_score == 80
    
    # Verify track was saved
    track = temp_db.query(Track).filter_by(artist_id=artist_id).first()
    assert track.isrc == 'TEST12345678'
    
    # Verify contact was saved
    contact = temp_db.query(ContactAttempt).filter_by(artist_id=artist_id).first()
    assert contact.contact_value == 'test@example.com'

def test_get_leads_filtering(temp_db):
    """Test lead filtering functionality"""
    db_manager = DatabaseManager()
    db_manager.session = temp_db
    
    # Create test artists
    artists = [
        Artist(name='NZ Artist A', country='NZ', region='new_zealand', 
               total_score=85, lead_tier='A'),
        Artist(name='AU Artist B', country='AU', region='australia', 
               total_score=65, lead_tier='B'),
        Artist(name='US Artist C', country='US', region='other', 
               total_score=45, lead_tier='C')
    ]
    
    for artist in artists:
        temp_db.add(artist)
    temp_db.commit()
    
    # Test tier filtering
    a_tier_leads = db_manager.get_leads(tier='A')
    assert len(a_tier_leads) == 1
    assert a_tier_leads[0].name == 'NZ Artist A'
    
    # Test region filtering
    nz_leads = db_manager.get_leads(region='new_zealand')
    assert len(nz_leads) == 1
    assert nz_leads[0].country == 'NZ'

if __name__ == "__main__":
    pytest.main([__file__])