"""
Database configuration for ISRC Analyzer with PostgreSQL support for Render deployment
Supports both SQLite for development and PostgreSQL for production
"""
import os
import json
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

def get_database_url():
    """Get database URL based on environment"""
    # Check for Render PostgreSQL URL first
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Render provides PostgreSQL URL, use it directly
        print(f"✅ Using PostgreSQL database from Render")
        return database_url
    
    # Fallback to SQLite for development
    db_path = os.path.join(os.getcwd(), 'data', 'isrc_analyzer.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    sqlite_url = f'sqlite:///{db_path}'
    print(f"🛠️  Using SQLite database for development: {db_path}")
    return sqlite_url

# Database Models
class Artist(Base):
    """Artist model with YouTube integration fields"""
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    musicbrainz_id = Column(String(100), unique=True)
    spotify_id = Column(String(100), unique=True)
    country = Column(String(10))
    region = Column(String(50))
    genre = Column(String(100))
    
    # Scoring
    total_score = Column(Float, default=0.0)
    independence_score = Column(Float, default=0.0)
    opportunity_score = Column(Float, default=0.0)
    geographic_score = Column(Float, default=0.0)
    lead_tier = Column(String(1), default='D')
    
    # Music platform metrics
    monthly_listeners = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    release_count = Column(Integer, default=0)
    last_release_date = Column(DateTime)
    
    # YouTube integration fields
    youtube_channel_id = Column(String(100))
    youtube_channel_url = Column(String(255))
    youtube_subscribers = Column(Integer, default=0)
    youtube_total_views = Column(Integer, default=0)
    youtube_video_count = Column(Integer, default=0)
    youtube_upload_frequency = Column(String(50))  # 'very_active', 'active', 'occasional', 'inactive'
    youtube_engagement_rate = Column(Float, default=0.0)
    youtube_growth_potential = Column(String(50))  # 'high_potential', 'moderate', 'low', 'unknown'
    youtube_last_upload = Column(DateTime)
    
    # Contact information
    contact_email = Column(String(255))
    website = Column(String(255))
    social_handles = Column(JSON)
    management_contact = Column(String(255))
    
    # Outreach tracking
    outreach_status = Column(String(50), default='not_contacted')
    last_contacted = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)
    
    # Relationships
    tracks = relationship("Track", back_populates="artist")
    contact_attempts = relationship("ContactAttempt", back_populates="artist")
    outreach_logs = relationship("OutreachLog", back_populates="artist")

class Track(Base):
    """Track model"""
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    isrc = Column(String(20), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    
    # Track metadata
    musicbrainz_recording_id = Column(String(100))
    spotify_track_id = Column(String(100))
    release_date = Column(DateTime)
    label = Column(String(255))
    duration_ms = Column(Integer)
    
    # Metrics
    spotify_popularity = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="tracks")

class ContactAttempt(Base):
    """Contact discovery attempts"""
    __tablename__ = 'contact_attempts'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    contact_method = Column(String(50), nullable=False)  # 'email', 'social', 'website'
    contact_value = Column(String(255), nullable=False)
    source = Column(String(100))  # 'musicbrainz', 'spotify', 'scraped'
    confidence_score = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="contact_attempts")

class OutreachLog(Base):
    """Outreach activity log"""
    __tablename__ = 'outreach_logs'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    contact_date = Column(DateTime, nullable=False)
    method = Column(String(50))  # 'email', 'social', 'phone'
    notes = Column(Text)
    response_received = Column(Boolean, default=False)
    follow_up_scheduled = Column(DateTime)
    conversion_status = Column(String(50))  # 'interested', 'not_interested', 'converted', 'no_response'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="outreach_logs")

class DatabaseManager:
    """Enhanced database manager with PostgreSQL support and YouTube operations"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = None
        self.session = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection with proper configuration for both SQLite and PostgreSQL"""
        try:
            if self.database_url.startswith('postgresql'):
                # PostgreSQL configuration for Render
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    connect_args={
                        "sslmode": "require",
                        "connect_timeout": 30
                    }
                )
            else:
                # SQLite configuration for development
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    connect_args={'check_same_thread': False}
                )
            
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            print(f"✅ Database connection established")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(self.engine)
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            raise
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics including YouTube metrics"""
        try:
            # Basic artist counts
            total_artists = self.session.query(Artist).count()
            
            # Tier distribution
            tier_distribution = {}
            for tier in ['A', 'B', 'C', 'D']:
                count = self.session.query(Artist).filter(Artist.lead_tier == tier).count()
                tier_distribution[tier] = count
            
            # YouTube statistics
            artists_with_youtube = self.session.query(Artist).filter(
                Artist.youtube_channel_id.isnot(None)
            ).count()
            
            total_youtube_subscribers = self.session.query(
                Artist.youtube_subscribers
            ).filter(
                Artist.youtube_subscribers.isnot(None)
            ).all()
            
            total_subs = sum(row[0] or 0 for row in total_youtube_subscribers)
            avg_subs = total_subs / max(len(total_youtube_subscribers), 1)
            
            high_potential_channels = self.session.query(Artist).filter(
                Artist.youtube_growth_potential == 'high_potential'
            ).count()
            
            return {
                'total_artists': total_artists,
                'tier_distribution': tier_distribution,
                'youtube_statistics': {
                    'artists_with_youtube': artists_with_youtube,
                    'total_youtube_subscribers': total_subs,
                    'avg_youtube_subscribers': avg_subs,
                    'high_potential_channels': high_potential_channels,
                    'youtube_coverage_percentage': (artists_with_youtube / max(total_artists, 1)) * 100
                }
            }
            
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {'total_artists': 0, 'tier_distribution': {}, 'youtube_statistics': {}}
    
    def get_youtube_opportunities(self, limit=20):
        """Get artists with YouTube opportunities"""
        try:
            # Artists with no YouTube presence but significant Spotify following
            no_youtube_presence = self.session.query(Artist).filter(
                Artist.youtube_channel_id.is_(None),
                Artist.monthly_listeners > 5000
            ).order_by(Artist.monthly_listeners.desc()).limit(limit).all()
            
            # Artists with underperforming YouTube channels
            underperforming_youtube = self.session.query(Artist).filter(
                Artist.youtube_channel_id.isnot(None),
                Artist.monthly_listeners > 10000,
                Artist.youtube_subscribers < Artist.monthly_listeners * 0.3
            ).order_by(Artist.monthly_listeners.desc()).limit(limit).all()
            
            return {
                'no_youtube_presence': [{
                    'id': artist.id,
                    'name': artist.name,
                    'country': artist.country,
                    'monthly_listeners': artist.monthly_listeners,
                    'total_score': artist.total_score,
                    'lead_tier': artist.lead_tier
                } for artist in no_youtube_presence],
                'underperforming_youtube': [{
                    'id': artist.id,
                    'name': artist.name,
                    'country': artist.country,
                    'monthly_listeners': artist.monthly_listeners,
                    'youtube_subscribers': artist.youtube_subscribers,
                    'youtube_channel_url': artist.youtube_channel_url,
                    'total_score': artist.total_score,
                    'lead_tier': artist.lead_tier
                } for artist in underperforming_youtube]
            }
            
        except Exception as e:
            print(f"Error getting YouTube opportunities: {e}")
            return {'no_youtube_presence': [], 'underperforming_youtube': []}
    
    def update_youtube_data(self, artist_id, youtube_data):
        """Update YouTube data for an artist"""
        try:
            artist = self.session.query(Artist).filter_by(id=artist_id).first()
            if not artist:
                return False
            
            # Update YouTube fields
            for field, value in youtube_data.items():
                if hasattr(artist, f'youtube_{field}'):
                    setattr(artist, f'youtube_{field}', value)
            
            artist.updated_at = datetime.utcnow()
            self.session.commit()
            return True
            
        except Exception as e:
            print(f"Error updating YouTube data: {e}")
            self.session.rollback()
            return False
    
    def save_artist_data(self, artist_data):
        """Save or update artist data including YouTube metrics"""
        try:
            # Check if artist already exists
            existing_artist = None
            if artist_data.get('musicbrainz_id'):
                existing_artist = self.session.query(Artist).filter_by(
                    musicbrainz_id=artist_data['musicbrainz_id']
                ).first()
            
            if not existing_artist and artist_data.get('spotify_id'):
                existing_artist = self.session.query(Artist).filter_by(
                    spotify_id=artist_data['spotify_id']
                ).first()
            
            if not existing_artist:
                existing_artist = self.session.query(Artist).filter_by(
                    name=artist_data['name']
                ).first()
            
            if existing_artist:
                # Update existing artist
                for key, value in artist_data.items():
                    if hasattr(existing_artist, key) and value is not None:
                        setattr(existing_artist, key, value)
                existing_artist.updated_at = datetime.utcnow()
                self.session.commit()
                return existing_artist.id
            else:
                # Create new artist
                artist = Artist(**{k: v for k, v in artist_data.items() if hasattr(Artist, k)})
                self.session.add(artist)
                self.session.commit()
                return artist.id
                
        except Exception as e:
            print(f"Error saving artist data: {e}")
            self.session.rollback()
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        self.session.close()

def init_db():
    """Initialize database with tables"""
    try:
        db_manager = DatabaseManager()
        db_manager.create_tables()
        print("✅ Database initialization completed")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def run_youtube_migration_if_needed():
    """Add YouTube columns if they don't exist (for upgrading existing databases)"""
    try:
        db_manager = DatabaseManager()
        
        # Check if YouTube columns exist
        inspector = db_manager.engine.dialect.get_inspector(db_manager.engine)
        columns = [col['name'] for col in inspector.get_columns('artists')]
        
        youtube_columns = [
            'youtube_channel_id', 'youtube_channel_url', 'youtube_subscribers',
            'youtube_total_views', 'youtube_video_count', 'youtube_upload_frequency',
            'youtube_engagement_rate', 'youtube_growth_potential', 'youtube_last_upload'
        ]
        
        missing_columns = [col for col in youtube_columns if col not in columns]
        
        if missing_columns:
            print(f"🔄 Adding YouTube integration columns: {missing_columns}")
            
            # Add columns using raw SQL (SQLAlchemy doesn't have great column addition support)
            for column in missing_columns:
                if 'subscribers' in column or 'views' in column or 'count' in column:
                    sql = f"ALTER TABLE artists ADD COLUMN {column} INTEGER DEFAULT 0"
                elif 'rate' in column:
                    sql = f"ALTER TABLE artists ADD COLUMN {column} REAL DEFAULT 0.0"
                elif 'upload' in column and 'last' in column:
                    sql = f"ALTER TABLE artists ADD COLUMN {column} TIMESTAMP"
                else:
                    sql = f"ALTER TABLE artists ADD COLUMN {column} VARCHAR(255)"
                
                try:
                    db_manager.session.execute(sql)
                    db_manager.session.commit()
                    print(f"✅ Added column: {column}")
                except Exception as e:
                    print(f"⚠️  Column {column} might already exist: {e}")
                    db_manager.session.rollback()
        else:
            print("✅ YouTube integration columns already exist")
            
    except Exception as e:
        print(f"⚠️  YouTube migration check failed: {e}")

def get_db():
    """Get database session for dependency injection"""
    db_manager = DatabaseManager()
    try:
        yield db_manager.session
    finally:
        db_manager.session.close()

# Create global database manager instance
_db_manager = None

def get_db_manager():
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager