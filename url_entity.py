"""
URL Entity Model

Defines the data structure for URL records with serialization support.
"""

from uuid import uuid4
from datetime import datetime

# Date format for consistent timestamp serialization
DATE_FORMAT = "%d-%m-%YT%H:%M:%S"


class URL:
    """
    URL Entity
    
    Represents a shortened URL with metadata including visit tracking,
    timestamps, and unique identification.
    """

    def __init__(
        self,
        long_url: str,
        short_code: str,
        created_at: str = None,
        visit_count: int = None,
        url_id: str = None,
    ):
        """
        Initialize URL entity.
        
        Args:
            long_url: Original long URL
            short_code: Generated 6-character short code
            created_at: Creation timestamp string (auto-generated if None)
            visit_count: Number of times resolved (defaults to 0)
            url_id: Unique identifier (auto-generated UUID if None)
        """
        # Generate or use provided UUID
        self.url_id = str(url_id) if url_id else str(uuid4())
        
        self.long_url = long_url
        self.short_code = short_code
        
        # Parse timestamp or use current time
        self.created_at = (
            datetime.strptime(created_at, DATE_FORMAT) if created_at else datetime.now()
        )
        
        # Initialize visit counter
        self.visit_count = visit_count if visit_count else 0

    def to_dict(self) -> dict:
        """
        Convert URL entity to dictionary for JSON serialization.
        
        Returns:
            dict: URL data with all fields as serializable types
        """
        return {
            "url_id": self.url_id,
            "long_url": self.long_url,
            "short_code": self.short_code,
            "created_at": (
                self.created_at.strftime(DATE_FORMAT) if self.created_at else None
            ),
            "visit_count": self.visit_count,
        }

    @classmethod
    def from_dict(cls, url_dict: dict) -> 'URL':
        """
        Create URL entity from dictionary (deserialization).
        
        Args:
            url_dict: Dictionary containing URL data
            
        Returns:
            URL: New URL entity instance
        """
        return cls(
            long_url=url_dict["long_url"],
            short_code=url_dict["short_code"],
            created_at=url_dict["created_at"],
            visit_count=url_dict["visit_count"],
            url_id=url_dict["url_id"],
        )