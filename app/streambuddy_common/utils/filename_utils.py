import re
import unicodedata

def sanitize_filename(title):
    """
    Convert a string into a safe filename.
    - Replace spaces with underscores
    - Remove special characters
    - Convert to lowercase
    - Limit length
    """
    # Convert to lowercase and replace spaces
    filename = title.lower().replace(' ', '_')
    
    # Remove accents
    filename = unicodedata.normalize('NFKD', filename)
    filename = ''.join(c for c in filename if not unicodedata.combining(c))
    
    # Remove special characters
    filename = re.sub(r'[^a-z0-9_-]', '', filename)
    
    # Limit length (optional, adjust as needed)
    max_length = 100
    if len(filename) > max_length:
        filename = filename[:max_length]
        
    # Ensure it doesn't end with a dash or underscore
    filename = filename.rstrip('-_')
    
    # If empty after sanitization, return a default name
    if not filename:
        filename = 'video'
        
    return filename