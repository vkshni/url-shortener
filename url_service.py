"""
URL Shortener Service Layer

Handles business logic for URL shortening, resolution, and validation.
Orchestrates interactions between storage and code generation components.
"""

from short_code_gen import generate, is_valid_code
from storage import URLDB
from url_entity import URL

# Maximum number of retries when short code collision occurs
MAX_COLLISION_RETRIES = 10


class URLService:
    """
    URL Shortener Service
    
    Provides core functionality for shortening URLs, resolving short codes,
    and managing URL data with validation and collision handling.
    """

    def __init__(self, db: URLDB = None):
        """
        Initialize URL service with optional database instance.
        
        Args:
            db: Database instance. Creates new URLDB if None.
        """
        self.db = db if db else URLDB()
    
    def shorten(self, long_url: str) -> str:
        """
        Create a short code for a long URL.
        
        Validates URL, checks for existing short code, and generates new code
        if needed. Handles collision detection with retry mechanism.
        
        Args:
            long_url: The URL to shorten
            
        Returns:
            str: 6-character short code
            
        Raises:
            ValueError: If URL validation fails or collision retry limit exceeded
        """
        # Validate URL format
        self.validate_url(long_url)

        # Return existing code if URL already shortened
        existing = self.db.find_by_url(long_url)
        if existing:
            return existing.short_code
        
        # Generate unique short code with collision handling
        for attempt in range(MAX_COLLISION_RETRIES):
            short_code = generate()

            # Check for collision
            if not self.db.find_by_code(short_code):
                url = URL(long_url, short_code)
                self.db.add(url)
                return short_code
        
        # Failed to generate unique code after max retries
        raise ValueError(f"Failed to generate a unique code after {MAX_COLLISION_RETRIES} attempts")

    def resolve(self, short_code: str) -> str:
        """
        Resolve a short code to its original URL and increment visit counter.
        
        Args:
            short_code: The 6-character code to resolve
            
        Returns:
            str: Original long URL
            
        Raises:
            ValueError: If code format invalid or code not found
        """
        # Validate short code format
        if not is_valid_code(short_code):
            raise ValueError("Short code should be exactly 6 alphanumeric characters")

        # Find URL by short code
        url = self.db.find_by_code(short_code)
        if not url:
            raise ValueError(f"Short code '{short_code}' not found")
        
        # Increment visit counter and persist
        url.visit_count += 1
        self.db.update(url)
        
        return url.long_url
    
    def list_all(self) -> list[URL]:
        """
        Retrieve all shortened URLs from database.
        
        Returns:
            list[URL]: List of all URL entities
        """
        return self.db.list_all()
    
    def get_stats(self, short_code: str) -> dict:
        """
        Get statistics for a specific short code.
        
        Args:
            short_code: The code to get stats for
            
        Returns:
            dict: URL data including visits, creation date, etc.
            
        Raises:
            ValueError: If short code not found
        """
        url = self.db.find_by_code(short_code)
        if not url:
            raise ValueError(f"Short code '{short_code}' not found")

        return url.to_dict()

    def validate_url(self, long_url: str):
        """
        Validate URL format and constraints.
        
        Args:
            long_url: URL to validate
            
        Raises:
            ValueError: If URL fails any validation check
        """
        # Check for empty or whitespace-only URL
        if not long_url or not long_url.strip():
            raise ValueError("URL cannot be empty")
        
        # Check maximum length
        if len(long_url) > 2000:
            raise ValueError("URL too long (max 2000 characters)")
        
        # Check minimum length
        if len(long_url) < 1:
            raise ValueError("URL cannot be empty")
        
        # Validate protocol
        if not (long_url.startswith("http://") or long_url.startswith("https://")):
            raise ValueError("URL must start with 'http://' or 'https://'")
        
        # Validate domain presence (must have at least one dot)
        if "." not in long_url:
            raise ValueError("Invalid URL format - missing domain")