"""
Validation utilities for Precise Digital Lead Generation Tool
Validates ISRCs, email addresses, and other input formats
"""
import re
from typing import Tuple

def validate_isrc(isrc_string) -> Tuple[bool, str]:
    """
    Properly validate ISRC format and return cleaned version
    
    Args:
        isrc_string: The ISRC string to validate
        
    Returns:
        Tuple of (is_valid, cleaned_isrc_or_error_message)
    """
    if not isrc_string:
        return False, "ISRC is required"
    
    # Convert to string and strip whitespace
    isrc_str = str(isrc_string).strip()
    if not isrc_str:
        return False, "ISRC cannot be empty"
    
    # Remove common separators and convert to uppercase
    cleaned = isrc_str.replace('-', '').replace(' ', '').replace('_', '').upper()
    
    # Check length
    if len(cleaned) != 12:
        return False, f"ISRC must be 12 characters long, got {len(cleaned)}"
    
    # Check that it contains only letters and numbers
    if not cleaned.isalnum():
        return False, "ISRC must contain only letters and numbers"
    
    # Check basic structure: CC-XXX-YY-NNNNN
    # CC = Country code (2 letters)
    # XXX = Registrant code (3 alphanumeric)
    # YY = Year (2 digits)
    # NNNNN = Designation code (5 alphanumeric)
    
    country_code = cleaned[:2]
    registrant_code = cleaned[2:5]
    year_code = cleaned[5:7]
    designation_code = cleaned[7:12]
    
    # Validate country code (first 2 characters must be letters)
    if not country_code.isalpha():
        return False, "First two characters must be country code (letters only)"
    
    # Validate registrant code (3 alphanumeric characters)
    if not registrant_code.isalnum():
        return False, "Characters 3-5 must be registrant code (alphanumeric)"
    
    # Validate year (2 digits)
    if not year_code.isdigit():
        return False, "Characters 6-7 must be year (digits only)"
    
    # Validate year range (reasonable years)
    try:
        year = int(year_code)
        if year < 0 or year > 99:  # 2-digit year representation
            return False, f"Invalid year: {year_code}"
    except ValueError:
        return False, f"Invalid year format: {year_code}"
    
    # Validate designation code (5 alphanumeric characters)
    if not designation_code.isalnum():
        return False, "Last 5 characters must be designation code (alphanumeric)"
    
    return True, cleaned

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, cleaned_email_or_error_message)
    """
    if not email:
        return False, "Email is required"
    
    email = str(email).strip().lower()
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, email
    else:
        return False, "Invalid email format"

def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, cleaned_url_or_error_message)
    """
    if not url:
        return False, "URL is required"
    
    url = str(url).strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Basic URL pattern
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    
    if re.match(pattern, url):
        return True, url
    else:
        return False, "Invalid URL format"

def validate_spotify_id(spotify_id: str) -> Tuple[bool, str]:
    """
    Validate Spotify ID format
    
    Args:
        spotify_id: Spotify ID to validate
        
    Returns:
        Tuple of (is_valid, cleaned_id_or_error_message)
    """
    if not spotify_id:
        return False, "Spotify ID is required"
    
    spotify_id = str(spotify_id).strip()
    
    # Spotify IDs are 22 characters, base62 encoded
    if len(spotify_id) != 22:
        return False, f"Spotify ID must be 22 characters long, got {len(spotify_id)}"
    
    # Check if it contains only valid base62 characters
    valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    if not all(c in valid_chars for c in spotify_id):
        return False, "Spotify ID contains invalid characters"
    
    return True, spotify_id

def validate_musicbrainz_id(mb_id: str) -> Tuple[bool, str]:
    """
    Validate MusicBrainz ID format (UUID)
    
    Args:
        mb_id: MusicBrainz ID to validate
        
    Returns:
        Tuple of (is_valid, cleaned_id_or_error_message)
    """
    if not mb_id:
        return False, "MusicBrainz ID is required"
    
    mb_id = str(mb_id).strip().lower()
    
    # UUID pattern: 8-4-4-4-12 hexadecimal digits
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    
    if re.match(pattern, mb_id):
        return True, mb_id
    else:
        return False, "Invalid MusicBrainz ID format (must be UUID)"

def validate_country_code(country_code: str) -> Tuple[bool, str]:
    """
    Validate ISO country code
    
    Args:
        country_code: Country code to validate
        
    Returns:
        Tuple of (is_valid, cleaned_code_or_error_message)
    """
    if not country_code:
        return False, "Country code is required"
    
    country_code = str(country_code).strip().upper()
    
    # List of common ISO 3166-1 alpha-2 country codes
    valid_codes = {
        'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT',
        'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI',
        'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY',
        'BZ', 'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN',
        'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM',
        'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK',
        'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL',
        'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM',
        'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR',
        'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN',
        'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS',
        'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK',
        'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW',
        'MX', 'MY', 'MZ', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP',
        'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM',
        'PN', 'PR', 'PS', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW',
        'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM',
        'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF',
        'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW',
        'TZ', 'UA', 'UG', 'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI',
        'VN', 'VU', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM', 'ZW'
    }
    
    if len(country_code) != 2:
        return False, "Country code must be 2 characters"
    
    if country_code in valid_codes:
        return True, country_code
    else:
        return False, f"Invalid country code: {country_code}"

# Batch validation functions
def validate_isrc_batch(isrcs: list) -> Tuple[list, list]:
    """
    Validate a batch of ISRCs
    
    Args:
        isrcs: List of ISRC strings to validate
        
    Returns:
        Tuple of (valid_isrcs, invalid_isrcs_with_errors)
    """
    valid_isrcs = []
    invalid_isrcs = []
    
    for isrc in isrcs:
        is_valid, result = validate_isrc(isrc)
        if is_valid:
            valid_isrcs.append(result)
        else:
            invalid_isrcs.append({'isrc': isrc, 'error': result})
    
    return valid_isrcs, invalid_isrcs

# Test function
def test_validators():
    """Test all validation functions"""
    print("Testing validators...")
    
    # Test ISRC validation
    test_isrcs = [
        "USRC17607839",     # Valid
        "GBUM71505078",     # Valid
        "us-rc-17-607839",  # Valid (should be cleaned)
        "INVALID",          # Invalid
        "USRC1760783",      # Too short
        "USRC17607839X",    # Too long
    ]
    
    for isrc in test_isrcs:
        is_valid, result = validate_isrc(isrc)
        status = "✅" if is_valid else "❌"
        print(f"  {status} ISRC '{isrc}': {result}")
    
    # Test email validation
    test_emails = [
        "test@example.com",         # Valid
        "user.name+tag@domain.co.uk",  # Valid
        "invalid.email",            # Invalid
        "@domain.com",              # Invalid
    ]
    
    for email in test_emails:
        is_valid, result = validate_email(email)
        status = "✅" if is_valid else "❌"
        print(f"  {status} Email '{email}': {result}")

if __name__ == "__main__":
    test_validators()