"""
Contact Discovery Service
Finds contact information for artists from various sources
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
    Service for discovering artist contact information
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
            'youtube': r'youtube\.com/(?:c/|channel/|user/)([a-zA-Z0-9_-]+)',
            'soundcloud': r'soundcloud\.com/([a-zA-Z0-9_-]+)',
            'bandcamp': r'([a-zA-Z0-9_-]+)\.bandcamp\.com',
            'tiktok': r'tiktok\.com/@([a-zA-Z0-9_.]+)'
        }
        
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
        Main contact discovery function
        Returns list of contact methods with confidence scores
        """
        contacts = []
        
        # 1. Extract from known URLs/profiles
        contacts.extend(self._extract_from_profiles(artist_data))
        
        # 2. Scrape artist website if available
        if artist_data.get('website'):
            website_contacts = self._scrape_website(artist_data['website'])
            contacts.extend(website_contacts)
        
        # 3. Search social media bios
        social_contacts = self._search_social_bios(artist_data)
        contacts.extend(social_contacts)
        
        # 4. Search streaming platform descriptions
        platform_contacts = self._search_platform_descriptions(artist_data)
        contacts.extend(platform_contacts)
        
        # 5. Generate potential emails based on artist name/website
        generated_contacts = self._generate_potential_emails(artist_data)
        contacts.extend(generated_contacts)
        
        # Clean and deduplicate
        cleaned_contacts = self._clean_and_deduplicate(contacts)
        
        # Sort by confidence score
        cleaned_contacts.sort(key=lambda x: x['confidence'], reverse=True)
        
        return cleaned_contacts[:10]  # Return top 10 contacts
    
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
    
    def _scrape_website(self, website_url: str) -> List[Dict]:
        """Scrape artist website for contact information"""
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
            
            # Extract social media links
            social_links = self._extract_social_links(soup)
            for platform, handle in social_links.items():
                contacts.append({
                    'type': 'social',
                    'value': handle,
                    'source': f'website_scrape_{urlparse(website_url).netloc}',
                    'confidence': 80,
                    'platform': platform
                })
        
        except Exception as e:
            print(f"Website scraping failed for {website_url}: {str(e)}")
        
        return contacts
    
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
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links from HTML"""
        social_links = {}
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            for platform, pattern in self.social_platforms.items():
                match = re.search(pattern, href, re.IGNORECASE)
                if match:
                    if platform == 'bandcamp':
                        social_links[platform] = href  # Full URL for Bandcamp
                    else:
                        social_links[platform] = match.group(1)  # Extract handle
                    break
        
        return social_links
    
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
            key = f"{contact['type']}:{contact['value'].lower()}"
            
            if key not in seen:
                seen.add(key)
                
                # Additional cleaning
                if contact['type'] == 'email':
                    contact['value'] = contact['value'].lower().strip()
                elif contact['type'] == 'social':
                    contact['value'] = contact['value'].strip()
                
                # Only include contacts with reasonable confidence
                if contact['confidence'] >= 20:
                    cleaned.append(contact)
        
        return cleaned

# Utility functions
def test_contact_discovery():
    """Test the contact discovery service"""
    service = ContactDiscoveryService()
    
    # Test data
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
            }
        }
    }
    
    contacts = service.discover_contacts(test_artist_data)
    
    print("Contact Discovery Test Results:")
    print("=" * 40)
    for i, contact in enumerate(contacts, 1):
        print(f"{i}. {contact['type'].upper()}: {contact['value']}")
        print(f"   Platform: {contact['platform']}")
        print(f"   Source: {contact['source']}")
        print(f"   Confidence: {contact['confidence']}%")
        if contact.get('note'):
            print(f"   Note: {contact['note']}")
        print()

def validate_email_extraction():
    """Test email extraction functionality"""
    service = ContactDiscoveryService()
    
    test_texts = [
        "Contact us at booking@example.com for shows",
        "Email: hello at example dot com",
        "Reach out to management[at]musiclabel[dot]co[dot]uk",
        "For bookings: noreply@spam.com (this should be filtered)",
        "Business inquiries: contact@artist-website.com"
    ]
    
    for text in test_texts:
        emails = service._extract_emails(text)
        print(f"Text: {text}")
        print(f"Extracted: {emails}")
        print()

if __name__ == "__main__":
    # test_contact_discovery()
    validate_email_extraction()