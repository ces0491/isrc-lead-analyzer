def validate_isrc(isrc_string):
    """Properly validate ISRC format"""
    if not isrc_string:
        return False, "ISRC is required"
    
    # Remove common separators
    cleaned = isrc_string.replace('-', '').replace(' ', '').upper()
    
    # Check length and format
    if len(cleaned) != 12:
        return False, "ISRC must be 12 characters long"
    
    if not cleaned.isalnum():
        return False, "ISRC must contain only letters and numbers"
    
    # Check basic structure
    if not cleaned[:2].isalpha():
        return False, "First two characters must be country code (letters)"
    
    if not cleaned[2:5].isalnum():
        return False, "Characters 3-5 must be registrant code"
    
    if not cleaned[5:7].isdigit():
        return False, "Characters 6-7 must be year digits"
    
    if not cleaned[7:].isalnum():
        return False, "Last 5 characters must be designation code"
    
    return True, cleaned