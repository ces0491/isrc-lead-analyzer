"""
Contact Discovery Service with YouTube Integration
Finds contact information for artists from various sources including YouTube channels
"""
import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from src.core.rate_limiter import rate_limiter
import time

class ContactDiscoveryService:
    """
    Service for discovering artist contact information with YouTube integration
    Uses multiple strategies to find emails, social media, and other contact methods
    """
    
    def __init__(self):
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b[A-Za-z0-9._%+-]+\s*\[?at\]?\s*[A-Za-z0-9.-]+\s*\[?dot\]?\s*[A-Z|a-z]{2,}\b'
        ]
        
        self.social_platforms = {
            'instagram': r'(?:instagram\.com/|@)([a-zA-Z0-9_.]+)',
            'twitter': r'(?:twitter\.com/|@)([a-zA-Z0-9_]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
            'youtube': r'youtube\.com/(?:c/|channel/|user/|@)([a-zA-Z0-9_.-]+)',
            'soundcloud': r'soundcloud\.com/([a-zA-Z0-9_-]+)',
            'bandcamp': r'([a-zA-Z0-9_-]+)\.bandcamp\.com',
            'tiktok': r'tiktok\.com/@([a-zA-Z0-9_.]+)'
        }
        
        # YouTube-specific patterns
        self.youtube_patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_.-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)'  # Short URLs
        ]
        
        # Common non-contact emails to filter out
        self.email_blacklist = [
            'noreply', 'donotreply', 'no-reply', 'marketing', 'spam',
            'admin', 'webmaster', 'postmaster', 'mailer-daemon',
            'newsletter', 'notifications', 'support'
        ]
        
        # Common contact keywords that indicate good emails
        self.contact_keywords = [
            'contact', 'booking', 'management', 'info', 'hello',
            'music', 'band', 'artist', 'manager', 'agent'
        ]
    
    def discover_contacts(self, artist_data: Dict) -> List[Dict]:
        """
        Main contact discovery function with YouTube integration
        Returns list of contact methods with confidence scores
        """
        contacts = []
        
        # 1. Extract from known URLs/profiles
        contacts.extend(self._extract_from_profiles(artist_data))
        
        # 2. NEW: Extract YouTube channel information
        contacts.extend(self._extract_youtube_contacts(artist_data))
        
        # 3. NEW: Search for YouTube links in bios and descriptions
        contacts.extend(self._search_youtube_in_descriptions(artist_data))
        
        # 4. Scrape artist website if available
        if artist_data.get('website'):
            website_contacts = self._scrape_website(artist_data['website'])
            contacts.extend(website_contacts)
        
        # 5. Search social media bios
        social_contacts = self._search_social_bios(artist_data)
        contacts.extend(social_contacts)
        
        # 6. Search streaming platform descriptions
        platform_contacts = self._search_platform_descriptions(artist_data)
        contacts.extend(platform_contacts)
        
        # 7. Generate potential emails based on artist name/website
        generated_contacts = self._generate_potential_emails(artist_data)
        contacts.extend(generated_contacts)
        
        # Clean and deduplicate
        cleaned_contacts = self._clean_and_deduplicate(contacts)
        
        # Sort by confidence score
        cleaned_contacts.sort(key=lambda x: x['confidence'], reverse=True)
        
        return cleaned_contacts[:15]  # Return top 15 contacts (increased for YouTube)
    
    def _extract_from_profiles(self, artist_data: Dict) -> List[Dict]:
        """Extract contacts from known profiles and URLs"""
        contacts = []
        
        # From MusicBrainz URLs
        mb_urls = artist_data.get('musicbrainz_data', {}).get('artist', {}).get('urls', {})
        for platform, url in mb_urls.items():
            if platform == 'website':
                contacts.append({
                    'type': 'website',
                    'value': url,
                    'source': 'musicbrainz',
                    'confidence': 85,
                    'platform': 'website'
                })
            elif platform in self.social_platforms:
                contacts.append({
                    'type': 'social',
                    'value': url,
                    'source': 'musicbrainz',
                    'confidence': 90,
                    'platform': platform
                })
        
        # From Spotify external URLs
        spotify_urls = artist_data.get('spotify_data', {}).get('external_urls', {})
        if spotify_urls.get('spotify'):
            contacts.append({
                'type': 'platform_profile',
                'value': spotify_urls['spotify'],
                'source': 'spotify_api',
                'confidence': 95,
                'platform': 'spotify'
            })
        
        return contacts
    
    def _extract_youtube_contacts(self, artist_data: Dict) -> List[Dict]:
        """NEW: Extract YouTube channel as contact method"""
        contacts = []
        
        youtube_data = artist_data.get('youtube_data', {})
        if not youtube_data:
            return contacts
        
        channel_data = youtube_data.get('channel', {})
        if not channel_data:
            return contacts
        
        channel_id = channel_data.get('channel_id')
        if channel_id:
            channel_url = f"https://youtube.com/channel/{channel_id}"
            
            # Extract additional details
            subscriber_count = channel_data.get('statistics', {}).get('subscriber_count', 0)
            channel_title = channel_data.get('title', '')
            published_at = channel_data.get('published_at', '')
            
            # Check if channel title matches artist name for confidence scoring
            artist_name = artist_data.get('name', '').lower()
            title_match = artist_name in channel_title.lower() if artist_name else False
            
            # Calculate confidence based on various factors
            confidence = 95 if title_match else 80
            
            # Boost confidence for channels with good subscriber count
            if subscriber_count and int(subscriber_count) > 1000:
                confidence += 5
            
            # Boost confidence for older, established channels
            if published_at:
                try:
                    from datetime import datetime
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    years_old = (datetime.now().replace(tzinfo=pub_date.tzinfo) - pub_date).days / 365
                    if years_old > 2:
                        confidence += 3
                except:
                    pass
            
            contacts.append({
                'type': 'platform_profile',
                'platform': 'youtube',
                'value': channel_url,
                'source': 'youtube_api',
                'confidence': min(confidence, 95),
                'metadata': {
                    'channel_title': channel_title,
                    'subscriber_count': subscriber_count,
                    'channel_id': channel_id,
                    'published_at': published_at
                }
            })
            
            # Also add YouTube handle if different from URL and title matches
            if channel_title and title_match:
                # Create a handle-style contact
                handle = channel_title.replace(' ', '').replace('-', '').replace('_', '')
                contacts.append({
                    'type': 'social',
                    'platform': 'youtube',
                    'value': f"@{handle}",
                    'source': 'youtube_api',
                    'confidence': 85,
                    'metadata': {
                        'handle_type': 'youtube_channel_name',
                        'original_title': channel_title
                    }
                })
        
        # Extract from video data if available
        videos = youtube_data.get('videos', [])
        if videos:
            # Look for contact info in video descriptions
            for video in videos[:3]:  # Check top 3 videos
                description = video.get('description', '')
                if description:
                    video_contacts = self._extract_contacts_from_text(
                        description, 
                        source='youtube_video_description',
                        confidence_modifier=-10  # Slightly lower confidence
                    )
                    contacts.extend(video_contacts)
        
        return contacts
    
    def _search_youtube_in_descriptions(self, artist_data: Dict) -> List[Dict]:
        """NEW: Search for YouTube links in artist descriptions and bios"""
        contacts = []
        
        # Search in Spotify artist bio (if available in extended data)
        spotify_data = artist_data.get('spotify_data', {})
        if 'bio' in spotify_data:
            youtube_links = self._extract_youtube_links_from_text(spotify_data['bio'])
            for link in youtube_links:
                link['source'] = 'spotify_bio'
                contacts.append(link)
        
        # Search in Last.fm bio
        lastfm_data = artist_data.get('lastfm_data', {})
        if 'artist' in lastfm_data and 'bio' in lastfm_data['artist']:
            youtube_links = self._extract_youtube_links_from_text(lastfm_data['artist']['bio'])
            for link in youtube_links:
                link['source'] = 'lastfm_bio'
                contacts.append(link)
        
        # Search in MusicBrainz annotation/disambiguation
        mb_data = artist_data.get('musicbrainz_data', {})
        if 'artist' in mb_data:
            artist_info = mb_data['artist']
            for field in ['annotation', 'disambiguation', 'comment']:
                if field in artist_info:
                    youtube_links = self._extract_youtube_links_from_text(artist_info[field])
                    for link in youtube_links:
                        link['source'] = f'musicbrainz_{field}'
                        contacts.append(link)
        
        return contacts
    
    def _extract_youtube_links_from_text(self, text: str) -> List[Dict]:
        """NEW: Extract YouTube links from bio text"""
        if not text:
            return []
        
        contacts = []
        
        for pattern in self.youtube_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Reconstruct full URL based on pattern type
                if 'channel/' in pattern:
                    full_url = f"https://youtube.com/channel/{match}"
                    contact_type = 'channel'
                elif '/c/' in pattern:
                    full_url = f"https://youtube.com/c/{match}"
                    contact_type = 'custom_url'
                elif '/user/' in pattern:
                    full_url = f"https://youtube.com/user/{match}"
                    contact_type = 'user'
                elif '/@' in pattern:
                    full_url = f"https://youtube.com/@{match}"
                    contact_type = 'handle'
                else:  # youtu.be short links
                    full_url = f"https://youtu.be/{match}"
                    contact_type = 'video'
                
                contacts.append({
                    'type': 'platform_profile',
                    'platform': 'youtube',
                    'value': full_url,
                    'source': 'bio_text_extraction',
                    'confidence': 75,
                    'metadata': {
                        'extraction_method': 'regex_pattern_matching',
                        'youtube_type': contact_type,
                        'extracted_id': match
                    }
                })
        
        return contacts
    
    def _extract_contacts_from_text(self, text: str, source: str, confidence_modifier: int = 0) -> List[Dict]:
        """Extract all types of contacts (emails, social, etc.) from text"""
        contacts = []
        
        if not text:
            return contacts
        
        # Extract emails
        emails = self._extract_emails(text)
        for email in emails:
            confidence = self._calculate_email_confidence(email, '', is_contact_page=False)
            contacts.append({
                'type': 'email',
                'value': email,
                'source': source,
                'confidence': max(10, confidence + confidence_modifier),
                'platform': 'email'
            })
        
        # Extract social media links
        for platform, pattern in self.social_platforms.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                contacts.append({
                    'type': 'social',
                    'platform': platform,
                    'value': match if platform == 'bandcamp' else f"@{match}",
                    'source': source,
                    'confidence': max(10, 70 + confidence_modifier)
                })
        
        return contacts
    
    def _scrape_website(self, website_url: str) -> List[Dict]:
        """Scrape artist website for contact information including YouTube links"""
        contacts = []
        
        try:
            # Add rate limiting for web scraping
            time.sleep(2)  # Be respectful to websites
            
            headers = {
                'User-Agent': 'PreciseDigitalLeadGen/1.0 (contact@precise.digital)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(website_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract emails from page text
            page_text = soup.get_text()
            emails = self._extract_emails(page_text)
            
            for email in emails:
                confidence = self._calculate_email_confidence(email, website_url)
                contacts.append({
                    'type': 'email',
                    'value': email,
                    'source': f'website_scrape_{urlparse(website_url).netloc}',
                    'confidence': confidence,
                    'platform': 'email'
                })
            
            # Look for contact page links
            contact_links = self._find_contact_page_links(soup, website_url)
            for link in contact_links:
                try:
                    contact_page_contacts = self._scrape_contact_page(link)
                    contacts.extend(contact_page_contacts)
                except Exception:
                    continue  # Skip failed contact page scrapes
            
            # Extract social media links including YouTube
            social_links = self._extract_social_links(soup)
            for platform, handle in social_links.items():
                contacts.append({
                    'type': 'social' if platform != 'youtube' else 'platform_profile',
                    'value': handle,
                    'source': f'website_scrape_{urlparse(website_url).netloc}',
                    'confidence': 85 if platform == 'youtube' else 80,
                    'platform': platform
                })
        
        except Exception as e:
            print(f"Website scraping failed for {website_url}: {str(e)}")
        
        return contacts
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links including YouTube from HTML"""
        social_links = {}
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Check regular social platforms
            for platform, pattern in self.social_platforms.items():
                match = re.search(pattern, href, re.IGNORECASE)
                if match:
                    if platform == 'bandcamp':
                        social_links[platform] = href  # Full URL for Bandcamp
                    elif platform == 'youtube':
                        social_links[platform] = href  # Full URL for YouTube
                    else:
                        social_links[platform] = match.group(1)  # Extract handle
                    break
            
            # Additional YouTube pattern checking
            if 'youtube' not in social_links:
                for pattern in self.youtube_patterns:
                    match = re.search(pattern, href, re.IGNORECASE)
                    if match:
                        social_links['youtube'] = href
                        break
        
        return social_links
    
    def _find_contact_page_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find links to contact pages"""
        contact_keywords = ['contact', 'booking', 'management', 'about', 'info']
        contact_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            link_text = link.get_text().lower()
            
            # Check if link points to contact page
            if any(keyword in href or keyword in link_text for keyword in contact_keywords):
                full_url = urljoin(base_url, link['href'])
                contact_links.append(full_url)
        
        return contact_links[:3]  # Limit to 3 contact pages
    
    def _scrape_contact_page(self, contact_url: str) -> List[Dict]:
        """Scrape specific contact page for information"""
        contacts = []
        
        try:
            time.sleep(1)  # Rate limiting
            
            headers = {
                'User-Agent': 'PreciseDigitalLeadGen/1.0 (contact@precise.digital)'
            }
            
            response = requests.get(contact_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract emails
            emails = self._extract_emails(page_text)
            for email in emails:
                confidence = self._calculate_email_confidence(email, contact_url, is_contact_page=True)
                contacts.append({
                    'type': 'email',
                    'value': email,
                    'source': f'contact_page_{urlparse(contact_url).netloc}',
                    'confidence': confidence,
                    'platform': 'email'
                })
            
            # Extract YouTube links from contact page
            youtube_links = self._extract_youtube_links_from_text(page_text)
            for link in youtube_links:
                link['source'] = f'contact_page_{urlparse(contact_url).netloc}'
                link['confidence'] += 10  # Boost confidence for contact page finds
                contacts.append(link)
        
        except Exception as e:
            print(f"Contact page scraping failed for {contact_url}: {str(e)}")
        
        return contacts
    
    def _search_social_bios(self, artist_data: Dict) -> List[Dict]:
        """Search social media bios for contact information"""
        contacts = []
        
        # This would require API access to social platforms
        # For now, return empty list - can be expanded with actual API integration
        
        return contacts
    
    def _search_platform_descriptions(self, artist_data: Dict) -> List[Dict]:
        """Search streaming platform descriptions for contact info"""
        contacts = []
        
        # This would require additional API calls to get artist descriptions
        # For now, return empty list - can be expanded with actual implementation
        
        return contacts
    
    def _generate_potential_emails(self, artist_data: Dict) -> List[Dict]:
        """Generate potential email addresses based on artist name and website"""
        contacts = []
        
        artist_name = artist_data.get('name', '').lower()
        website = artist_data.get('website', '')
        
        if not artist_name or not website:
            return contacts
        
        # Extract domain from website
        try:
            domain = urlparse(website).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
        except:
            return contacts
        
        # Generate common email patterns
        name_parts = artist_name.replace(' ', '').replace('-', '').replace('_', '')
        name_with_dots = artist_name.replace(' ', '.').replace('-', '.').replace('_', '.')
        
        email_patterns = [
            f"contact@{domain}",
            f"info@{domain}",
            f"booking@{domain}",
            f"management@{domain}",
            f"{name_parts}@{domain}",
            f"{name_with_dots}@{domain}",
            f"hello@{domain}",
            f"music@{domain}"
        ]
        
        for email in email_patterns:
            if self._is_valid_email(email):
                contacts.append({
                    'type': 'email',
                    'value': email,
                    'source': 'generated_pattern',
                    'confidence': 30,  # Low confidence for generated emails
                    'platform': 'email',
                    'note': 'Generated based on artist name and website'
                })
        
        return contacts
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        emails = []
        
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emails.extend(matches)
        
        # Clean up extracted emails
        cleaned_emails = []
        for email in emails:
            # Handle obfuscated emails (e.g., "email at domain dot com")
            cleaned = email.replace(' at ', '@').replace(' dot ', '.').replace('[at]', '@').replace('[dot]', '.')
            cleaned = re.sub(r'\s+', '', cleaned)  # Remove extra spaces
            
            if self._is_valid_email(cleaned):
                cleaned_emails.append(cleaned.lower())
        
        return list(set(cleaned_emails))  # Remove duplicates
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _calculate_email_confidence(self, email: str, source_url: str, is_contact_page: bool = False) -> int:
        """Calculate confidence score for an email address"""
        confidence = 50  # Base confidence
        
        email_lower = email.lower()
        
        # Reduce confidence for blacklisted terms
        if any(term in email_lower for term in self.email_blacklist):
            confidence -= 30
        
        # Increase confidence for contact-related terms
        if any(term in email_lower for term in self.contact_keywords):
            confidence += 20
        
        # Increase confidence if found on contact page
        if is_contact_page:
            confidence += 15
        
        # Increase confidence if email domain matches website domain
        try:
            email_domain = email_lower.split('@')[1]
            if source_url:
                source_domain = urlparse(source_url).netloc.lower()
                if source_domain.endswith(email_domain) or email_domain in source_domain:
                    confidence += 25
        except:
            pass
        
        # Ensure confidence is within bounds
        return max(10, min(95, confidence))
    
    def _clean_and_deduplicate(self, contacts: List[Dict]) -> List[Dict]:
        """Clean and remove duplicate contacts"""
        seen = set()
        cleaned = []
        
        for contact in contacts:
            # Create unique key for deduplication
            key = f"{contact['type']}:{contact['platform']}:{contact['value'].lower()}"
            
            if key not in seen:
                seen.add(key)
                
                # Additional cleaning
                if contact['type'] == 'email':
                    contact['value'] = contact['value'].lower().strip()
                elif contact['type'] == 'social':
                    contact['value'] = contact['value'].strip()
                elif contact['type'] == 'platform_profile':
                    contact['value'] = contact['value'].strip()
                
                # Only include contacts with reasonable confidence
                if contact['confidence'] >= 20:
                    cleaned.append(contact)
        
        return cleaned

# Utility functions for testing YouTube integration
def test_youtube_contact_discovery():
    """Test YouTube contact discovery specifically"""
    service = ContactDiscoveryService()
    
    # Test data with YouTube integration
    test_artist_data = {
        'name': 'Test Artist',
        'website': 'https://testartist.com',
        'musicbrainz_data': {
            'artist': {
                'urls': {
                    'website': 'https://testartist.com',
                    'twitter': 'https://twitter.com/testartist',
                    'instagram': 'https://instagram.com/testartist'
                }
            }
        },
        'spotify_data': {
            'external_urls': {
                'spotify': 'https://open.spotify.com/artist/testid'
            },
            'bio': 'Check out our YouTube channel: https://youtube.com/@testartist'
        },
        'youtube_data': {
            'channel': {
                'channel_id': 'UC1234567890123456789',
                'title': 'Test Artist Official',
                'statistics': {
                    'subscriber_count': 15000,
                    'view_count': 500000,
                    'video_count': 25
                },
                'published_at': '2020-01-15T00:00:00Z'
            },
            'analytics': {
                'recent_activity': {
                    'upload_frequency': 'active',
                    'videos_last_30_days': 3
                },
                'growth_potential': 'high_potential'
            },
            'videos': [
                {
                    'title': 'Latest Song - Official Music Video',
                    'description': 'For bookings contact: booking@testartist.com\\nFollow us on Instagram @testartist'
                }
            ]
        }
    }
    
    contacts = service.discover_contacts(test_artist_data)
    
    print("YouTube Contact Discovery Test Results:")
    print("=" * 50)
    for i, contact in enumerate(contacts, 1):
        print(f"{i}. {contact['type'].upper()}: {contact['value']}")
        print(f"   Platform: {contact.get('platform', 'N/A')}")
        print(f"   Source: {contact['source']}")
        print(f"   Confidence: {contact['confidence']}%")
        if contact.get('metadata'):
            print(f"   Metadata: {contact['metadata']}")
        if contact.get('note'):
            print(f"   Note: {contact['note']}")
        print()

def test_youtube_link_extraction():
    """Test YouTube link extraction from various text formats"""
    service = ContactDiscoveryService()
    
    test_texts = [
        "Check out our music videos on YouTube: https://youtube.com/channel/UC1234567890123456789",
        "Subscribe to youtube.com/c/testartist for new releases!",
        "Follow us: YouTube: youtube.com/@testartist, Instagram: @testartist",
        "Watch our latest video: youtu.be/dQw4w9WgXcQ",
        "Visit our YouTube page youtube.com/user/testartistofficial for more content"
    ]
    
    print("YouTube Link Extraction Test:")
    print("=" * 40)
    
    for i, text in enumerate(test_texts, 1):
        links = service._extract_youtube_links_from_text(text)
        print(f"{i}. Text: {text}")
        print(f"   Extracted: {[link['value'] for link in links]}")
        if links:
            print(f"   Types: {[link['metadata']['youtube_type'] for link in links]}")
        print()

if __name__ == "__main__":
    test_youtube_contact_discovery()
    print("\n" + "="*60 + "\n")
    test_youtube_link_extraction()