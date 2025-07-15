"""
COMPLETE config/database.py fix for PostgreSQL JSON index issue
Replace your existing config/database.py with this corrected version
"""

import os
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Boolean, Text, ForeignKey, Index, text, JSON
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the base class for all models
Base = declarative_base()

class Artist(Base):
    """Artist model with all lead generation data"""
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    musicbrainz_id = Column(String(36), unique=True, nullable=True)
    spotify_id = Column(String(22), unique=True, nullable=True)
    
    # Geographic information
    country = Column(String(2), nullable=True)
    region = Column(String(50), nullable=True)
    
    # Genre and style
    genre = Column(String(100), nullable=True)
    
    # Lead scoring
    total_score = Column(Float, default=0.0)
    independence_score = Column(Float, default=0.0)
    opportunity_score = Column(Float, default=0.0)
    geographic_score = Column(Float, default=0.0)
    lead_tier = Column(String(1), default='D')  # A, B, C, D
    
    # Metrics
    monthly_listeners = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    release_count = Column(Integer, default=0)
    last_release_date = Column(DateTime, nullable=True)
    
    # YouTube metrics (NEW - added for your YouTube integration)
    youtube_channel_id = Column(String(100), nullable=True)
    youtube_channel_url = Column(String(255), nullable=True)
    youtube_subscribers = Column(Integer, default=0)
    youtube_total_views = Column(Integer, default=0)
    youtube_video_count = Column(Integer, default=0)
    youtube_upload_frequency = Column(String(20), nullable=True)  # very_active, active, moderate, low, inactive
    youtube_growth_potential = Column(String(20), nullable=True)  # high_potential, moderate_potential, low_potential
    youtube_engagement_rate = Column(Float, default=0.0)
    youtube_last_upload = Column(DateTime, nullable=True)
    
    # Contact information
    contact_email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    social_handles = Column(JSONB, nullable=True)  # Use JSONB for PostgreSQL
    management_contact = Column(String(255), nullable=True)
    
    # Outreach tracking
    outreach_status = Column(String(20), default='not_contacted')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_scraped = Column(DateTime, nullable=True)
    
    # Relationships
    tracks = relationship("Track", back_populates="artist")
    contact_attempts = relationship("ContactAttempt", back_populates="artist")
    outreach_logs = relationship("OutreachLog", back_populates="artist")
    
    # Indexes
    __table_args__ = (
        Index('idx_artists_total_score', 'total_score'),
        Index('idx_artists_lead_tier', 'lead_tier'),
        Index('idx_artists_region', 'region'),
        Index('idx_artists_outreach_status', 'outreach_status'),
        Index('idx_artists_youtube_subscribers', 'youtube_subscribers'),
        Index('idx_artists_social_handles_gin', 'social_handles', postgresql_using='gin'),
    )

class Track(Base):
    """Track model with ISRC and platform data"""
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    isrc = Column(String(12), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    
    # Release information
    release_date = Column(DateTime, nullable=True)
    label = Column(String(255), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Platform IDs
    spotify_id = Column(String(22), nullable=True)
    musicbrainz_id = Column(String(36), nullable=True)
    
    # Metrics
    spotify_popularity = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    artist = relationship("Artist", back_populates="tracks")
    
    # Indexes
    __table_args__ = (
        Index('idx_tracks_isrc', 'isrc'),
        Index('idx_tracks_artist_id', 'artist_id'),
        Index('idx_tracks_release_date', 'release_date'),
    )

class ContactAttempt(Base):
    """Contact discovery attempts and results"""
    __tablename__ = 'contact_attempts'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    
    contact_method = Column(String(20), nullable=False)  # email, social, website, etc.
    contact_value = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)
    confidence_score = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    artist = relationship("Artist", back_populates="contact_attempts")
    
    # Indexes
    __table_args__ = (
        Index('idx_contact_attempts_artist_id', 'artist_id'),
        Index('idx_contact_attempts_method', 'contact_method'),
        Index('idx_contact_attempts_confidence', 'confidence_score'),
    )

class OutreachLog(Base):
    """Outreach tracking and communication history"""
    __tablename__ = 'outreach_logs'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    
    contact_date = Column(DateTime, nullable=False)
    method = Column(String(50), nullable=False)  # email, phone, social, etc.
    notes = Column(Text, nullable=True)
    response_received = Column(Boolean, default=False)
    follow_up_scheduled = Column(DateTime, nullable=True)
    conversion_status = Column(String(20), default='no_response')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    artist = relationship("Artist", back_populates="outreach_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_outreach_logs_artist_id', 'artist_id'),
        Index('idx_outreach_logs_contact_date', 'contact_date'),
        Index('idx_outreach_logs_conversion_status', 'conversion_status'),
    )

# FIXED: ProcessingLog model with proper PostgreSQL JSON indexes
class ProcessingLog(Base):
    """Processing performance and statistics tracking"""
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True)
    processing_time_seconds = Column(Float, nullable=False)
    data_sources_used = Column(JSONB, nullable=True)  # Use JSONB for PostgreSQL
    isrc_processed = Column(String(12), nullable=True)
    artist_name = Column(String(255), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    api_calls_made = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # FIXED: Separate indexes instead of composite B-tree index with JSON
    __table_args__ = (
        # Separate B-tree index for numeric queries
        Index('ix_processing_logs_time', 'processing_time_seconds'),
        # GIN index for JSON operations (supports @>, ?, ?&, ?| operators)
        Index('ix_processing_logs_sources_gin', 'data_sources_used', postgresql_using='gin'),
        # Partial index for performance queries
        Index('ix_processing_logs_performance_partial', 
              'processing_time_seconds',
              postgresql_where=text('data_sources_used IS NOT NULL')),
        # Additional useful indexes
        Index('ix_processing_logs_success', 'success'),
        Index('ix_processing_logs_created_at', 'created_at'),
        Index('ix_processing_logs_isrc', 'isrc_processed'),
    )

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            # Fallback to SQLite for development
            self.database_url = 'sqlite:///data/precise_leads.db'
            os.makedirs('data', exist_ok=True)
        
        # Handle Render.com PostgreSQL URL format
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        self.engine = None
        self.SessionLocal = None
        self.session = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database engine and session"""
        try:
            # Create engine with proper PostgreSQL settings
            if 'postgresql://' in self.database_url:
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=False,  # Set to True for SQL debugging
                    connect_args={
                        "options": "-c timezone=UTC"
                    }
                )
            else:
                # SQLite settings
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    connect_args={"check_same_thread": False}
                )
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.session = self.SessionLocal()
            
            logger.info(f"✅ Database connection established: {self.database_url.split('@')[0]}@***")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics including YouTube metrics"""
        try:
            with self.get_session() as session:
                # Basic stats
                total_artists = session.query(Artist).count()
                total_tracks = session.query(Track).count()
                
                # Lead tier distribution
                tier_stats = {}
                for tier in ['A', 'B', 'C', 'D']:
                    count = session.query(Artist).filter(Artist.lead_tier == tier).count()
                    tier_stats[tier] = count
                
                # Geographic distribution
                geo_stats = {}
                regions = session.query(Artist.region, func.count(Artist.id)).group_by(Artist.region).all()
                for region, count in regions:
                    geo_stats[region or 'unknown'] = count
                
                # Outreach status
                outreach_stats = {}
                statuses = session.query(Artist.outreach_status, func.count(Artist.id)).group_by(Artist.outreach_status).all()
                for status, count in statuses:
                    outreach_stats[status or 'unknown'] = count
                
                # YouTube statistics
                youtube_stats = {
                    'artists_with_youtube': session.query(Artist).filter(Artist.youtube_channel_id.isnot(None)).count(),
                    'total_youtube_subscribers': session.query(func.sum(Artist.youtube_subscribers)).scalar() or 0,
                    'avg_youtube_subscribers': session.query(func.avg(Artist.youtube_subscribers)).filter(Artist.youtube_subscribers > 0).scalar() or 0,
                    'high_potential_channels': session.query(Artist).filter(Artist.youtube_growth_potential == 'high_potential').count(),
                }
                
                return {
                    'total_artists': total_artists,
                    'total_tracks': total_tracks,
                    'tier_distribution': tier_stats,
                    'geographic_distribution': geo_stats,
                    'outreach_distribution': outreach_stats,
                    'youtube_statistics': youtube_stats,
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {}
    
    def get_youtube_opportunities(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get artists with YouTube opportunities"""
        try:
            with self.get_session() as session:
                # Artists with high YouTube growth potential or no YouTube presence
                opportunities = session.query(Artist).filter(
                    (Artist.youtube_growth_potential == 'high_potential') |
                    (Artist.youtube_channel_id.is_(None) & (Artist.monthly_listeners > 5000))
                ).order_by(Artist.total_score.desc()).limit(limit).all()
                
                result = []
                for artist in opportunities:
                    result.append({
                        'id': artist.id,
                        'name': artist.name,
                        'total_score': artist.total_score,
                        'monthly_listeners': artist.monthly_listeners,
                        'youtube_subscribers': artist.youtube_subscribers or 0,
                        'youtube_growth_potential': artist.youtube_growth_potential,
                        'has_youtube_channel': bool(artist.youtube_channel_id),
                        'opportunity_type': 'high_potential' if artist.youtube_growth_potential == 'high_potential' else 'no_youtube_presence'
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get YouTube opportunities: {e}")
            return []
    
    def update_youtube_data(self, artist_id: int, youtube_data: Dict[str, Any]) -> bool:
        """Update YouTube data for an artist"""
        try:
            with self.get_session() as session:
                artist = session.query(Artist).filter(Artist.id == artist_id).first()
                if not artist:
                    return False
                
                # Update YouTube fields
                for field, value in youtube_data.items():
                    if hasattr(artist, f'youtube_{field}'):
                        setattr(artist, f'youtube_{field}', value)
                
                artist.updated_at = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update YouTube data: {e}")
            return False

def init_db():
    """Initialize database tables"""
    try:
        db_manager = DatabaseManager()
        
        logger.info("🔄 Initializing database...")
        
        # Create all tables - this is where the error was occurring
        Base.metadata.create_all(db_manager.engine)
        
        logger.info("✅ Database tables created successfully")
        
        # Test the database connection
        with db_manager.get_session() as session:
            test_query = session.execute(text("SELECT 1")).scalar()
            if test_query == 1:
                logger.info("✅ Database connection test successful")
            else:
                logger.error("❌ Database connection test failed")
                
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

# Create global database manager instance
db_manager = DatabaseManager()

# Export models and manager
__all__ = [
    'Base', 'Artist', 'Track', 'ContactAttempt', 'OutreachLog', 'ProcessingLog',
    'DatabaseManager', 'db_manager', 'init_db'
]