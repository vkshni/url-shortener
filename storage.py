"""
Storage Manager

Handles data persistence using JSON file storage with in-memory caching
for improved performance.
"""

from pathlib import Path
import json

from url_entity import URL

# Base directory for file operations
BASE_DIR = Path(__file__).parent


class JSONFile:
    """
    Low-level JSON file handler.
    
    Manages reading and writing JSON data to disk with automatic
    file creation and formatting.
    """

    def __init__(self, file_name: str):
        """
        Initialize JSON file handler.
        
        Args:
            file_name: Name of the JSON file to manage
        """
        self.file_path = self.create(file_name)

    def create(self, file_name: str) -> Path:
        """
        Create JSON file if it doesn't exist.
        
        Args:
            file_name: Name of file to create
            
        Returns:
            Path: Full path to the file
        """
        path = BASE_DIR / file_name
        
        # Initialize empty JSON array if file doesn't exist
        if not path.exists():
            with open(path, "w") as f:
                json.dump([], f, indent=4)
        
        return path

    def read_all(self) -> list:
        """
        Read all data from JSON file.
        
        Returns:
            list: Parsed JSON data
        """
        with open(self.file_path, "r") as f:
            data = json.load(f)
            return data

    def write_all(self, data: list):
        """
        Write data to JSON file.
        
        Args:
            data: List of dictionaries to write
        """
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)


class URLDB:
    """
    URL Database Manager
    
    Provides CRUD operations for URL records with in-memory caching
    for performance optimization.
    """

    def __init__(self, url_file: str = "urls.json"):
        """
        Initialize database with JSON file backend.
        
        Args:
            url_file: Name of JSON file for storage (default: urls.json)
        """
        self.json_handler = JSONFile(url_file)
        self._cache = None  # In-memory cache for faster operations
        self._load_cache()

    def _load_cache(self):
        """Load data from file into memory cache (called on init)."""
        if self._cache is None:
            self._cache = self.json_handler.read_all()

    def _save_cache(self):
        """Persist in-memory cache to disk."""
        self.json_handler.write_all(self._cache)

    def add(self, url: URL):
        """
        Add new URL to database.
        
        Args:
            url: URL entity to add
        """
        url_dict = url.to_dict()
        self._cache.append(url_dict)
        self._save_cache()

    def find_by_url(self, long_url: str) -> URL:
        """
        Find URL by long URL string.
        
        Args:
            long_url: Original long URL to search for
            
        Returns:
            URL: URL entity if found, None otherwise
        """
        url_obj = None
        for url_dict in self._cache:
            if url_dict["long_url"] == long_url:
                url_obj = URL.from_dict(url_dict)
                break

        return url_obj

    def find_by_code(self, short_code: str) -> URL:
        """
        Find URL by short code.
        
        Args:
            short_code: 6-character short code to search for
            
        Returns:
            URL: URL entity if found, None otherwise
        """
        url_obj = None
        for url_dict in self._cache:
            if url_dict["short_code"] == short_code:
                url_obj = URL.from_dict(url_dict)
                break

        return url_obj

    def list_all(self) -> list[URL]:
        """
        Get all URLs from database.
        
        Returns:
            list[URL]: List of all URL entities
        """
        data = [URL.from_dict(url_dict) for url_dict in self._cache]
        return data

    def update(self, url: URL) -> bool:
        """
        Update existing URL in database.
        
        Args:
            url: URL entity with updated data
            
        Returns:
            bool: True if updated, False if not found
        """
        updated = False
        
        # Find and update by url_id
        for i, url_dict in enumerate(self._cache):
            if url_dict["url_id"] == url.url_id:
                self._cache[i] = url.to_dict()
                updated = True
                break

        # Persist changes if update succeeded
        if updated:
            self._save_cache()

        return updated