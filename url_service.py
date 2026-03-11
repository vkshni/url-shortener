from short_code_gen import generate
from storage import URLDB
from url_entity import URL

MAX_COLLISION_RETRIES = 10

# URL Services

class URLService:

    def __init__(self, db: URLDB = None):
        self.db = db if db else URLDB()
    
    def shorten(self, long_url: str) -> str:

        existing = self.db.find_by_url(long_url)
        if existing:
            return existing.short_code
        
        for attempt in range(MAX_COLLISION_RETRIES):
            short_code = generate()

            if not self.db.find_by_code(short_code):
                url = URL(
                    long_url,
                    short_code
                )
                self.db.add(url)
                return short_code
        
        raise ValueError(f"Failed to generate a unique code after {MAX_COLLISION_RETRIES} attempts")

