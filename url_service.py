from short_code_gen import generate, is_valid_code
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

    def resolve(self, short_code: str) -> str:

        if not is_valid_code(short_code):
            raise ValueError(f"Short code should be exactly 6 alphanumeric characters")

        url = self.db.find_by_code(short_code)

        if not url:
            raise ValueError(f"Short code '{short_code}' not found")
        
        url.visit_count += 1
        self.db.update(url)
        return url.long_url
    
    def list_all(self) -> list[URL]:

        return self.db.list_all()
    
    def get_stats(self, short_code):

        url = self.db.find_by_code(short_code)
        if not url:
            raise ValueError(f"Short code '{short_code}' not found")

        return url.to_dict()
        

