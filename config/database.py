"""
Database models and management for Precise Digital Lead Generation Tool
Complete SQLAlchemy models with YouTube integration and Prism Analytics branding
"""
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, JSON, Index, func, text, and_, or_
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

# Import settings
try:
    from config.settings import settings
except ImportError:
    # Fallback for testing
    class MockSettings:
        def get_database_url(self):
            return "sqlite:///data/precise_leads.db"
    settings = MockSettings()

# Create base class
Base = declarative_base()

class Artist(Base):
    """
    Artist model with comprehensive data including YouTube metrics
    Central entity for lead generation and tracking
    """
    __tablename__ = 'artists'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic artist information
    name = Column(String(255), nullable=False, index=True)
    musicbrainz_id = Column(String(36), unique=True, index=True)  # UUID
    spotify_id = Column(String(22), unique=True, index=True)
    
    # Geographic information
    country = Column(String(2))  # ISO country code
    region = Column(String(50), index=True)  # Target region classification
    
    # Musical information
    genre = Column(String(100), index=True)
    
    # Engagement metrics
    monthly_listeners = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    release_count = Column(Integer, default=0)
    last_release_date = Column(DateTime)
    
    # Lead scoring
    independence_score = Column(Integer, default=0)
    opportunity_score = Column(Integer, default=0)
    geographic_score = Column(Integer, default=0)
    total_score = Column(Float, default=0.0, index=True)
    lead_tier = Column(String(1), index=True)  # A, B, C, D
    
    # YouTube metrics (NEW - YouTube integration)
    youtube_channel_id = Column(String(24))  # YouTube channel ID
    youtube_channel_url = Column(String(255))
    youtube_subscribers = Column(Integer, default=0)
    youtube_total_views = Column(Integer, default=0)
    youtube_video_count = Column(Integer, default=0)
    youtube_upload_frequency = Column(String(20))  # very_active, active, moderate, low, inactive
    youtube_engagement_rate = Column(Float, default=0.0)
    youtube_growth_potential = Column(String(20))  # high_potential, moderate_potential, low_potential
    youtube_last_upload = Column(DateTime)
    
    # Contact information
    contact_email = Column(String(255))
    website = Column(String(255))
    social_handles = Column(JSON)  # Dictionary of platform: handle
    management_contact = Column(String(255))
    
    # Outreach tracking
    outreach_status = Column(String(20), default='not_contacted', index=True)
    # not_contacted, contacted, responded, interested, not_interested, converted
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tracks = relationship("Track", back_populates="artist", cascade="all, delete-orphan")
    contact_attempts = relationship("ContactAttempt", back_populates="artist", cascade="all, delete-orphan")
    outreach_logs = relationship("OutreachLog", back_populates="artist", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_artist_scoring', 'total_score', 'lead_tier'),
        Index('ix_artist_location', 'country', 'region'),
        Index('ix_artist_youtube', 'youtube_channel_id', 'youtube_subscribers'),
        Index('ix_artist_outreach', 'outreach_status', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert artist to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'musicbrainz_id': self.musicbrainz_id,
            'spotify_id': self.spotify_id,
            'country': self.country,
            'region': self.region,
            'genre': self.genre,
            'monthly_listeners': self.monthly_listeners,
            'scores': {
                'independence': self.independence_score,
                'opportunity': self.opportunity_score,
                'geographic': self.geographic_score,
                'total': self.total_score,
                'tier': self.lead_tier
            },
            'youtube_metrics': {
                'channel_id': self.youtube_channel_id,
                'channel_url': self.youtube_channel_url,
                'subscribers': self.youtube_subscribers,
                'total_views': self.youtube_total_views,
                'video_count': self.youtube_video_count,
                'upload_frequency': self.youtube_upload_frequency,
                'engagement_rate': self.youtube_engagement_rate,
                'growth_potential': self.youtube_growth_potential,
                'last_upload': self.youtube_last_upload.isoformat() if self.youtube_last_upload else None
            },
            'contact_info': {
                'email': self.contact_email,
                'website': self.website,
                'social_handles': self.social_handles,
                'management_contact': self.management_contact
            },
            'outreach_status': self.outreach_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Track(Base):
    """
    Track model for individual recordings
    Linked to artists and contains ISRC-based metadata
    """
    __tablename__ = 'tracks'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Track identifiers
    isrc = Column(String(12), unique=True, nullable=False, index=True)
    musicbrainz_recording_id = Column(String(36), unique=True, index=True)
    spotify_track_id = Column(String(22), index=True)
    
    # Track information
    title = Column(String(255), nullable=False)
    release_date = Column(DateTime, index=True)
    duration_ms = Column(Integer)
    
    # Release information
    label = Column(String(255), index=True)
    release_title = Column(String(255))
    
    # Platform availability
    platforms_available = Column(JSON)  # List of platforms
    
    # Performance metrics
    spotify_popularity = Column(Integer, default=0)
    lastfm_playcount = Column(Integer, default=0)
    
    # Foreign key
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="tracks")
    
    # Indexes
    __table_args__ = (
        Index('ix_track_performance', 'spotify_popularity', 'lastfm_playcount'),
        Index('ix_track_release', 'release_date', 'label'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert track to dictionary for API responses"""
        return {
            'id': self.id,
            'isrc': self.isrc,
            'title': self.title,
            'artist_id': self.artist_id,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'label': self.label,
            'platforms_available': self.platforms_available,
            'spotify_popularity': self.spotify_popularity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContactAttempt(Base):
    """
    Contact attempts and discovered contact methods
    Tracks different ways to reach artists including YouTube channels
    """
    __tablename__ = 'contact_attempts'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Contact information
    contact_method = Column(String(50), nullable=False, index=True)  # email, social, website, youtube_channel, etc.
    contact_value = Column(String(255), nullable=False)
    platform = Column(String(50))  # instagram, twitter, youtube, email, etc.
    
    # Quality assessment
    confidence_score = Column(Integer, default=50)  # 0-100 confidence in contact validity
    source = Column(String(100))  # Where this contact was found
    verified = Column(Boolean, default=False)
    
    # Contact attempt tracking
    last_attempted = Column(DateTime)
    attempt_count = Column(Integer, default=0)
    response_received = Column(Boolean, default=False)
    
    # Foreign key
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="contact_attempts")
    
    # Indexes
    __table_args__ = (
        Index('ix_contact_quality', 'confidence_score', 'verified'),
        Index('ix_contact_method', 'contact_method', 'platform'),
    )

class OutreachLog(Base):
    """
    Outreach activity log for tracking communication with artists
    Part of the CRM functionality for lead management
    """
    __tablename__ = 'outreach_logs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Outreach details
    contact_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    method = Column(String(50), nullable=False)  # email, social_dm, youtube_comment, phone, etc.
    notes = Column(Text)
    
    # Follow-up tracking
    follow_up_scheduled = Column(DateTime, index=True)
    follow_up_completed = Column(Boolean, default=False)
    
    # Conversion tracking
    conversion_status = Column(String(20), default='no_response', index=True)
    # no_response, interested, not_interested, converted, follow_up_needed
    
    # Foreign key
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="outreach_logs")

class ProcessingLog(Base):
    """
    Log of ISRC processing for debugging and monitoring
    Tracks the Prism Analytics Engine processing pipeline
    """
    __tablename__ = 'processing_logs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Processing details
    isrc = Column(String(12), index=True)
    processing_status = Column(String(20), nullable=False, index=True)  # started, completed, failed
    data_sources_used = Column(JSON)  # List of APIs called
    processing_time_seconds = Column(Float)
    
    # Error tracking
    error_message = Column(Text)
    error_type = Column(String(100))
    
    # Results summary
    artist_found = Column(Boolean, default=False)
    lead_score = Column(Float)
    youtube_data_found = Column(Boolean, default=False)  # NEW: YouTube tracking
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_processing_status', 'processing_status', 'created_at'),
        Index('ix_processing_performance', 'processing_time_seconds', 'data_sources_used'),
    )

class DatabaseManager:
    """
    Database management class with connection handling and utility methods
    Handles both development (SQLite) and production (PostgreSQL) scenarios
    """
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.session = None
        self._setup_database()
    
    def _setup_database(self):
        """Initialize database connection and session factory"""
        try:
            database_url = settings.get_database_url()
            
            # Create engine with appropriate settings
            if database_url.startswith('sqlite'):
                self.engine = create_engine(
                    database_url,
                    echo=settings.database.echo,
                    pool_pre_ping=True
                )
            else:
                # PostgreSQL or other databases
                self.engine = create_engine(
                    database_url,
                    echo=settings.database.echo,
                    pool_size=settings.database.pool_size,
                    max_overflow=settings.database.max_overflow,
                    pool_pre_ping=settings.database.pool_pre_ping
                )
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.session = self.session_factory()
            
            print(f"✅ Database connection established: {database_url}")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        if not self.session:
            self.session = self.session_factory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup"""
        if self.session:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
            # Note: We don't close the session here to maintain it across requests
    
    def save_artist_data(self, artist_data: Dict[str, Any]) -> int:
        """
        Save or update artist data including YouTube metrics
        Returns artist ID
        """
        try:
            # Check if artist already exists
            existing_artist = self.session.query(Artist).filter(
                or_(
                    Artist.name == artist_data['name'],
                    Artist.musicbrainz_id == artist_data.get('musicbrainz_id'),
                    Artist.spotify_id == artist_data.get('spotify_id')
                )
            ).first()
            
            if existing_artist:
                # Update existing artist
                for key, value in artist_data.items():
                    if key in ['scores']:
                        # Handle scores dict
                        existing_artist.independence_score = value.get('independence_score', 0)
                        existing_artist.opportunity_score = value.get('opportunity_score', 0)
                        existing_artist.geographic_score = value.get('geographic_score', 0)
                        existing_artist.total_score = value.get('total_score', 0.0)
                        existing_artist.lead_tier = value.get('tier', 'D')
                    elif key == 'contacts':
                        # Handle contacts separately
                        self._save_contact_attempts(existing_artist.id, value)
                    elif key == 'track_data':
                        # Handle track data separately
                        if value:
                            self._save_track_data(existing_artist.id, value)
                    elif hasattr(existing_artist, key):
                        setattr(existing_artist, key, value)
                
                existing_artist.updated_at = datetime.utcnow()
                self.session.flush()
                return existing_artist.id
            
            else:
                # Create new artist
                new_artist = Artist(
                    name=artist_data['name'],
                    musicbrainz_id=artist_data.get('musicbrainz_id'),
                    spotify_id=artist_data.get('spotify_id'),
                    country=artist_data.get('country'),
                    region=artist_data.get('region'),
                    genre=artist_data.get('genre'),
                    monthly_listeners=artist_data.get('monthly_listeners', 0),
                    # YouTube metrics
                    youtube_channel_id=artist_data.get('youtube_channel_id'),
                    youtube_channel_url=artist_data.get('youtube_channel_url'),
                    youtube_subscribers=artist_data.get('youtube_subscribers', 0),
                    youtube_total_views=artist_data.get('youtube_total_views', 0),
                    youtube_video_count=artist_data.get('youtube_video_count', 0),
                    youtube_upload_frequency=artist_data.get('youtube_upload_frequency'),
                    youtube_engagement_rate=artist_data.get('youtube_engagement_rate', 0.0),
                    youtube_growth_potential=artist_data.get('youtube_growth_potential'),
                    youtube_last_upload=artist_data.get('youtube_last_upload')
                )
                
                # Add scores if provided
                if 'scores' in artist_data:
                    scores = artist_data['scores']
                    new_artist.independence_score = scores.get('independence_score', 0)
                    new_artist.opportunity_score = scores.get('opportunity_score', 0)
                    new_artist.geographic_score = scores.get('geographic_score', 0)
                    new_artist.total_score = scores.get('total_score', 0.0)
                    new_artist.lead_tier = scores.get('tier', 'D')
                
                self.session.add(new_artist)
                self.session.flush()
                
                # Save related data
                if 'contacts' in artist_data:
                    self._save_contact_attempts(new_artist.id, artist_data['contacts'])
                
                if 'track_data' in artist_data and artist_data['track_data']:
                    self._save_track_data(new_artist.id, artist_data['track_data'])
                
                return new_artist.id
        
        except Exception as e:
            self.session.rollback()
            print(f"Error saving artist data: {e}")
            raise
    
    def _save_contact_attempts(self, artist_id: int, contacts: List[Dict]):
        """Save contact attempts for an artist"""
        for contact in contacts:
            existing_contact = self.session.query(ContactAttempt).filter(
                and_(
                    ContactAttempt.artist_id == artist_id,
                    ContactAttempt.contact_value == contact['value'],
                    ContactAttempt.contact_method == contact['type']
                )
            ).first()
            
            if not existing_contact:
                new_contact = ContactAttempt(
                    artist_id=artist_id,
                    contact_method=contact['type'],
                    contact_value=contact['value'],
                    platform=contact.get('platform', ''),
                    confidence_score=contact.get('confidence', 50),
                    source=contact.get('source', '')
                )
                self.session.add(new_contact)
    
    def _save_track_data(self, artist_id: int, track_data: Dict):
        """Save track data for an artist"""
        if not track_data.get('isrc'):
            return
        
        existing_track = self.session.query(Track).filter(
            Track.isrc == track_data['isrc']
        ).first()
        
        if not existing_track:
            new_track = Track(
                isrc=track_data['isrc'],
                title=track_data.get('title', ''),
                artist_id=artist_id,
                musicbrainz_recording_id=track_data.get('musicbrainz_recording_id'),
                spotify_track_id=track_data.get('spotify_track_id'),
                release_date=track_data.get('release_date'),
                label=track_data.get('label'),
                platforms_available=track_data.get('platforms_available', []),
                spotify_popularity=track_data.get('spotify_popularity', 0),
                lastfm_playcount=track_data.get('lastfm_playcount', 0)
            )
            self.session.add(new_track)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics including YouTube metrics"""
        try:
            # Basic counts
            total_artists = self.session.query(Artist).count()
            total_tracks = self.session.query(Track).count()
            
            # Lead tier distribution
            tier_distribution = {}
            for tier in ['A', 'B', 'C', 'D']:
                count = self.session.query(Artist).filter(Artist.lead_tier == tier).count()
                tier_distribution[f'tier_{tier}'] = count
            
            # Geographic distribution
            geographic_stats = self.session.query(
                Artist.region,
                func.count(Artist.id).label('count')
            ).group_by(Artist.region).all()
            
            geographic_distribution = {region: count for region, count in geographic_stats}
            
            # Outreach status distribution
            outreach_stats = self.session.query(
                Artist.outreach_status,
                func.count(Artist.id).label('count')
            ).group_by(Artist.outreach_status).all()
            
            outreach_distribution = {status: count for status, count in outreach_stats}
            
            # YouTube statistics (NEW)
            youtube_stats = self._get_youtube_statistics()
            
            # Recent activity
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_artists = self.session.query(Artist).filter(
                Artist.created_at >= thirty_days_ago
            ).count()
            
            # Top scoring artists
            top_artists = self.session.query(Artist).filter(
                Artist.total_score > 0
            ).order_by(Artist.total_score.desc()).limit(5).all()
            
            return {
                'total_artists': total_artists,
                'total_tracks': total_tracks,
                'tier_distribution': tier_distribution,
                'geographic_distribution': geographic_distribution,
                'outreach_distribution': outreach_distribution,
                'youtube_statistics': youtube_stats,  # NEW
                'recent_activity': {
                    'new_artists_30_days': recent_artists,
                    'last_updated': datetime.utcnow().isoformat()
                },
                'top_artists': [
                    {
                        'name': artist.name,
                        'score': artist.total_score,
                        'tier': artist.lead_tier,
                        'country': artist.country
                    }
                    for artist in top_artists
                ]
            }
        
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}
    
    def _get_youtube_statistics(self) -> Dict[str, Any]:
        """Get YouTube-specific statistics (NEW method)"""
        try:
            # Artists with YouTube channels
            artists_with_youtube = self.session.query(Artist).filter(
                Artist.youtube_channel_id.isnot(None)
            ).count()
            
            # Total YouTube subscribers across all artists
            total_subscribers = self.session.query(
                func.sum(Artist.youtube_subscribers)
            ).filter(
                Artist.youtube_subscribers > 0
            ).scalar() or 0
            
            # Average subscribers
            avg_subscribers = self.session.query(
                func.avg(Artist.youtube_subscribers)
            ).filter(
                Artist.youtube_subscribers > 0
            ).scalar() or 0
            
            # High potential channels
            high_potential_channels = self.session.query(Artist).filter(
                Artist.youtube_growth_potential == 'high_potential'
            ).count()
            
            # Upload frequency distribution
            upload_frequency_stats = self.session.query(
                Artist.youtube_upload_frequency,
                func.count(Artist.id).label('count')
            ).filter(
                Artist.youtube_upload_frequency.isnot(None)
            ).group_by(Artist.youtube_upload_frequency).all()
            
            upload_frequency_distribution = {
                freq: count for freq, count in upload_frequency_stats
            }
            
            return {
                'artists_with_youtube': artists_with_youtube,
                'total_youtube_subscribers': int(total_subscribers),
                'avg_youtube_subscribers': round(float(avg_subscribers)),
                'high_potential_channels': high_potential_channels,
                'upload_frequency_distribution': upload_frequency_distribution
            }
        
        except Exception as e:
            print(f"Error getting YouTube statistics: {e}")
            return {}
    
    def get_youtube_opportunities(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get artists with YouTube opportunities for targeted outreach"""
        try:
            # Artists with underperforming YouTube relative to Spotify
            underperforming_youtube = self.session.query(Artist).filter(
                and_(
                    Artist.monthly_listeners > 10000,
                    Artist.youtube_subscribers < Artist.monthly_listeners * 0.3,
                    Artist.youtube_channel_id.isnot(None)
                )
            ).order_by(Artist.monthly_listeners.desc()).limit(limit // 2).all()
            
            # Artists with no YouTube presence but good Spotify following
            no_youtube_presence = self.session.query(Artist).filter(
                and_(
                    Artist.monthly_listeners > 5000,
                    Artist.youtube_channel_id.is_(None)
                )
            ).order_by(Artist.monthly_listeners.desc()).limit(limit // 2).all()
            
            opportunities = []
            
            # Process underperforming YouTube channels
            for artist in underperforming_youtube:
                opportunities.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'opportunity_type': 'youtube_underperforming',
                    'spotify_followers': artist.monthly_listeners,
                    'youtube_subscribers': artist.youtube_subscribers,
                    'youtube_channel_url': artist.youtube_channel_url,
                    'potential': 'YouTube optimization and content strategy',
                    'priority_score': artist.total_score
                })
            
            # Process no YouTube presence artists
            for artist in no_youtube_presence:
                opportunities.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'opportunity_type': 'no_youtube_presence',
                    'spotify_followers': artist.monthly_listeners,
                    'youtube_subscribers': 0,
                    'youtube_channel_url': None,
                    'potential': 'YouTube channel creation and setup',
                    'priority_score': artist.total_score
                })
            
            # Sort by priority score
            opportunities.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return opportunities[:limit]
        
        except Exception as e:
            print(f"Error getting YouTube opportunities: {e}")
            return []
    
    def update_youtube_data(self, artist_id: int, youtube_data: Dict[str, Any]) -> bool:
        """Update YouTube data for a specific artist"""
        try:
            artist = self.session.query(Artist).filter(Artist.id == artist_id).first()
            if not artist:
                return False
            
            # Update YouTube fields
            for field, value in youtube_data.items():
                if hasattr(artist, field):
                    setattr(artist, field, value)
            
            artist.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        
        except Exception as e:
            self.session.rollback()
            print(f"Error updating YouTube data: {e}")
            return False
    
    def log_processing(self, isrc: str, status: str, **kwargs):
        """Log ISRC processing for monitoring"""
        try:
            log_entry = ProcessingLog(
                isrc=isrc,
                processing_status=status,
                data_sources_used=kwargs.get('data_sources_used', []),
                processing_time_seconds=kwargs.get('processing_time', 0),
                error_message=kwargs.get('error_message'),
                error_type=kwargs.get('error_type'),
                artist_found=kwargs.get('artist_found', False),
                lead_score=kwargs.get('lead_score'),
                youtube_data_found=kwargs.get('youtube_data_found', False)
            )
            self.session.add(log_entry)
            self.session.commit()
        except Exception as e:
            print(f"Error logging processing: {e}")
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Clean up old processing logs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            deleted = self.session.query(ProcessingLog).filter(
                ProcessingLog.created_at < cutoff_date
            ).delete()
            self.session.commit()
            print(f"Cleaned up {deleted} old processing logs")
        except Exception as e:
            print(f"Error cleaning up logs: {e}")

def init_db():
    """Initialize database tables"""
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Create database manager instance
        db_manager = DatabaseManager()
        
        # Create all tables
        Base.metadata.create_all(db_manager.engine)
        
        print("✅ Database tables created successfully")
        print("🎵 Prism Analytics Engine database initialized")
        
        # Test the connection
        with db_manager as db:
            test_query = db.session.execute(text("SELECT 1")).scalar()
            if test_query == 1:
                print("✅ Database connection test successful")
        
        return db_manager
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# Export commonly used classes and functions
__all__ = [
    'Base',
    'Artist',
    'Track', 
    'ContactAttempt',
    'OutreachLog',
    'ProcessingLog',
    'DatabaseManager',
    'init_db'
]