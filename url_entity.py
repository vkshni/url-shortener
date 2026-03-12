from uuid import uuid4
from datetime import datetime

DATE_FORMAT = "%d-%m-%YT%H:%M:%S"

# URL Entity


class URL:

    def __init__(
        self,
        long_url: str,
        short_code: str,
        created_at: str = None,
        visit_count: int = None,
        url_id: str = None,
    ):
        self.url_id = str(url_id) if url_id else str(uuid4())
        self.long_url = long_url
        self.short_code = short_code
        self.created_at = (
            datetime.strptime(created_at, DATE_FORMAT) if created_at else datetime.now()
        )

        self.visit_count = visit_count if visit_count else 0

        self.validate()

    def to_dict(self):

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
    def from_dict(cls, url_dict):

        return cls(
            long_url=url_dict["long_url"],
            short_code=url_dict["short_code"],
            created_at=url_dict["created_at"],
            visit_count=url_dict["visit_count"],
            url_id=url_dict["url_id"],
        )

    def validate(self):
        
        if not self.long_url:
            raise ValueError("URL cannot be empty")
        
        if not (1 <= len(self.long_url) <= 2000) :
            raise ValueError(f"URL too long (max 2000 characters)")
        
        if  not (self.long_url.startswith("http://") or self.long_url.startswith("https://")):
            raise ValueError(f"URL must start with 'http://' or 'https://'")
        
        if "." not in self.long_url:
            raise ValueError(f"Invalid URL format - missing domain")
